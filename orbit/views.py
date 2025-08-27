from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Person, Conversation, ContactAttempt, Relationship
from .serializers import (
    PersonSerializer, ConversationSerializer, 
    ContactAttemptSerializer, RelationshipSerializer
)


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all().order_by('name')
    serializer_class = PersonSerializer
    permission_classes = [IsAuthenticated]


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().order_by('-date')
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]


class ContactAttemptViewSet(viewsets.ModelViewSet):
    queryset = ContactAttempt.objects.all().order_by('-date')
    serializer_class = ContactAttemptSerializer
    permission_classes = [IsAuthenticated]


class RelationshipViewSet(viewsets.ModelViewSet):
    queryset = Relationship.objects.all().order_by('person1__name')
    serializer_class = RelationshipSerializer
    permission_classes = [IsAuthenticated]