from rest_framework import serializers
from .models import Person, Conversation, ContactAttempt, Relationship


class PersonSerializer(serializers.ModelSerializer):
    last_contacted = serializers.DateField(read_only=True)
    created_by_username = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Person
        fields = [
            'id', 'name', 'name_ext', 'email', 'phone', 'location', 'birthday',
            'how_we_met', 'notes', 'ai_summary', 'created_by_username', 
            'created_at', 'last_contacted'
        ]
        read_only_fields = ['created_at', 'last_contacted', 'created_by_username']


class ConversationSerializer(serializers.ModelSerializer):
    participants = PersonSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Person.objects.all(),
        source='participants',
        write_only=True
    )
    created_by_username = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'participant_ids', 'date', 'type', 
            'location', 'notes', 'private', 'created_by_username', 'created_at'
        ]
        read_only_fields = ['created_at', 'participants', 'created_by_username']


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