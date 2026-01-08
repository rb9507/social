from django.contrib import admin
from django.urls import path
from .views import *
from .views import affiliate_register
from . import views
from .views import affiliate_dashboard
urlpatterns = [
   path("upload-image/", send_image_to_n8n, name="upload_image"),
   path("super-admin/", superAdmin, name="super_admin"),
   path("admin-registration/", admin_registration, name="admin_registration"),
   path("create-admin/", create_admin, name="create_admin"),
   path("register/",views.affiliate_register,name='affiliate_register'),
   path("login/",views.affiliate_login,name='affiliate_login'),
   path("dashboard/", views.affiliate_dashboard, name="affiliate_userdashboard"),

      

]
