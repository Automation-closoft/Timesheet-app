from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_name']  # Removed 'phone_number' since it's no longer in the model

admin.site.register(UserProfile, UserProfileAdmin)