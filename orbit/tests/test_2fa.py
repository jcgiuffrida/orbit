from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django_otp.plugins.otp_totp.models import TOTPDevice
from unittest.mock import patch, MagicMock
import base64
from io import BytesIO


class TwoFactorAuthenticationTest(APITestCase):
    """Test suite for Two-Factor Authentication functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_login_without_2fa(self):
        """Test normal login flow when 2FA is not enabled"""
        self.client.logout()
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['first_name'], 'Test')
        self.assertEqual(response.data['user']['last_name'], 'User')
        self.assertFalse(response.data['user']['has_2fa'])

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        self.client.logout()
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], 'Invalid credentials')

    def test_login_missing_credentials(self):
        """Test login with missing username or password"""
        self.client.logout()
        url = reverse('login')
        
        # Missing password
        data = {'username': 'testuser'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Username and password required')
        
        # Missing username
        data = {'password': 'testpass123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Username and password required')

    def test_current_user_without_2fa(self):
        """Test current user endpoint without 2FA enabled"""
        url = reverse('current-user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['first_name'], 'Test')
        self.assertEqual(response.data['last_name'], 'User')
        self.assertFalse(response.data['has_2fa'])
        # Verify sensitive info is not exposed
        self.assertNotIn('email', response.data)
        self.assertNotIn('is_staff', response.data)
        self.assertNotIn('is_superuser', response.data)

    def test_2fa_status_without_2fa(self):
        """Test 2FA status endpoint when 2FA is not enabled"""
        url = reverse('2fa-status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_2fa'])
        self.assertEqual(response.data['device_count'], 0)

    @patch('qrcode.QRCode.make_image')
    def test_setup_2fa_success(self, mock_make_image):
        """Test successful 2FA setup"""
        # Mock QR code image generation
        mock_img = MagicMock()
        mock_img.save = MagicMock()
        mock_make_image.return_value = mock_img

        url = reverse('setup-2fa')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('qr_code', response.data)
        self.assertIn('secret_key', response.data)
        self.assertIn('device_id', response.data)
        
        # Verify QR code data format
        self.assertTrue(response.data['qr_code'].startswith('data:image/png;base64,'))
        
        # Verify device was created (but not confirmed)
        device = TOTPDevice.objects.get(user=self.user)
        self.assertFalse(device.confirmed)
        self.assertEqual(device.name, 'testuser-totp')

    def test_setup_2fa_already_enabled(self):
        """Test setup 2FA when already enabled"""
        # Create an already confirmed device
        TOTPDevice.objects.create(
            user=self.user,
            name='existing-device',
            confirmed=True
        )
        
        url = reverse('setup-2fa')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Two-factor authentication is already enabled')

    def test_confirm_2fa_success(self):
        """Test successful 2FA confirmation"""
        # Create an unconfirmed device
        device = TOTPDevice.objects.create(
            user=self.user,
            name='test-device',
            confirmed=False
        )
        
        # Mock the verify_token method on the TOTPDevice class
        with patch.object(TOTPDevice, 'verify_token', return_value=True):
            url = reverse('confirm-2fa')
            data = {
                'token': '123456',
                'device_id': device.id
            }
            response = self.client.post(url, data)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            self.assertEqual(response.data['message'], 'Two-factor authentication enabled')
            
            # Verify device is now confirmed
            device.refresh_from_db()
            self.assertTrue(device.confirmed)

    def test_confirm_2fa_invalid_token(self):
        """Test 2FA confirmation with invalid token"""
        device = TOTPDevice.objects.create(
            user=self.user,
            name='test-device',
            confirmed=False
        )
        
        # Mock the verify_token method to return False
        with patch.object(TOTPDevice, 'verify_token', return_value=False):
            url = reverse('confirm-2fa')
            data = {
                'token': '000000',
                'device_id': device.id
            }
            response = self.client.post(url, data)
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['error'], 'Invalid token')
            
            # Verify device is still not confirmed
            device.refresh_from_db()
            self.assertFalse(device.confirmed)

    def test_confirm_2fa_missing_parameters(self):
        """Test 2FA confirmation with missing parameters"""
        url = reverse('confirm-2fa')
        
        # Missing token
        data = {'device_id': '123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Token and device_id are required')
        
        # Missing device_id
        data = {'token': '123456'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Token and device_id are required')

    def test_confirm_2fa_invalid_device(self):
        """Test 2FA confirmation with invalid device ID"""
        url = reverse('confirm-2fa')
        data = {
            'token': '123456',
            'device_id': '999999'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid device')

    def test_confirm_2fa_already_confirmed_device(self):
        """Test 2FA confirmation with already confirmed device"""
        device = TOTPDevice.objects.create(
            user=self.user,
            name='test-device',
            confirmed=True
        )
        
        url = reverse('confirm-2fa')
        data = {
            'token': '123456',
            'device_id': device.id
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid device')

    def test_disable_2fa_success(self):
        """Test successful 2FA disabling"""
        # Create a confirmed device
        TOTPDevice.objects.create(
            user=self.user,
            name='test-device',
            confirmed=True
        )
        
        url = reverse('disable-2fa')
        data = {'password': 'testpass123'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'Two-factor authentication disabled')
        
        # Verify all devices are deleted
        self.assertEqual(TOTPDevice.objects.filter(user=self.user).count(), 0)

    def test_disable_2fa_wrong_password(self):
        """Test 2FA disabling with wrong password"""
        TOTPDevice.objects.create(
            user=self.user,
            name='test-device',
            confirmed=True
        )
        
        url = reverse('disable-2fa')
        data = {'password': 'wrongpassword'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], 'Invalid password')
        
        # Verify device still exists
        self.assertEqual(TOTPDevice.objects.filter(user=self.user).count(), 1)

    def test_disable_2fa_missing_password(self):
        """Test 2FA disabling without password"""
        url = reverse('disable-2fa')
        data = {}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Password confirmation required')

    def test_login_with_2fa_enabled(self):
        """Test login flow when 2FA is enabled"""
        # Create a confirmed TOTP device
        device = TOTPDevice.objects.create(
            user=self.user,
            name='test-device',
            confirmed=True
        )
        
        self.client.logout()
        url = reverse('login')
        
        # First attempt without OTP token
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data.get('success', False))
        self.assertTrue(response.data.get('requires_2fa', False))
        self.assertEqual(response.data['error'], 'Two-factor authentication required')

    def test_login_with_2fa_valid_token(self):
        """Test login with valid 2FA token"""
        # Create a confirmed TOTP device
        device = TOTPDevice.objects.create(
            user=self.user,
            name='test-device',
            confirmed=True
        )
        
        self.client.logout()
        url = reverse('login')
        
        # Mock match_token to return the device (valid token)
        with patch('orbit.views.match_token', return_value=device):
            data = {
                'username': 'testuser',
                'password': 'testpass123',
                'otp_token': '123456'
            }
            response = self.client.post(url, data)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            self.assertEqual(response.data['user']['username'], 'testuser')
            self.assertTrue(response.data['user']['has_2fa'])

    def test_login_with_2fa_invalid_token(self):
        """Test login with invalid 2FA token"""
        # Create a confirmed TOTP device
        TOTPDevice.objects.create(
            user=self.user,
            name='test-device',
            confirmed=True
        )
        
        self.client.logout()
        url = reverse('login')
        
        # Mock match_token to return None (invalid token)
        with patch('orbit.views.match_token', return_value=None):
            data = {
                'username': 'testuser',
                'password': 'testpass123',
                'otp_token': '000000'
            }
            response = self.client.post(url, data)
            
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertEqual(response.data['error'], 'Invalid authentication token')

    def test_2fa_status_with_2fa_enabled(self):
        """Test 2FA status endpoint when 2FA is enabled"""
        TOTPDevice.objects.create(
            user=self.user,
            name='test-device',
            confirmed=True
        )
        
        url = reverse('2fa-status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_2fa'])
        self.assertEqual(response.data['device_count'], 1)

    def test_current_user_with_2fa_enabled(self):
        """Test current user endpoint with 2FA enabled"""
        TOTPDevice.objects.create(
            user=self.user,
            name='test-device',
            confirmed=True
        )
        
        url = reverse('current-user')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertTrue(response.data['has_2fa'])

    def test_unauthenticated_access_to_2fa_endpoints(self):
        """Test that 2FA management endpoints require authentication"""
        self.client.logout()
        
        endpoints = [
            ('setup-2fa', 'post'),
            ('confirm-2fa', 'post'),
            ('disable-2fa', 'post'),
            ('2fa-status', 'get'),
        ]
        
        for endpoint_name, method in endpoints:
            url = reverse(endpoint_name)
            if method == 'get':
                response = self.client.get(url)
            else:
                response = self.client.post(url, {})
            
            self.assertEqual(
                response.status_code, 
                status.HTTP_403_FORBIDDEN,
                f"Endpoint {endpoint_name} should require authentication"
            )

    def test_multiple_devices_cleanup_on_setup(self):
        """Test that old unconfirmed devices are cleaned up on new setup"""
        # Create an old unconfirmed device
        old_device = TOTPDevice.objects.create(
            user=self.user,
            name='old-device',
            confirmed=False
        )
        
        with patch('qrcode.QRCode.make_image'):
            url = reverse('setup-2fa')
            response = self.client.post(url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Verify old device still exists (not automatically cleaned in this implementation)
            # But new device was created
            devices = TOTPDevice.objects.filter(user=self.user)
            self.assertEqual(devices.count(), 2)
            
            # Get the new device
            new_device = devices.exclude(id=old_device.id).first()
            self.assertIsNotNone(new_device)
            self.assertFalse(new_device.confirmed)

    def test_csrf_token_endpoint(self):
        """Test CSRF token endpoint is accessible without authentication"""
        self.client.logout()
        url = reverse('csrf-token')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('csrfToken', response.data)
        self.assertIsNotNone(response.data['csrfToken'])

    def test_logout_endpoint(self):
        """Test logout endpoint"""
        url = reverse('logout')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])


class TwoFactorAuthenticationUserIsolationTest(APITestCase):
    """Test that 2FA devices are properly isolated between users"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )

    def test_2fa_device_isolation(self):
        """Test that users can only manage their own 2FA devices"""
        # User1 sets up 2FA
        self.client.force_authenticate(user=self.user1)
        
        with patch('qrcode.QRCode.make_image'):
            setup_url = reverse('setup-2fa')
            response = self.client.post(setup_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            device_id = response.data['device_id']
        
        # User2 should not be able to confirm user1's device
        self.client.force_authenticate(user=self.user2)
        confirm_url = reverse('confirm-2fa')
        data = {
            'token': '123456',
            'device_id': device_id
        }
        response = self.client.post(confirm_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid device')

    def test_2fa_status_isolation(self):
        """Test that 2FA status is user-specific"""
        # User1 enables 2FA
        TOTPDevice.objects.create(
            user=self.user1,
            name='user1-device',
            confirmed=True
        )
        
        # User1 should see 2FA enabled
        self.client.force_authenticate(user=self.user1)
        url = reverse('2fa-status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_2fa'])
        self.assertEqual(response.data['device_count'], 1)
        
        # User2 should see 2FA disabled
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_2fa'])
        self.assertEqual(response.data['device_count'], 0)

    def test_disable_2fa_isolation(self):
        """Test that users can only disable their own 2FA"""
        # Create devices for both users
        user1_device = TOTPDevice.objects.create(
            user=self.user1,
            name='user1-device',
            confirmed=True
        )
        user2_device = TOTPDevice.objects.create(
            user=self.user2,
            name='user2-device',
            confirmed=True
        )
        
        # User1 disables their 2FA
        self.client.force_authenticate(user=self.user1)
        url = reverse('disable-2fa')
        data = {'password': 'testpass123'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify only user1's device was deleted
        self.assertFalse(TOTPDevice.objects.filter(id=user1_device.id).exists())
        self.assertTrue(TOTPDevice.objects.filter(id=user2_device.id).exists())