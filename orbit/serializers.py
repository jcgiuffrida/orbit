from rest_framework import serializers
from .models import Person, Conversation, ContactAttempt, Relationship
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Q


class PersonSerializer(serializers.ModelSerializer):
    last_contacted = serializers.DateField(read_only=True)
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    conversation_count = serializers.SerializerMethodField()
    conversation_count_recent = serializers.SerializerMethodField()
    days_since_last_contact = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = [
            'id', 'name', 'name_ext', 'email', 'phone', 'location', 'address', 'company', 'birthday',
            'how_we_met', 'notes', 'ai_summary', 'created_by_username', 
            'created_at', 'last_contacted', 'conversation_count', 
            'conversation_count_recent', 'days_since_last_contact'
        ]
        read_only_fields = [
            'created_at', 'last_contacted', 'created_by_username', 
            'conversation_count', 'conversation_count_recent', 'days_since_last_contact'
        ]

    def get_conversation_count(self, obj):
        """Total conversation count"""
        return obj.conversations.count()

    def get_conversation_count_recent(self, obj):
        """Conversation count in past 2 years"""
        two_years_ago = timezone.now().date() - timedelta(days=365*2)
        return obj.conversations.filter(date__gte=two_years_ago).count()

    def get_days_since_last_contact(self, obj):
        """Days since last conversation"""
        if obj.last_contacted:
            return (timezone.now().date() - obj.last_contacted).days
        return None


class ConversationSerializer(serializers.ModelSerializer):
    participants = PersonSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Person.objects.all(),
        source='participants',
        write_only=True
    )
    participant_names = serializers.SerializerMethodField()
    created_by_username = serializers.ReadOnlyField(source='created_by.username')

    def get_participant_names(self, obj):
        return [participant.name for participant in obj.participants.all()]

    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'participant_ids', 'participant_names', 'date', 'type', 
            'location', 'notes', 'private', 'created_by_username', 'created_at'
        ]
        read_only_fields = ['created_at', 'participants', 'participant_names', 'created_by_username']


class ContactAttemptSerializer(serializers.ModelSerializer):
    person_name = serializers.ReadOnlyField(source='person.name')
    created_by_username = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = ContactAttempt
        fields = [
            'id', 'person', 'person_name', 'date', 'type', 'notes', 
            'led_to_conversation', 'private', 'created_by_username', 'created_at'
        ]
        read_only_fields = ['created_at', 'person_name', 'created_by_username']


class RelationshipSerializer(serializers.ModelSerializer):
    person1_name = serializers.ReadOnlyField(source='person1.name')
    person2_name = serializers.ReadOnlyField(source='person2.name')
    created_by_username = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Relationship
        fields = [
            'id', 'person1', 'person1_name', 'person2', 'person2_name',
            'relationship_type', 'description', 'created_by_username', 'created_at'
        ]
        read_only_fields = ['created_at', 'person1_name', 'person2_name', 'created_by_username']