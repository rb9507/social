from django import views
from django.contrib import admin
from django.urls import path
from .views import *  

from . import views   

urlpatterns = [
   path("upload-image/", send_image_to_n8n, name="upload_image"),
   path("super-admin/", superAdmin, name="super_admin"),
   path("admin-registration/", admin_registration, name="admin_registration"),
   path("create-admin/", create_admin, name="create_admin"),
   path("log-admin/", log_admin, name="log_admin"),
   path("auth-admin/", auth_admin, name="auth_admin"),
   path("create-post/", create_post, name="create_post"),
   path("post-submitted/", post_submitted, name="post_submitted"),
   path("posts-list/", posts_list, name="posts_list"),
   path("affiliate-register/", affiliate_register, name="affiliate_register"),
   path("affiliate-login/", affiliate_login, name="affiliate_login"),
   path("affiliate-dashboard/", affiliate_dashboard, name="affiliate_dashboard"),
   path("like/",Like_post,name="Like_post"),
   path("comment/",comment_post,name="comment_post"),
   path("share/",share_post,name="share_post"),
   #path('like-post/', views.Like_post, name='like_post'),
   path('like-post/',views.like_post,name='like_post'),
   path('comment-post/', views.comment_post, name='comment_post'),
   path('share-post/', views.share_post, name='share_post'),
   path('affiliate-feed/', views.affiliate_feed, name='affiliate_feed'),
   path('user/settings/', views.afflilate_settings, name='affliatesettings'), 
   #path('affiliate-logout/', views.affiliate_logout, name='affiliate_logout'),
   path('edit-profile/', views.edit_affiliate_profile, name='edit_affiliate_profile'),
   path('change-password/', views.change_password_page, name='change_password_page'),



   path('update-profile/', views.update_affiliate_profile, name='update_affiliate_profile'),
   path('update-password/', views.change_affiliate_password, name='change_affiliate_password'),
   path('user/logout/', views.affiliate_logout, name='affiliate_logout'),
   path("users/", affiliate_users, name="affiliate_users"),
   path("settings/", setting, name="settings"),
   path("profile/", profile, name="profile"),
   path("update-profile/", update_admin_profile, name="update_profile"),
   path("change-password/", change_password, name="change_password"),
   path("update-password/", update_password, name="update_password"),
   path("edit-post/<int:post_id>", editpost, name="edit_post"),
   path("submit-edit-post/<int:post_id>", submit_editpost, name="submit_edit_post"), # type: ignore
   path("delete-post/<int:post_id>", del_post, name="delete_post"),
   path("logout/", logout_view, name="logout"),
   path("delete-post/<int:post_id>", del_post, name="delete_post"),
   path("webhoook/n8n/media/", store_media_id, name="n8n_webhook_media")
]






