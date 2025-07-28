from django.contrib import admin
from .models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'bio')
from .models import Follow, FollowRequest, OTPVerification

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followed')

@admin.register(FollowRequest)
class FollowRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user')

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp', 'created_at')

admin.site.unregister(User)
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass