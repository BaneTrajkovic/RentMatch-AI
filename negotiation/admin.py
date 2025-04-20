from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Property, PropertyChat, PropertyChatMessage

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'address')
    search_fields = ('title', 'address')

class PropertyChatMessageInline(admin.TabularInline):
    model = PropertyChatMessage
    extra = 0
    readonly_fields = ('timestamp',)

@admin.register(PropertyChat)
class PropertyChatAdmin(admin.ModelAdmin):
    list_display = ('title', 'property', 'landlord', 'renter', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'property__title', 'landlord__username', 'renter__username')
    inlines = [PropertyChatMessageInline]

@admin.register(PropertyChatMessage)
class PropertyChatMessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender_type', 'user', 'timestamp')
    list_filter = ('sender_type', 'timestamp')
    search_fields = ('content', 'user__username')