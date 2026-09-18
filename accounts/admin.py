from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'warehouse')
    list_filter = ('role', 'warehouse')
    search_fields = ('user__username', 'user__email', 'phone')
    raw_id_fields = ('user',)
