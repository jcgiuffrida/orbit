"""
URL configuration for the project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from orbit.views import index_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('orbit.api_urls')),
    # Serve Vue.js frontend for all other routes
    re_path(r'^(?!admin|api).*$', index_view, name='frontend'),
]
