from rest_framework import serializers
from .models import Person, Conversation, ContactAttempt, Relationship


class PersonSerializer(serializers.ModelSerializer):
    last_contacted = serializers.DateField(read_only=True)

    class Meta:
        model = Person
        fields = [
            'id', 'name', 'name_ext', 'email', 'phone', 'birthday',
            'how_we_met', 'notes', 'ai_summary', 'created_at', 'last_contacted'
        ]
        read_only_fields = ['created_at', 'last_contacted']


class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Person.objects.all()
    )
    participant_names = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'participant_names', 'date', 'type', 
            'location', 'notes', 'created_at'
        ]
        read_only_fields = ['created_at', 'participant_names']

    def get_participant_names(self, obj):
        return [participant.name for participant in obj.participants.all()]


class ContactAttemptSerializer(serializers.ModelSerializer):
    person_name = serializers.ReadOnlyField(source='person.name')

    class Meta:
        model = ContactAttempt
        fields = [
            'id', 'person', 'person_name', 'date', 'type', 'notes', 
            'led_to_conversation', 'created_at'
        ]
        read_only_fields = ['created_at', 'person_name']


class RelationshipSerializer(serializers.ModelSerializer):
    person1_name = serializers.ReadOnlyField(source='person1.name')
    person2_name = serializers.ReadOnlyField(source='person2.name')

    class Meta:
        model = Relationship
        fields = [
            'id', 'person1', 'person1_name', 'person2', 'person2_name',
            'relationship_type', 'description', 'created_at'
        ]
        read_only_fields = ['created_at', 'person1_name', 'person2_name']