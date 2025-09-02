from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta
from orbit.models import Person, Conversation, ContactAttempt, Relationship


class APIAuthenticationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.person = Person.objects.create(name="Test Person", created_by=self.user)

    def test_unauthenticated_access_denied_people(self):
        url = reverse('person-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_access_denied_conversations(self):
        url = reverse('conversation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_access_denied_contact_attempts(self):
        url = reverse('contactattempt-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_access_denied_relationships(self):
        url = reverse('relationship-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_access_allowed(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('person-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PersonAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.person = Person.objects.create(
            name="Alice Smith",
            name_ext="from work",
            email="alice@example.com",
            phone="555-1234",
            birthday=date(1990, 5, 15),
            how_we_met="Work colleague",
            notes="Great at presentations",
            created_by=self.user
        )

    def test_list_people(self):
        url = reverse('person-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_person(self):
        url = reverse('person-list')
        data = {
            'name': 'Bob Johnson',
            'email': 'bob@example.com',
            'phone': '555-5678'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Person.objects.count(), 2)

    def test_retrieve_person(self):
        url = reverse('person-detail', kwargs={'pk': self.person.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Alice Smith')
        self.assertEqual(response.data['name_ext'], 'from work')

    def test_update_person(self):
        url = reverse('person-detail', kwargs={'pk': self.person.pk})
        data = {
            'name': 'Alice Smith-Jones',
            'email': 'alice.jones@example.com'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.person.refresh_from_db()
        self.assertEqual(self.person.name, 'Alice Smith-Jones')

    def test_delete_person(self):
        url = reverse('person-detail', kwargs={'pk': self.person.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Person.objects.count(), 0)

    def test_person_last_contacted_field(self):
        # Create a conversation with this person
        conversation = Conversation.objects.create(
            date=date.today() - timedelta(days=3),
            type='phone',
            notes='Quick call',
            created_by=self.user
        )
        conversation.participants.add(self.person)
        
        url = reverse('person-detail', kwargs={'pk': self.person.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_date = str(date.today() - timedelta(days=3))
        self.assertEqual(response.data['last_contacted'], expected_date)


class ConversationAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.person1 = Person.objects.create(name="Alice", created_by=self.user)
        self.person2 = Person.objects.create(name="Bob", created_by=self.user)
        self.conversation = Conversation.objects.create(
            date=date.today(),
            type='in_person',
            location='Coffee shop',
            notes='Great chat',
            created_by=self.user
        )
        self.conversation.participants.add(self.person1, self.person2)

    def test_list_conversations(self):
        url = reverse('conversation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_conversation(self):
        url = reverse('conversation-list')
        data = {
            'participants': [self.person1.pk],
            'date': str(date.today()),
            'type': 'phone',
            'notes': 'Quick call'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 2)

    def test_conversation_participant_names(self):
        url = reverse('conversation-detail', kwargs={'pk': self.conversation.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Alice', response.data['participant_names'])
        self.assertIn('Bob', response.data['participant_names'])

    def test_update_conversation(self):
        url = reverse('conversation-detail', kwargs={'pk': self.conversation.pk})
        data = {
            'location': 'Restaurant',
            'notes': 'Updated notes'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.location, 'Restaurant')

    def test_delete_conversation(self):
        url = reverse('conversation-detail', kwargs={'pk': self.conversation.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Conversation.objects.count(), 0)


class ContactAttemptAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.person = Person.objects.create(name="Alice", created_by=self.user)
        self.conversation = Conversation.objects.create(
            date=date.today(),
            type='phone',
            notes='Follow-up call',
            created_by=self.user
        )
        self.contact_attempt = ContactAttempt.objects.create(
            person=self.person,
            date=date.today() - timedelta(days=1),
            type='text',
            notes='Sent hello message',
            led_to_conversation=True,
            created_by=self.user
        )

    def test_list_contact_attempts(self):
        url = reverse('contactattempt-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_contact_attempt(self):
        url = reverse('contactattempt-list')
        data = {
            'person': self.person.pk,
            'date': str(date.today()),
            'type': 'email',
            'notes': 'Sent follow-up email'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContactAttempt.objects.count(), 2)

    def test_contact_attempt_person_name(self):
        url = reverse('contactattempt-detail', kwargs={'pk': self.contact_attempt.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['person_name'], 'Alice')

    def test_update_contact_attempt(self):
        url = reverse('contactattempt-detail', kwargs={'pk': self.contact_attempt.pk})
        data = {
            'notes': 'Updated notes'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.contact_attempt.refresh_from_db()
        self.assertEqual(self.contact_attempt.notes, 'Updated notes')

    def test_delete_contact_attempt(self):
        url = reverse('contactattempt-detail', kwargs={'pk': self.contact_attempt.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ContactAttempt.objects.count(), 0)


class RelationshipAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.person1 = Person.objects.create(name="Alice", created_by=self.user)
        self.person2 = Person.objects.create(name="Bob", created_by=self.user)
        self.relationship = Relationship.objects.create(
            person1=self.person1,
            person2=self.person2,
            relationship_type='friend',
            description='College roommates',
            created_by=self.user
        )

    def test_list_relationships(self):
        url = reverse('relationship-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_relationship(self):
        person3 = Person.objects.create(name="Charlie", created_by=self.user)
        url = reverse('relationship-list')
        data = {
            'person1': self.person1.pk,
            'person2': person3.pk,
            'relationship_type': 'colleague',
            'description': 'Work together'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Relationship.objects.count(), 2)

    def test_relationship_person_names(self):
        url = reverse('relationship-detail', kwargs={'pk': self.relationship.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['person1_name'], 'Alice')
        self.assertEqual(response.data['person2_name'], 'Bob')

    def test_update_relationship(self):
        url = reverse('relationship-detail', kwargs={'pk': self.relationship.pk})
        data = {
            'description': 'Best friends from college'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.relationship.refresh_from_db()
        self.assertEqual(self.relationship.description, 'Best friends from college')

    def test_delete_relationship(self):
        url = reverse('relationship-detail', kwargs={'pk': self.relationship.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Relationship.objects.count(), 0)

    def test_relationship_unique_constraint_validation(self):
        url = reverse('relationship-list')
        data = {
            'person1': self.person1.pk,
            'person2': self.person2.pk,
            'relationship_type': 'colleague'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PrivacyFilteringTest(APITestCase):
    def setUp(self):
        # Create two users for testing privacy isolation
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2', 
            password='testpass123'
        )
        
        # Create shared people (visible to all users)
        self.person1 = Person.objects.create(name="Alice", created_by=self.user1)
        self.person2 = Person.objects.create(name="Bob", created_by=self.user2)
        
        # Create public and private conversations
        self.public_conversation = Conversation.objects.create(
            date=date.today(),
            type='phone',
            notes='Public conversation',
            private=False,
            created_by=self.user1
        )
        self.public_conversation.participants.add(self.person1)
        
        self.private_conversation_user1 = Conversation.objects.create(
            date=date.today() - timedelta(days=1),
            type='text',
            notes='Private conversation by user1',
            private=True,
            created_by=self.user1
        )
        self.private_conversation_user1.participants.add(self.person1)
        
        self.private_conversation_user2 = Conversation.objects.create(
            date=date.today() - timedelta(days=2),
            type='email',
            notes='Private conversation by user2',
            private=True,
            created_by=self.user2
        )
        self.private_conversation_user2.participants.add(self.person2)
        
        # Create public and private contact attempts
        self.public_contact_attempt = ContactAttempt.objects.create(
            person=self.person1,
            date=date.today(),
            type='call',
            notes='Public contact attempt',
            private=False,
            created_by=self.user1
        )
        
        self.private_contact_attempt_user1 = ContactAttempt.objects.create(
            person=self.person1,
            date=date.today() - timedelta(days=1),
            type='text',
            notes='Private contact attempt by user1',
            private=True,
            created_by=self.user1
        )
        
        self.private_contact_attempt_user2 = ContactAttempt.objects.create(
            person=self.person2,
            date=date.today() - timedelta(days=2),
            type='email',
            notes='Private contact attempt by user2',
            private=True,
            created_by=self.user2
        )
        
        # Create relationships (shared by all users)
        self.relationship = Relationship.objects.create(
            person1=self.person1,
            person2=self.person2,
            relationship_type='friend',
            created_by=self.user1
        )

    def test_people_shared_across_users(self):
        """People should be visible to all family members"""
        # Test user1 can see all people
        self.client.force_authenticate(user=self.user1)
        url = reverse('person-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Test user2 can see all people
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_relationships_shared_across_users(self):
        """Relationships should be visible to all family members"""
        # Test user1 can see all relationships
        self.client.force_authenticate(user=self.user1)
        url = reverse('relationship-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test user2 can see all relationships
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_conversation_privacy_filtering(self):
        """Users should only see public conversations and their own private ones"""
        # Test user1 sees: public + their own private (2 total)
        self.client.force_authenticate(user=self.user1)
        url = reverse('conversation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Verify user1 sees the right conversations
        conversation_ids = [conv['id'] for conv in response.data['results']]
        self.assertIn(str(self.public_conversation.id), conversation_ids)
        self.assertIn(str(self.private_conversation_user1.id), conversation_ids)
        self.assertNotIn(str(self.private_conversation_user2.id), conversation_ids)
        
        # Test user2 sees: public + their own private (2 total)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Verify user2 sees the right conversations
        conversation_ids = [conv['id'] for conv in response.data['results']]
        self.assertIn(str(self.public_conversation.id), conversation_ids)
        self.assertIn(str(self.private_conversation_user2.id), conversation_ids)
        self.assertNotIn(str(self.private_conversation_user1.id), conversation_ids)

    def test_contact_attempt_privacy_filtering(self):
        """Users should only see public contact attempts and their own private ones"""
        # Test user1 sees: public + their own private (2 total)
        self.client.force_authenticate(user=self.user1)
        url = reverse('contactattempt-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Verify user1 sees the right contact attempts
        attempt_ids = [attempt['id'] for attempt in response.data['results']]
        self.assertIn(str(self.public_contact_attempt.id), attempt_ids)
        self.assertIn(str(self.private_contact_attempt_user1.id), attempt_ids)
        self.assertNotIn(str(self.private_contact_attempt_user2.id), attempt_ids)
        
        # Test user2 sees: public + their own private (2 total)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Verify user2 sees the right contact attempts
        attempt_ids = [attempt['id'] for attempt in response.data['results']]
        self.assertIn(str(self.public_contact_attempt.id), attempt_ids)
        self.assertIn(str(self.private_contact_attempt_user2.id), attempt_ids)
        self.assertNotIn(str(self.private_contact_attempt_user1.id), attempt_ids)

    def test_created_by_field_assignment(self):
        """Test that created_by field is automatically set on creation"""
        self.client.force_authenticate(user=self.user1)
        
        # Test Person creation
        person_url = reverse('person-list')
        person_data = {'name': 'New Person'}
        response = self.client.post(person_url, person_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_person = Person.objects.get(id=response.data['id'])
        self.assertEqual(created_person.created_by, self.user1)
        
        # Test Conversation creation
        conversation_url = reverse('conversation-list')
        conversation_data = {
            'participants': [created_person.pk],
            'date': str(date.today()),
            'type': 'phone',
            'notes': 'Test conversation',
            'private': True
        }
        response = self.client.post(conversation_url, conversation_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_conversation = Conversation.objects.get(id=response.data['id'])
        self.assertEqual(created_conversation.created_by, self.user1)
        self.assertTrue(created_conversation.private)
        
        # Test ContactAttempt creation
        contact_attempt_url = reverse('contactattempt-list')
        contact_attempt_data = {
            'person': created_person.pk,
            'date': str(date.today()),
            'type': 'email',
            'notes': 'Test contact attempt',
            'private': True
        }
        response = self.client.post(contact_attempt_url, contact_attempt_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_attempt = ContactAttempt.objects.get(id=response.data['id'])
        self.assertEqual(created_attempt.created_by, self.user1)
        self.assertTrue(created_attempt.private)
        
        # Test Relationship creation
        person2 = Person.objects.create(name='Another Person', created_by=self.user1)
        relationship_url = reverse('relationship-list')
        relationship_data = {
            'person1': created_person.pk,
            'person2': person2.pk,
            'relationship_type': 'colleague'
        }
        response = self.client.post(relationship_url, relationship_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_relationship = Relationship.objects.get(id=response.data['id'])
        self.assertEqual(created_relationship.created_by, self.user1)

    def test_private_conversation_detail_access(self):
        """Test that users can only access their own private conversations in detail"""
        # User1 should be able to access their private conversation
        self.client.force_authenticate(user=self.user1)
        url = reverse('conversation-detail', kwargs={'pk': self.private_conversation_user1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # User1 should NOT be able to access user2's private conversation
        url = reverse('conversation-detail', kwargs={'pk': self.private_conversation_user2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # But user1 should be able to access public conversations
        url = reverse('conversation-detail', kwargs={'pk': self.public_conversation.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_private_contact_attempt_detail_access(self):
        """Test that users can only access their own private contact attempts in detail"""
        # User2 should be able to access their private contact attempt
        self.client.force_authenticate(user=self.user2)
        url = reverse('contactattempt-detail', kwargs={'pk': self.private_contact_attempt_user2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # User2 should NOT be able to access user1's private contact attempt
        url = reverse('contactattempt-detail', kwargs={'pk': self.private_contact_attempt_user1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # But user2 should be able to access public contact attempts
        url = reverse('contactattempt-detail', kwargs={'pk': self.public_contact_attempt.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)