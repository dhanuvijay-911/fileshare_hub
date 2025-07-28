from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class UserProfile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)  # ✅ Added phone number
    bio = models.TextField(blank=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()

class FollowRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='follow_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='follow_requests_received', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user} → {self.to_user} ({'Accepted' if self.is_accepted else 'Pending'})"

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='follows', on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name='followed_by', on_delete=models.CASCADE)
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"

class OTPVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() <= self.created_at + timedelta(minutes=10)
