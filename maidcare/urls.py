from django.contrib import admin
from django.urls import path
from maidcare import views

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls, name='admin'),

    # ================= USER SIDE =================
    path('', views.request_service, name='home'),
    path('request/', views.request_service, name='request_service'),
    path('login/', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('user-forgot-password/', views.user_forgot_password, name='user_forgot_password'),
    path('user-reset-password/', views.user_reset_password, name='user_reset_password'),
    path('profile/', views.user_profile, name='user_profile'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('user-logout/', views.user_logout, name='user_logout'),

    # ================= ADMIN AUTH =================
    path('adminlogin/', views.admin_login, name='admin_login'),
    path('admindashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('forgot-password/', views.forgot_password, name='admin_forgot_password'),
    path('reset-password/', views.reset_password, name='admin_reset_password'),
    path('logout/', views.logout_view, name='admin_logout'),

    # ================= CATEGORY =================
    path('category/', views.category, name='category'),
    path('delete-category/<str:id>/', views.delete_category, name='delete_category'),

    # ================= HOUSEKEEPER =================
    path('housekeeper/', views.housekeeper, name='housekeeper'),
    path('delete-housekeeper/<str:id>/', views.delete_housekeeper, name='delete_housekeeper'),
    path('edit-housekeeper/<str:id>/', views.edit_housekeeper, name='edit_housekeeper'),

    # ================= HIRING =================
    path('hiring/', views.show_request, name='hiring_requests'),

    # ================= API =================
    path('api/requests/', views.get_requests_api, name='api_get_requests'),
    path('api/create-request/', views.create_request_api, name='api_create_request'),
    path('api/housekeepers/', views.get_housekeepers_api, name='api_get_housekeepers'),
    path('api/assign/', views.assign_housekeeper_api, name='api_assign_housekeeper'),
]