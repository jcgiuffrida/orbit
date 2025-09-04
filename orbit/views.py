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
from django.db.models import Q, Count, Max
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Person, Conversation, ContactAttempt, Relationship
from .serializers import (
    PersonSerializer, PersonDetailedSerializer, ConversationSerializer, 
    ContactAttemptSerializer, RelationshipSerializer
)


class PersonViewSet(viewsets.ModelViewSet):
    serializer_class = PersonSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # People are shared across all family members
        return Person.objects.all().select_related('created_by').annotate(last_contacted=Max('conversations__date')).order_by('name')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Include public conversations (private=False) and private conversations created by current user
        queryset = Conversation.objects.filter(
            Q(private=False) | Q(private=True, created_by=self.request.user)
        ).prefetch_related('participants').select_related('created_by')
        
        # Filter by participant if provided
        participant_id = self.request.query_params.get('participant', None)
        if participant_id:
            try:
                queryset = queryset.filter(participants__id=participant_id)
            except (ValueError, TypeError) as e:
                # Return empty queryset if participant_id is invalid
                return Conversation.objects.none()
        
        return queryset.order_by('-date')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ContactAttemptViewSet(viewsets.ModelViewSet):
    serializer_class = ContactAttemptSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Include public contact attempts (private=False) and private attempts created by current user
        return ContactAttempt.objects.filter(
            Q(private=False) | Q(private=True, created_by=self.request.user)
        ).select_related('person', 'created_by').order_by('-date')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class RelationshipViewSet(viewsets.ModelViewSet):
    serializer_class = RelationshipSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Relationships are shared across all family members
        return Relationship.objects.select_related(
            'person1', 'person2', 'created_by',    
        ).order_by('person1__name')
    
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


