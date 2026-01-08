from django.contrib import admin
from django.urls import path
from .views import *
from .views import affiliate_register   

urlpatterns = [
   path("upload-image/", send_image_to_n8n, name="upload_image"),
   path("super-admin/", superAdmin, name="super_admin"),
   path("admin-registration/", admin_registration, name="admin_registration"),
   path("create-admin/", create_admin, name="create_admin"),
   path("log-admin/", log_admin, name="log_admin"),
   path("auth-admin/", auth_admin, name="auth_admin"),
   path("create-post/", create_post, name="create_post"),
   path("post-submitted/", post_submitted, name="post_submitted"),
   path("posts-list/", posts_list, name="posts_list")
]
