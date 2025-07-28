from django.shortcuts import redirect, render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import File, UploadedFile, UserProfile
from users.models import FollowRequest, Follow ,UserProfile
from .serializers import FileSerializer
from django.contrib.auth.models import User
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from .forms import FileUploadForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse

from core import models
from users.utils import are_mutually_following
from core.models import UploadedFile 
def home(request):
    return render(request, 'home.html')

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return File.objects.filter(
            Q(uploader=self.request.user) | Q(shared_with=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        file = self.get_object()
        user_id = request.data.get('user_id')
        user_to_share = get_object_or_404(User, pk=user_id)
        file.shared_with.add(user_to_share)
        return Response({'status': 'file shared'})

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        file = self.get_object()
        if request.user != file.uploader and request.user not in file.shared_with.all():
            return Response({'error': 'Unauthorized'}, status=403)
        return FileResponse(file.file.open('rb'), as_attachment=True, filename=file.filename)

@login_required
def upload_view(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.uploaded_by = request.user
            file.save()
            return redirect("upload")
    else:
        form = FileUploadForm()
    return render(request, "upload.html", {"form": form})

@login_required
def profile_view(request, user_id=None):
    profile_user = get_object_or_404(User, id=user_id) if user_id else request.user
    profile, created = UserProfile.objects.get_or_create(user=profile_user)

    friends = User.objects.filter(
        id__in=Follow.objects.filter(follower=request.user).values_list('followed_id', flat=True)
    ).filter(
        id__in=Follow.objects.filter(followed=request.user).values_list('follower_id', flat=True)
    )

    # 🛠️ FIX: Exclude users who sent you a request
    incoming_requests = FollowRequest.objects.filter(
        to_user=request.user, is_accepted=False
    ).values_list('from_user_id', flat=True)

    # ✅ Now exclude: self, friends, and pending incoming requests
    other_users = User.objects.exclude(id=request.user.id)\
                              .exclude(id__in=friends)\
                              .exclude(id__in=incoming_requests)

    sent_requests = FollowRequest.objects.filter(from_user=request.user).values_list('to_user_id', flat=True)

    if request.user == profile_user:
        follow_requests = FollowRequest.objects.filter(to_user=request.user, is_accepted=False)
    else:
        follow_requests = None

    return render(request, 'profile.html', {
        'profile': profile,
        'other_users': other_users,
        'follow_requests': follow_requests,
        'friends': friends,
        'sent_requests': sent_requests,
    })


def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            filename = uploaded_file.name

            # Check if file with same name and user exists
            existing_file = UploadedFile.objects.filter(
                file__icontains=filename, uploaded_by=request.user
            ).first()

            if existing_file:
                # Delete old file from storage
                existing_file.file.delete(save=False)

                # Update the existing record
                existing_file.file = uploaded_file
                existing_file.description = form.cleaned_data['description']
                existing_file.save()
            else:
                # Create new file record
                new_upload = form.save(commit=False)
                new_upload.uploaded_by = request.user
                new_upload.save()

            return redirect('upload')
    else:
        form = FileUploadForm()

    recent_files = UploadedFile.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')[:5]
    return render(request, 'upload.html', {'form': form, 'files': recent_files})

@login_required
def view_user_files(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    print("DEBUG → you:", request.user, "| viewing:", other_user,
          "| mutual? ->", are_mutually_following(request.user, other_user))
    
    if are_mutually_following(request.user, other_user):
        files = UploadedFile.objects.filter(uploaded_by=other_user)
        return render(request, 'view_files.html', {
            'files': files,
            'viewing_user': other_user
        })
    else:
        return HttpResponse("Access Denied: You are not friends with this user.")
    
@login_required
def accept_follow(request, user_id):
    from_user = get_object_or_404(User, id=user_id)
    to_user = request.user

    if from_user == to_user:
        return JsonResponse({'success': False, 'error': 'Cannot follow yourself.'}, status=400)

    Follow.objects.get_or_create(follower=to_user, followed=from_user)

    return JsonResponse({'success': True})