from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Other Info'
    
# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    
# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
