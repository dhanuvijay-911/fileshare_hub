from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='core_profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    friends = models.ManyToManyField('self', symmetrical=True, blank=True)

    def __str__(self):
        return self.user.username

class File(models.Model):
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    file = models.FileField(upload_to='user_files/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    shared_with = models.ManyToManyField(User, related_name='shared_files', blank=True)

    def __str__(self):
        return f"{self.filename} uploaded by {self.uploader.username}"
class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.file.name} uploaded by {self.uploaded_by.username}"
    
class FollowRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username} (Pending)"
