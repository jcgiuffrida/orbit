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
            birthday_month=1,
            birthday_day=15,
            birth_year=1990,
            how_we_met="Through testing",
            notes="This is a test person"
        )

    def test_person_creation(self):
        self.assertEqual(self.person.name, "Test Person")
        self.assertEqual(self.person.name_ext, "test context")
        self.assertEqual(self.person.email, "test@example.com")
        self.assertEqual(self.person.phone, "555-1234")
        self.assertEqual(self.person.birthday_month, 1)
        self.assertEqual(self.person.birthday_day, 15)
        self.assertEqual(self.person.birth_year, 1990)
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
        self.assertIsNone(person.birthday_month)
        self.assertIsNone(person.birthday_day)
        self.assertIsNone(person.birth_year)
        self.assertIsNone(person.birthday)

    def test_birthday_without_year(self):
        """Test birthday with month and day but no year"""
        person = Person.objects.create(
            name="Jane Doe",
            birthday_month=3,
            birthday_day=22
        )
        self.assertEqual(person.birthday_month, 3)
        self.assertEqual(person.birthday_day, 22)
        self.assertIsNone(person.birth_year)
        # birthday property should use current year
        self.assertIsNotNone(person.birthday)
        self.assertEqual(person.birthday.month, 3)
        self.assertEqual(person.birthday.day, 22)
        # birthday_display should not show year
        self.assertEqual(person.birthday_display, "March 22")
        # age should be None when year is unknown
        self.assertIsNone(person.age)

    def test_birthday_display_with_year(self):
        """Test birthday display includes year when known"""
        person = Person.objects.create(
            name="John Doe",
            birthday_month=7,
            birthday_day=4,
            birth_year=1985
        )
        self.assertEqual(person.birthday_display, "July 4, 1985")
        self.assertIsNotNone(person.age)

    def test_invalid_birthday_handling(self):
        """Test handling of invalid dates like Feb 29 on non-leap years"""
        person = Person.objects.create(
            name="Leap Year Baby",
            birthday_month=2,
            birthday_day=29,
            birth_year=2021  # 2021 is not a leap year
        )
        # The birthday property should handle this gracefully
        self.assertIsNone(person.birthday)  # Invalid date returns None

    def test_upcoming_birthdays_logic(self):
        """Test the upcoming birthdays helper function"""
        from datetime import date, timedelta
        from orbit.views import get_upcoming_birthdays
        
        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        
        # Create people with birthdays
        person_today = Person.objects.create(
            name="Birthday Today",
            birthday_month=today.month,
            birthday_day=today.day,
            birth_year=1990
        )
        
        person_tomorrow = Person.objects.create(
            name="Birthday Tomorrow", 
            birthday_month=tomorrow.month,
            birthday_day=tomorrow.day,
            birth_year=1985
        )
        
        person_next_week = Person.objects.create(
            name="Birthday Next Week",
            birthday_month=next_week.month,
            birthday_day=next_week.day
        )
        
        # Test upcoming birthdays in next 10 days
        upcoming = get_upcoming_birthdays(days_ahead=10)
        
        # Should find all three people
        self.assertEqual(len(upcoming), 3)
        
        # Check they're sorted by days_until
        self.assertEqual(upcoming[0]['days_until'], 0)  # Today
        self.assertEqual(upcoming[1]['days_until'], 1)  # Tomorrow
        self.assertEqual(upcoming[2]['days_until'], 7)  # Next week
        
        # Check is_today flag
        self.assertTrue(upcoming[0]['is_today'])
        self.assertFalse(upcoming[1]['is_today'])
        self.assertFalse(upcoming[2]['is_today'])


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
            led_to_conversation=True
        )

    def test_contact_attempt_creation(self):
        self.assertEqual(self.contact_attempt.person, self.person)
        self.assertEqual(self.contact_attempt.date, date.today() - timedelta(days=1))
        self.assertEqual(self.contact_attempt.type, "text")
        self.assertEqual(self.contact_attempt.notes, "Sent a quick hello")
        self.assertEqual(self.contact_attempt.led_to_conversation, True)
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
        self.assertEqual(attempt.led_to_conversation, False)

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