from .models import FollowRequest
from users.models import Follow
import random
from django.core.mail import send_mail
from django.conf import settings

def are_mutually_following(user1, user2):
    if user1 == user2:
        return True

    return (
        Follow.objects.filter(follower=user1, followed=user2).exists() and
        Follow.objects.filter(follower=user2, followed=user1).exists()
    )

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user, otp):
    subject = 'OTP for Account Deletion - FileShare Hub'
    message = f'Your OTP for deleting your FileShare Hub account "{user}" is: {otp}\n\nDo not share this code with anyone.'
    from_email = None
    recipient_list = [user.email]

    print(f"Sending OTP to {user.email}...")  # ✅ for debugging/logging
    send_mail(subject, message, from_email, recipient_list)