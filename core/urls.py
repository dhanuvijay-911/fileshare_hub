from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FileViewSet, home, upload_file, profile_view, accept_follow, view_user_files
from django.contrib.auth import views as auth_views
from users.views import accept_follow_request, unfriend_user

router = DefaultRouter()
router.register(r'files', FileViewSet)

urlpatterns = [
    # Auth routes
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Core app views
    path('upload/', upload_file, name='upload'),
    path('profile/', profile_view, name='profile'),
    path('profile/<int:user_id>/', profile_view, name='profile_view'),
    path('api/users/home/', home, name='home'),

    # Follow-related actions
    path('accept-follow-request/<int:request_id>/', accept_follow_request, name='accept_follow_request'),
    path('accept-follow/<int:user_id>/', accept_follow, name='accept_follow'),
    path('api/users/unfriend/<int:user_id>/', unfriend_user, name='unfriend_user'),

    # DRF API routes
    path('api/', include(router.urls)),

    #Files related 
    path('users/<int:user_id>/files/', view_user_files, name='view_user_files'),

]