def get_upcoming_birthdays(days_ahead=30):
    """Get upcoming birthdays in the next N days"""
    from datetime import date
    from .serializers import PersonSerializer
    
    today = date.today()
    birthdays = []
    
    # Get all people with birthdays (month and day must be present)
    people_with_birthdays = Person.objects.filter(
        birthday_month__isnull=False,
        birthday_day__isnull=False
    ).select_related('created_by')
    
    for person in people_with_birthdays:
        # Calculate next birthday occurrence
        try:
            # Try this year first
            birthday_this_year = date(today.year, person.birthday_month, person.birthday_day)
            
            if birthday_this_year >= today:
                next_birthday = birthday_this_year
            else:
                # Birthday has passed this year, use next year
                next_birthday = date(today.year + 1, person.birthday_month, person.birthday_day)
                
            days_until = (next_birthday - today).days
            
            if days_until <= days_ahead:
                birthday_data = PersonSerializer(person).data
                birthday_data['next_birthday'] = next_birthday.isoformat()
                birthday_data['days_until'] = days_until
                birthday_data['is_today'] = days_until == 0
                birthdays.append(birthday_data)
                
        except ValueError:
            # Handle invalid dates (like Feb 29 on non-leap years)
            continue
    
    # Sort by days until birthday
    birthdays.sort(key=lambda x: x['days_until'])
    return birthdays


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_analytics(request):
    """Get dashboard analytics data"""
    now = timezone.now()
    today = now.date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    six_months_ago = today - timedelta(days=30 * 6)
    year_ago = today - timedelta(days=365)
    two_years_ago = today - timedelta(days=730)
    
    # Recent conversations (last 10, within past year)
    recent_conversations = Conversation.objects.filter(
        Q(date__gte=year_ago) &
        (Q(private=False) | Q(created_by=request.user))
    ).prefetch_related('participants').order_by('-date')[:10]
    
    # Top contacts by conversation count in past 1-2 years
    top_contacts = Person.objects.annotate(
        recent_conversation_count=Count(
            'conversations',
            filter=Q(conversations__date__gte=two_years_ago) &
                   (Q(conversations__private=False) | Q(conversations__created_by=request.user))
        )
    ).filter(recent_conversation_count__gt=0).order_by('-recent_conversation_count')[:10]
    
    # Activity counts
    conversations_week = Conversation.objects.filter(
        Q(date__gte=week_ago) &
        (Q(private=False) | Q(created_by=request.user))
    ).count()
    
    conversations_month = Conversation.objects.filter(
        Q(date__gte=month_ago) &
        (Q(private=False) | Q(created_by=request.user))
    ).count()
    
    conversations_year = Conversation.objects.filter(
        Q(date__gte=year_ago) &
        (Q(private=False) | Q(created_by=request.user))
    ).count()
    
    contact_attempts_week = ContactAttempt.objects.filter(
        Q(date__gte=week_ago) &
        (Q(private=False) | Q(created_by=request.user))
    ).count()
    
    contact_attempts_month = ContactAttempt.objects.filter(
        Q(date__gte=month_ago) &
        (Q(private=False) | Q(created_by=request.user))
    ).count()
    
    contact_attempts_year = ContactAttempt.objects.filter(
        Q(date__gte=year_ago) &
        (Q(private=False) | Q(created_by=request.user))
    ).count()
    
    # People to reach out to (those with conversations but none recently)
    # Find people with conversations > 30 days ago but historically active
    people_to_reach_out = Person.objects.filter(
        conversations__isnull=False
    ).annotate(
        total_conversations=Count('conversations', filter=
            (Q(conversations__private=False) | Q(conversations__created_by=request.user)) & Q(conversations__date__gte=two_years_ago)
        ),
        recent_conversations=Count('conversations', filter=
            Q(conversations__date__gte=six_months_ago) &
            (Q(conversations__private=False) | Q(conversations__created_by=request.user))
        )
    ).filter(
        total_conversations__gte=3,  # At least 3 total conversations
        recent_conversations=0       # But none recently
    ).distinct()[:10]
    
    # Monthly activity data for chart (past 12 months)
    monthly_data = []
    current_date = today.replace(day=1)  # Start of current month
    
    for month in range(12):
        # Calculate the target month (going backwards)
        if month == 0:
            target_month = current_date
        else:
            # Go back month by month
            year = current_date.year
            month_num = current_date.month - month
            while month_num <= 0:
                month_num += 12
                year -= 1
            target_month = current_date.replace(year=year, month=month_num, day=1)
        
        # Calculate month boundaries
        month_start = target_month
        
        # Get the last day of this month
        if target_month.month == 12:
            next_month_start = target_month.replace(year=target_month.year + 1, month=1, day=1)
        else:
            next_month_start = target_month.replace(month=target_month.month + 1, day=1)
        month_end = next_month_start - timedelta(days=1)
        
        # For current month, don't go beyond today
        if month == 0:
            month_end = min(month_end, today)
        
        conv_count = Conversation.objects.filter(
            Q(date__gte=month_start) & Q(date__lte=month_end) &
            (Q(private=False) | Q(created_by=request.user))
        ).count()
        
        attempt_count = ContactAttempt.objects.filter(
            Q(date__gte=month_start) & Q(date__lte=month_end) &
            (Q(private=False) | Q(created_by=request.user))
        ).count()
        
        monthly_data.append({
            'month_start': month_start,
            'month_end': month_end,
            'month_name': month_start.strftime('%B %Y'),
            'conversations': conv_count,
            'contact_attempts': attempt_count
        })
    
    monthly_data.reverse()  # Show chronologically (oldest first)
    
    # Upcoming birthdays in the next 30 days
    upcoming_birthdays = get_upcoming_birthdays(days_ahead=30)
    
    return Response({
        'recent_conversations': ConversationSerializer(recent_conversations, many=True).data,
        'top_contacts': PersonDetailedSerializer(top_contacts, many=True).data,
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
        'monthly_activity': monthly_data,
        'upcoming_birthdays': upcoming_birthdays
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def location_suggestions(request):
    """Get unique location suggestions for auto-complete"""
    locations = Person.objects.exclude(location='').values_list('location', flat=True).distinct()
    return Response({'locations': sorted(set(locations))})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def company_suggestions(request):
    """Get unique company suggestions for auto-complete"""
    companies = Person.objects.exclude(company='').values_list('company', flat=True).distinct()
    return Response({'companies': sorted(set(companies))})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_location_suggestions(request):
    """Get unique conversation location suggestions for auto-complete"""
    locations = Conversation.objects.exclude(location='').values_list('location', flat=True).distinct()
    return Response({'locations': sorted(set(locations))})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def birthday_timeline(request):
    """Get birthday timeline starting from today"""
    days_ahead = int(request.GET.get('days', 365))  # Default to 1 year
    return Response({
        'birthdays': get_upcoming_birthdays(days_ahead=days_ahead)
    })


# Frontend view
def index_view(request):
    """Serve the Vue.js frontend"""
    from django.shortcuts import render
    return render(request, 'index.html')