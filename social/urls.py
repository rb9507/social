from django.urls import path
from . import views

urlpatterns = [
    # COMMON / INTEGRATIONS
    path("upload-image/", views.send_image_to_n8n, name="upload_image"),
    # path("webhoook/n8n/media/", views.store_media_id, name="n8n_webhook_media"),

    # SUPER ADMIN URLS
    path("super-admin/", views.superAdmin, name="super_admin"),
    path("admin-registration/", views.admin_registration, name="admin_registration"),
    path("create-admin/", views.create_admin, name="create_admin"),
    path("log-admin/", views.log_admin, name="log_admin"),
    path("auth-admin/", views.auth_admin, name="auth_admin"),

    path("create-post/", views.create_post, name="create_post"),
    path("post-submitted/", views.post_submitted, name="post_submitted"),
    path("posts-list/", views.posts_list, name="posts_list"),

    path("edit-post/<int:post_id>", views.editpost, name="edit_post"),
    path("submit-edit-post/<int:post_id>", views.submit_editpost, name="submit_edit_post"),
    path("delete-post/<int:post_id>", views.del_post, name="delete_post"),

    path("users/", views.affiliate_users, name="affiliate_users"),
    path("settings/", views.setting, name="settings"),
    path("profile/", views.profile, name="profile"),
    path("update-profile/", views.update_admin_profile, name="update_profile"),
    path("change-password/", views.change_password, name="change_password"),
    path("update-password/", views.update_password, name="update_password"),
    path("logout/", views.logout_view, name="logout"),

    # AFFILIATE USER URLS
    path("affiliate-register/", views.affiliate_register, name="affiliate_register"),
    path("affiliate-login/", views.affiliate_login, name="affiliate_login"),
    path("affiliate-dashboard/", views.affiliate_dashboard, name="affiliate_dashboard"),
    path("affiliate-feed/", views.affiliate_feed, name="affiliate_feed"),

    path("affiliate/like/", views.like_post, name="like_post"),
    path("affiliate/comment/", views.comment_post, name="comment_post"),
    path("affiliate/share/", views.share_post, name="share_post"),

    path("like_post/", views.like_post, name="like_post"),
    path("comment-post/", views.comment_post, name="comment_post"),
    path("share-post/", views.share_post, name="share_post"),

    path("user/settings/", views.usersettings, name="usersettings"),
    path("edit-profile/", views.edit_affiliate_profile, name="edit_affiliate_profile"),
    path("affiliate/change-password/", views.change_password_page, name="change_password_page"),
    path("affiliate/update-profile/", views.update_affiliate_profile, name="update_affiliate_profile"),
    path("affiliate/update-password/", views.change_affiliate_password, name="change_affiliate_password"),
    path("affiliate-logout/", views.affiliate_logout, name="affiliate_logout"),
]
