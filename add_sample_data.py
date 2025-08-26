#!/usr/bin/env python
import os
import sys
import django
from datetime import date, timedelta

from orbit.models import Person, Conversation, ContactAttempt, Relationship

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orbit.settings')
sys.path.append('/Users/jonathangiuffrida/.virtualenvs/orbitenv/orbit')
django.setup()


# Check if data already exists
if Person.objects.exists():
    print("WARNING: Database already contains people. Exiting to avoid duplicates.")
    sys.exit(1)

# Add People
maya = Person.objects.create(
    name="Maya Patel",
    name_ext="from coding bootcamp",
    email="maya.patel@email.com",
    phone="555-2847",
    birthday=date(1993, 6, 12),
    how_we_met="Met during a coding bootcamp in 2019",
    notes="Full-stack developer, loves rock climbing and board games"
)

finn = Person.objects.create(
    name="Finn O'Connor",
    email="finn.oconnor@email.com",
    birthday=date(1988, 9, 4),
    how_we_met="Neighbor across the street",
    notes="Freelance graphic designer, has a golden retriever named Buster"
)

elena = Person.objects.create(
    name="Elena Rodriguez",
    name_ext="mystery book enthusiast",
    phone="555-9634",
    how_we_met="Book club at Riverside Library",
    notes="Retired high school Spanish teacher, incredible baker"
)

jasper = Person.objects.create(
    name="Jasper Kim",
    email="j.kim@company.com",
    phone="555-7521",
    birthday=date(1991, 2, 28),
    how_we_met="Started same day at current job",
    notes="Product manager, marathon runner, great at karaoke"
)

# Add Conversations
conv1 = Conversation.objects.create(
    date=date.today() - timedelta(days=7),
    type="phone",
    location="",
    notes="Caught up about work and upcoming vacation plans. Maya mentioned she's planning a rock climbing trip to Joshua Tree."
)
conv1.participants.add(maya)

conv2 = Conversation.objects.create(
    date=date.today() - timedelta(days=14),
    type="in_person",
    location="Local coffee shop",
    notes="Had coffee and discussed his latest design projects. Finn showed me photos of Buster at the dog park."
)
conv2.participants.add(finn)

conv3 = Conversation.objects.create(
    date=date.today() - timedelta(days=21),
    type="in_person",
    location="Riverside Library meeting room",
    notes="Book club discussion about 'The Thursday Murder Club'. Elena brought homemade churros for everyone."
)
conv3.participants.add(elena)

# Group conversation
conv4 = Conversation.objects.create(
    date=date.today() - timedelta(days=30),
    type="in_person",
    location="Office conference room",
    notes="Team meeting about Q4 product roadmap. Jasper presented the user research findings and new feature priorities."
)
conv4.participants.add(jasper, maya)

# Add Contact Attempts
ContactAttempt.objects.create(
    person=maya,
    date=date.today() - timedelta(days=8),
    type="text",
    notes="Sent a text asking about her rock climbing plans",
    led_to_conversation=conv1
)

ContactAttempt.objects.create(
    person=finn,
    date=date.today() - timedelta(days=15),
    type="call",
    notes="Called to schedule coffee meetup",
    led_to_conversation=conv2
)

ContactAttempt.objects.create(
    person=elena,
    date=date.today() - timedelta(days=5),
    type="email",
    notes="Emailed about next book club selection"
)

ContactAttempt.objects.create(
    person=jasper,
    date=date.today() - timedelta(days=2),
    type="social",
    notes="Commented on his marathon training post on Instagram"
)

# Add Relationships
Relationship.objects.create(
    person1=maya,
    person2=jasper,
    relationship_type="colleague",
    description="Work together on product development"
)

Relationship.objects.create(
    person1=finn,
    person2=maya,
    relationship_type="friend",
    description="Both live in the same neighborhood"
)

print("Sample data added successfully!")
print(f"Created {Person.objects.count()} people")
print(f"Created {Conversation.objects.count()} conversations") 
print(f"Created {ContactAttempt.objects.count()} contact attempts")
print(f"Created {Relationship.objects.count()} relationships")