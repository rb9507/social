from django.contrib import admin
from django.urls import path
from .views import send_image_to_n8n

urlpatterns = [
   path("upload-image/", send_image_to_n8n, name="upload_image")
]
