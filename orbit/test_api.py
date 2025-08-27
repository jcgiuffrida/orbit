from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta
from .models import Person, Conversation, ContactAttempt, Relationship


class APIAuthenticationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.person = Person.objects.create(name="Test Person")

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
            notes="Great at presentations"
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
            notes='Quick call'
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
        self.person1 = Person.objects.create(name="Alice")
        self.person2 = Person.objects.create(name="Bob")
        self.conversation = Conversation.objects.create(
            date=date.today(),
            type='in_person',
            location='Coffee shop',
            notes='Great chat'
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
        self.person = Person.objects.create(name="Alice")
        self.conversation = Conversation.objects.create(
            date=date.today(),
            type='phone',
            notes='Follow-up call'
        )
        self.contact_attempt = ContactAttempt.objects.create(
            person=self.person,
            date=date.today() - timedelta(days=1),
            type='text',
            notes='Sent hello message',
            led_to_conversation=self.conversation
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
        self.person1 = Person.objects.create(name="Alice")
        self.person2 = Person.objects.create(name="Bob")
        self.relationship = Relationship.objects.create(
            person1=self.person1,
            person2=self.person2,
            relationship_type='friend',
            description='College roommates'
        )

    def test_list_relationships(self):
        url = reverse('relationship-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_relationship(self):
        person3 = Person.objects.create(name="Charlie")
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