from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PersonViewSet, ConversationViewSet, ContactAttemptViewSet, RelationshipViewSet

router = DefaultRouter()
router.register('people', PersonViewSet)
router.register('conversations', ConversationViewSet)
router.register('contact-attempts', ContactAttemptViewSet)
router.register('relationships', RelationshipViewSet)

urlpatterns = [
    path('', include(router.urls)),
]