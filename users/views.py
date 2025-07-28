import json
from django.utils import timezone
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from django.contrib.auth.models import User

from users.models import FollowRequest
from .models import *
from .serializers import UserProfileSerializer, UserSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from users.forms import CustomLoginForm
from core.views import home
from django import forms
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from rest_framework.decorators import api_view

from .utils import generate_otp, send_otp_email
from django.http import HttpResponse
from .forms import EditProfileForm
from .models import OTPVerification



class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('search')
        if query:
            return User.objects.filter(Q(username__icontains=query) | Q(email__icontains=query))
        return super().get_queryset()

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            messages.success(request, "Registration successful. Please log in.")
            return redirect("login")  # Redirect back to login page

    return render(request, "register.html")

# User Login View
def custom_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.last_login_time = timezone.now()
            profile.save()

            login(request, user)
            return redirect('home') 
        else:
            # ✅ Show custom error message
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()
    
    return render(request, 'login.html', {'form': form})

# User Logout View
def custom_logout(request):
    logout(request)
    return redirect('login')
 
def dashboard(request):
    return redirect('index')

@login_required
def send_follow_request(request, user_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # AJAX check
        to_user = get_object_or_404(User, id=user_id)
        if request.user != to_user:
            FollowRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
        return JsonResponse({'status': 'ok'})
    else:
        # fallback for non-AJAX POST (optional)
        return redirect('profile')


@require_POST
@login_required
def undo_follow_request(request, user_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        to_user = get_object_or_404(User, id=user_id)
        FollowRequest.objects.filter(from_user=request.user, to_user=to_user).delete()
        return JsonResponse({'status': 'ok'})
    else:
        return redirect('profile')


def accept_follow_request(request, request_id):
    if request.method == "POST":
        follow_request = FollowRequest.objects.filter(id=request_id).first()

        if follow_request:
            from_user = follow_request.from_user
            to_user = follow_request.to_user

            follow_request.delete()

            # Create mutual follows
            Follow.objects.get_or_create(follower=from_user, followed=to_user)
            Follow.objects.get_or_create(follower=to_user, followed=from_user)

            return JsonResponse({
                "success": True,
                "follow_back": True,
                "request_from_id": from_user.id
            })
        else:
            return JsonResponse({"success": False, "error": "Request not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})



@require_POST
@login_required
def unfriend_user(request, user_id):
    if request.method == "POST":
        from_user = request.user
        to_user = get_object_or_404(User, id=user_id)

        Follow.objects.filter(follower=from_user, followed=to_user).delete()
        Follow.objects.filter(follower=to_user, followed=from_user).delete()

        return JsonResponse({
            "status": "ok", 
            "username": to_user.username
        })
    return JsonResponse({"status": "error", "error": "Invalid request"}, status=400)

# 
@login_required
def profile_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    return render(request, 'users/profile.html', {
        'user': user,     
        'profile': profile
    })

def edit_profile_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received Data:", data)
            user = request.user
            profile, _ = UserProfile.objects.get_or_create(user=user)

            user.email = data.get('email', user.email)
            user.save()

            profile.phone_number = data.get('phone_number', profile.phone_number)
            profile.bio = data.get('bio', profile.bio)
            profile.save()

            print("Updated email:", user.email)
            print("Updated phone:", profile.phone_number)
            print("Updated bio:", profile.bio)

            return JsonResponse({'success': True})
        except Exception as e:
            print("Error in edit_profile_api:", e)
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid method'})

@login_required
def request_delete_account(request):
    if request.method == "POST":
        user = request.user
        otp = generate_otp()
        OTPVerification.objects.create(user=user, otp=otp)
        send_otp_email(user, otp)
        return JsonResponse({'message': f'OTP sent to {user.email[-13:]}'})
    return JsonResponse({'error': 'Invalid method'}, status=405)

@login_required
def verify_otp_delete(request):
    if request.method == "POST":
        data = json.loads(request.body)
        entered_otp = data.get("otp")
        try:
            # otp_record = OTPVerification.objects.get(user=request.user)
            otp_record = OTPVerification.objects.filter(user=request.user).order_by('-created_at').first()

            if otp_record.otp == entered_otp and otp_record.is_valid():
                request.user.delete()
                logout(request)
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"error": "Invalid OTP"}, status=400)
        except OTPVerification.DoesNotExist:
            return JsonResponse({"error": "No OTP record found"}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)