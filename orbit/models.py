from django.db import models
from django.contrib.auth.models import User
import uuid


class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField()
    name_ext = models.CharField("Additional context to remember them by", blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(blank=True)
    location = models.CharField("City or state", blank=True)
    address = models.TextField(blank=True)
    company = models.CharField(blank=True)
    birthday = models.DateField(blank=True, null=True)
    how_we_met = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    ai_summary = models.TextField(blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='created_people')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.name_ext:
            return f"{self.name} ({self.name_ext})"
        return self.name
    
    @property
    def last_contacted(self):
        last_conversation = self.conversations.order_by('-date').first()
        return last_conversation.date if last_conversation else None


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CONVERSATION_TYPES = [
        ('in_person', 'In Person'),
        ('phone', 'Phone Call'),
        ('text', 'Text Message'),
        ('email', 'Email'),
        ('video', 'Video Call'),
        ('other', 'Other'),
    ]
    
    participants = models.ManyToManyField(Person, related_name='conversations')
    date = models.DateField()
    type = models.CharField(choices=CONVERSATION_TYPES)
    location = models.CharField(blank=True)
    notes = models.TextField()
    private = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='created_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        participant_names = ", ".join([p.name for p in self.participants.all()])
        return f"{self.date} - {participant_names}"
    
    class Meta:
        ordering = ['-date']


class ContactAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ATTEMPT_TYPES = [
        ('text', 'Text Message'),
        ('email', 'Email'),
        ('call', 'Phone Call'),
        ('social', 'Social Media'),
        ('other', 'Other'),
    ]
    
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='contact_attempts')
    date = models.DateField()
    type = models.CharField(choices=ATTEMPT_TYPES)
    notes = models.TextField(blank=True)
    led_to_conversation = models.BooleanField(default=False)
    private = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='created_contact_attempts')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.date} - {self.type} to {self.person.name}"
    
    class Meta:
        ordering = ['-date']


class Relationship(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    RELATIONSHIP_TYPES = [
        ('partner', 'Partner'),
        ('family', 'Family'),
        ('friend', 'Friend'),
        ('colleague', 'Colleague'),
        ('acquaintance', 'Acquaintance'),
        ('other', 'Other'),
    ]
    
    person1 = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='relationships_as_person1')
    person2 = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='relationships_as_person2')
    relationship_type = models.CharField(choices=RELATIONSHIP_TYPES)
    description = models.CharField(blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='created_relationships')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.person1.name} - {self.person2.name} ({self.relationship_type})"
    
    class Meta:
        unique_together = ['person1', 'person2']