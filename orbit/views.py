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
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_analytics(request):
    """Get dashboard analytics data"""
    now = timezone.now()
    today = now.date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)
    two_years_ago = today - timedelta(days=730)
    
    # Recent conversations (last 10)
    recent_conversations = Conversation.objects.filter(
        Q(private=False) | Q(private=True, created_by=request.user)
    ).order_by('-date')[:10]
    
    # Top contacts by conversation count in past 1-2 years
    top_contacts = Person.objects.annotate(
        recent_conversation_count=Count(
            'conversations',
            filter=Q(conversations__date__gte=two_years_ago) &
                   (Q(conversations__private=False) | Q(conversations__private=True, conversations__created_by=request.user))
        )
    ).filter(recent_conversation_count__gt=0).order_by('-recent_conversation_count')[:10]
    
    # Activity counts
    conversations_week = Conversation.objects.filter(
        Q(date__gte=week_ago) &
        (Q(private=False) | Q(private=True, created_by=request.user))
    ).count()
    
    conversations_month = Conversation.objects.filter(
        Q(date__gte=month_ago) &
        (Q(private=False) | Q(private=True, created_by=request.user))
    ).count()
    
    conversations_year = Conversation.objects.filter(
        Q(date__gte=year_ago) &
        (Q(private=False) | Q(private=True, created_by=request.user))
    ).count()
    
    contact_attempts_week = ContactAttempt.objects.filter(
        Q(date__gte=week_ago) &
        (Q(private=False) | Q(private=True, created_by=request.user))
    ).count()
    
    contact_attempts_month = ContactAttempt.objects.filter(
        Q(date__gte=month_ago) &
        (Q(private=False) | Q(private=True, created_by=request.user))
    ).count()
    
    contact_attempts_year = ContactAttempt.objects.filter(
        Q(date__gte=year_ago) &
        (Q(private=False) | Q(private=True, created_by=request.user))
    ).count()
    
    # People to reach out to (those with conversations but none recently)
    # Find people with conversations > 30 days ago but historically active
    people_to_reach_out = Person.objects.filter(
        conversations__isnull=False
    ).annotate(
        total_conversations=Count('conversations', filter=
            Q(conversations__private=False) | Q(conversations__private=True, conversations__created_by=request.user)
        ),
        recent_conversations=Count('conversations', filter=
            Q(conversations__date__gte=month_ago) &
            (Q(conversations__private=False) | Q(conversations__private=True, conversations__created_by=request.user))
        )
    ).filter(
        total_conversations__gte=3,  # At least 3 total conversations
        recent_conversations=0       # But none in past month
    ).distinct()[:10]
    
    # Monthly activity data for chart (past 6 months)
    monthly_data = []
    for month in range(6):
        # Calculate month boundaries
        if month == 0:
            month_end = today
        else:
            month_end = (today.replace(day=1) - timedelta(days=1)).replace(day=1) if month == 1 else (today.replace(day=1) - timedelta(days=32*month)).replace(day=1) - timedelta(days=1)
        
        if month == 0:
            month_start = today.replace(day=1)
        else:
            temp_date = today.replace(day=1) - timedelta(days=32*month)
            month_start = temp_date.replace(day=1)
        
        # Adjust end date for current month
        if month == 0:
            month_end = today
        else:
            # Get last day of the month
            next_month = month_start.replace(day=28) + timedelta(days=4)
            month_end = next_month - timedelta(days=next_month.day)
        
        conv_count = Conversation.objects.filter(
            Q(date__gte=month_start) & Q(date__lte=month_end) &
            (Q(private=False) | Q(private=True, created_by=request.user))
        ).count()
        
        attempt_count = ContactAttempt.objects.filter(
            Q(date__gte=month_start) & Q(date__lte=month_end) &
            (Q(private=False) | Q(private=True, created_by=request.user))
        ).count()
        
        monthly_data.append({
            'month_start': month_start,
            'month_end': month_end,
            'month_name': month_start.strftime('%B %Y'),
            'conversations': conv_count,
            'contact_attempts': attempt_count
        })
    
    monthly_data.reverse()  # Show chronologically
    
    return Response({
        'recent_conversations': ConversationSerializer(recent_conversations, many=True).data,
        'top_contacts': PersonSerializer(top_contacts, many=True).data,
        'activity_overview': {
            'conversations': {
                'week': conversations_week,
                'month': conversations_month,
                'year': conversations_year
            },
            'contact_attempts': {
                'week': contact_attempts_week,
                'month': contact_attempts_month,
                'year': contact_attempts_year
            }
        },
        'people_to_reach_out': PersonSerializer(people_to_reach_out, many=True).data,
        'monthly_activity': monthly_data
    })


# Frontend view
def index_view(request):
    """Serve the Vue.js frontend"""
    from django.shortcuts import render
    return render(request, 'index.html')