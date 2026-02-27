"""
URL configuration for maidcare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("",views.request_service),
    path("request/", views.request_service),
    path('adminlogin/',views.admin_login),
    path('admindashboard/',views.admin_dashboard),
    path("category/",views.category),
   path("delete-category/<str:id>/", views.delete_category, name="delete_category"),
    path("housekeeper/",views.housekeeper),
    path("delete-housekeeper/<str:id>/", views.delete_housekeeper, name="delete_housekeeper"),
    path("edit-housekeeper/<str:id>/", views.edit_housekeeper, name="edit_housekeeper"),
    path("hiring/",views.show_request),
    path("logout/",views.logout_view),
]
