from django.test import TestCase
from datetime import date, timedelta
from orbit.models import Person, Conversation, ContactAttempt, Relationship


class PersonModelTest(TestCase):
    def setUp(self):
        self.person = Person.objects.create(
            name="Test Person",
            name_ext="test context",
            email="test@example.com",
            phone="555-1234",
            birthday=date(1990, 1, 15),
            how_we_met="Through testing",
            notes="This is a test person"
        )

    def test_person_creation(self):
        self.assertEqual(self.person.name, "Test Person")
        self.assertEqual(self.person.name_ext, "test context")
        self.assertEqual(self.person.email, "test@example.com")
        self.assertEqual(self.person.phone, "555-1234")
        self.assertEqual(self.person.birthday, date(1990, 1, 15))
        self.assertTrue(self.person.created_at)

    def test_person_str_with_name_ext(self):
        expected = "Test Person (test context)"
        self.assertEqual(str(self.person), expected)

    def test_person_str_without_name_ext(self):
        person = Person.objects.create(name="Simple Name")
        self.assertEqual(str(person), "Simple Name")

    def test_person_last_contacted_no_conversations(self):
        self.assertIsNone(self.person.last_contacted)

    def test_person_last_contacted_with_conversations(self):
        # Create a conversation
        conversation = Conversation.objects.create(
            date=date.today() - timedelta(days=5),
            type="phone",
            notes="Test conversation"
        )
        conversation.participants.add(self.person)
        
        self.assertEqual(self.person.last_contacted, date.today() - timedelta(days=5))

    def test_person_blank_fields(self):
        person = Person.objects.create(name="Minimal Person")
        self.assertEqual(person.name_ext, "")
        self.assertEqual(person.email, "")
        self.assertEqual(person.phone, "")
        self.assertEqual(person.how_we_met, "")
        self.assertEqual(person.notes, "")
        self.assertEqual(person.ai_summary, "")
        self.assertIsNone(person.birthday)


class ConversationModelTest(TestCase):
    def setUp(self):
        self.person1 = Person.objects.create(name="Alice")
        self.person2 = Person.objects.create(name="Bob")
        self.conversation = Conversation.objects.create(
            date=date.today(),
            type="in_person",
            location="Coffee shop",
            notes="Great chat about life"
        )
        self.conversation.participants.add(self.person1, self.person2)

    def test_conversation_creation(self):
        self.assertEqual(self.conversation.date, date.today())
        self.assertEqual(self.conversation.type, "in_person")
        self.assertEqual(self.conversation.location, "Coffee shop")
        self.assertEqual(self.conversation.notes, "Great chat about life")
        self.assertTrue(self.conversation.created_at)

    def test_conversation_participants(self):
        participants = list(self.conversation.participants.all())
        self.assertIn(self.person1, participants)
        self.assertIn(self.person2, participants)
        self.assertEqual(len(participants), 2)

    def test_conversation_str(self):
        str_repr = str(self.conversation)
        self.assertTrue(str_repr.startswith(str(date.today())))
        self.assertIn('Alice', str_repr)
        self.assertIn('Bob', str_repr)

    def test_conversation_ordering(self):
        # Create older conversation
        older_conv = Conversation.objects.create(
            date=date.today() - timedelta(days=1),
            type="phone",
            notes="Older conversation"
        )
        
        conversations = list(Conversation.objects.all())
        self.assertEqual(conversations[0], self.conversation)  # Newer first
        self.assertEqual(conversations[1], older_conv)

    def test_conversation_type_choices(self):
        valid_types = ['in_person', 'phone', 'text', 'email', 'video', 'other']
        for conv_type in valid_types:
            conv = Conversation.objects.create(
                date=date.today(),
                type=conv_type,
                notes=f"Test {conv_type}"
            )
            self.assertEqual(conv.type, conv_type)


class ContactAttemptModelTest(TestCase):
    def setUp(self):
        self.person = Person.objects.create(name="Test Person")
        self.conversation = Conversation.objects.create(
            date=date.today(),
            type="phone",
            notes="Follow-up call"
        )
        self.contact_attempt = ContactAttempt.objects.create(
            person=self.person,
            date=date.today() - timedelta(days=1),
            type="text",
            notes="Sent a quick hello",
            led_to_conversation=self.conversation
        )

    def test_contact_attempt_creation(self):
        self.assertEqual(self.contact_attempt.person, self.person)
        self.assertEqual(self.contact_attempt.date, date.today() - timedelta(days=1))
        self.assertEqual(self.contact_attempt.type, "text")
        self.assertEqual(self.contact_attempt.notes, "Sent a quick hello")
        self.assertEqual(self.contact_attempt.led_to_conversation, self.conversation)
        self.assertTrue(self.contact_attempt.created_at)

    def test_contact_attempt_str(self):
        expected = f"{date.today() - timedelta(days=1)} - text to Test Person"
        self.assertEqual(str(self.contact_attempt), expected)

    def test_contact_attempt_without_conversation(self):
        attempt = ContactAttempt.objects.create(
            person=self.person,
            date=date.today(),
            type="email",
            notes="No response"
        )
        self.assertIsNone(attempt.led_to_conversation)

    def test_contact_attempt_ordering(self):
        # Create newer attempt
        newer_attempt = ContactAttempt.objects.create(
            person=self.person,
            date=date.today(),
            type="call"
        )
        
        attempts = list(ContactAttempt.objects.all())
        self.assertEqual(attempts[0], newer_attempt)  # Newer first
        self.assertEqual(attempts[1], self.contact_attempt)


class RelationshipModelTest(TestCase):
    def setUp(self):
        self.person1 = Person.objects.create(name="Alice")
        self.person2 = Person.objects.create(name="Bob")
        self.relationship = Relationship.objects.create(
            person1=self.person1,
            person2=self.person2,
            relationship_type="friend",
            description="College roommates"
        )

    def test_relationship_creation(self):
        self.assertEqual(self.relationship.person1, self.person1)
        self.assertEqual(self.relationship.person2, self.person2)
        self.assertEqual(self.relationship.relationship_type, "friend")
        self.assertEqual(self.relationship.description, "College roommates")
        self.assertTrue(self.relationship.created_at)

    def test_relationship_str(self):
        expected = "Alice - Bob (friend)"
        self.assertEqual(str(self.relationship), expected)

    def test_relationship_unique_constraint(self):
        # Try to create duplicate relationship
        with self.assertRaises(Exception):  # Will be IntegrityError
            Relationship.objects.create(
                person1=self.person1,
                person2=self.person2,
                relationship_type="colleague"
            )

    def test_relationship_type_choices(self):
        valid_types = ['partner', 'family', 'friend', 'colleague', 'acquaintance', 'other']
        person3 = Person.objects.create(name="Charlie")
        
        for rel_type in valid_types:
            person_temp = Person.objects.create(name=f"Person_{rel_type}")
            rel = Relationship.objects.create(
                person1=person3,
                person2=person_temp,
                relationship_type=rel_type
            )
            self.assertEqual(rel.relationship_type, rel_type)