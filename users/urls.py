from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserProfileViewSet
from . import views
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profile', UserProfileViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    path('', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('home/', views.dashboard, name='home'),
    path('follow/<int:user_id>/', views.send_follow_request, name='send_follow'),
    # path('accept-follow/<int:user_id>/', views.accept_follow_request, name='accept_follow'),
    path('undo-follow/<int:user_id>/', views.undo_follow_request, name='undo_follow'),

#  urls related to profile editing
    path('profile/', views.profile_view, name='profile_view'),
    path('delete-request/', views.request_delete_account, name='request_delete_account'),
    path('verify-delete-otp/', views.verify_otp_delete, name='verify_delete_otp'),

# urls related to edit profile
    path('api/users/edit-profile/', views.edit_profile_api, name='edit_profile_api'),

]
