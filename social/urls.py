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
<<<<<<< HEAD
   path("register/",views.affiliate_register,name='affiliate_register'),
   path("login/",views.affiliate_login,name='affiliate_login'),
   path("dashboard/", views.affiliate_dashboard, name="affiliate_dashboard"),

      

=======
   path("log-admin/", log_admin, name="log_admin"),
   path("auth-admin/", auth_admin, name="auth_admin"),
   path("create-post/", create_post, name="create_post"),
   path("post-submitted/", post_submitted, name="post_submitted")
>>>>>>> 0cce5019967b306a709b8fa567e62635e78dc287
]
