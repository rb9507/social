from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
   path("upload-image/", send_image_to_n8n, name="upload_image"),
   path("super-admin/", superAdmin, name="super_admin")
]
