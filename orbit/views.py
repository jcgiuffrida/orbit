from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import Person, Conversation, ContactAttempt, Relationship
from .serializers import (
    PersonSerializer, ConversationSerializer, 
    ContactAttemptSerializer, RelationshipSerializer
)


class PersonViewSet(viewsets.ModelViewSet):
    serializer_class = PersonSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # People are shared across all family members
        return Person.objects.all().order_by('name')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Include public conversations (private=False) and private conversations created by current user
        return Conversation.objects.filter(
            Q(private=False) | Q(private=True, created_by=self.request.user)
        ).order_by('-date')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ContactAttemptViewSet(viewsets.ModelViewSet):
    serializer_class = ContactAttemptSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Include public contact attempts (private=False) and private attempts created by current user
        return ContactAttempt.objects.filter(
            Q(private=False) | Q(private=True, created_by=self.request.user)
        ).order_by('-date')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class RelationshipViewSet(viewsets.ModelViewSet):
    serializer_class = RelationshipSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Relationships are shared across all family members
        return Relationship.objects.all().order_by('person1__name')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# Auth API endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current authenticated user info"""
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login endpoint"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        return Response({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            }
        })
    else:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout endpoint"""
    logout(request)
    return Response({'success': True})


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_token(request):
    """Get CSRF token for frontend"""
    return Response({'csrfToken': get_token(request)})


# Frontend view
def index_view(request):
    """Serve the Vue.js frontend"""
    from django.shortcuts import render
    return render(request, 'index.html')