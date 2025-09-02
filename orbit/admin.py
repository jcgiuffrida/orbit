from django.contrib import admin
from .models import Person, Conversation, ContactAttempt, Relationship


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_ext', 'location', 'email', 'phone', 'conversations_')
    list_filter = ('created_at', 'birthday_month', 'location')
    search_fields = ('name', 'name_ext', 'location', 'email', 'how_we_met', 'notes')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'name_ext', 'location', 'address', 'company', 'email', 'phone', 'birthday_month', 'birthday_day', 'birth_year')
        }),
        ('Background', {
            'fields': ('how_we_met', 'notes')
        }),
        ('AI Summary', {
            'fields': ('ai_summary',),
            'classes': ('collapse',)
        }),
        ('Meta', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

    def conversations_(self, obj):
        return obj.conversations.count()


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('date', 'type', 'location', 'get_participants', 'created_at')
    list_filter = ('type', 'date', 'created_at')
    search_fields = ('notes', 'location')
    readonly_fields = ('created_at',)
    filter_horizontal = ('participants',)
    
    def get_participants(self, obj):
        return ", ".join([p.name for p in obj.participants.all()])
    get_participants.short_description = 'Participants'


@admin.register(ContactAttempt)
class ContactAttemptAdmin(admin.ModelAdmin):
    list_display = ('person', 'date', 'type', 'led_to_conversation', 'created_at')
    list_filter = ('type', 'date', 'created_at')
    search_fields = ('person__name', 'notes')
    readonly_fields = ('created_at',)


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ('person1', 'person2', 'relationship_type', 'description', 'created_at')
    list_filter = ('relationship_type', 'created_at')
    search_fields = ('person1__name', 'person2__name', 'description')
    readonly_fields = ('created_at',)