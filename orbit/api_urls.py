from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PersonViewSet, ConversationViewSet, ContactAttemptViewSet, RelationshipViewSet,
    current_user, login_view, logout_view, csrf_token, dashboard_analytics,
    location_suggestions, company_suggestions
)

router = DefaultRouter()
router.register('people', PersonViewSet, basename='person')
router.register('conversations', ConversationViewSet, basename='conversation')
router.register('contact-attempts', ContactAttemptViewSet, basename='contactattempt')
router.register('relationships', RelationshipViewSet, basename='relationship')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', dashboard_analytics, name='dashboard-analytics'),
    path('suggestions/locations/', location_suggestions, name='location-suggestions'),
    path('suggestions/companies/', company_suggestions, name='company-suggestions'),
    path('auth/user/', current_user, name='current-user'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/csrf/', csrf_token, name='csrf-token'),
]