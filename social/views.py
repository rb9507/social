import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,redirect
from social.serilizers import AdminSerializer
from social.models import SuperAdmin,Post
from .models import AffiliateProfile
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth import authenticate, login
#from .models import AffiliateLogin
from django.db import models
from .models import Post
#from .models import Post, AffiliatePostAction
from django.contrib.auth.decorators import login_required
from utils.cloudConnect import upload_image_to_cloudinary   
from .models import Like, Post, AffiliateProfile
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import *
from django.shortcuts import get_object_or_404
from .models import Post, Like, Comment, Share, AffiliateProfile

N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/social-post"
#sending image


def send_image_to_n8n(image_url, caption,post_id):
    payload = {
        "image_url": image_url,
        "caption": caption,
        "post_id": post_id
    }

    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            timeout=40
        )
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

    return JsonResponse({
        "success": True,
        "n8n_status": response.status_code,
        "n8n_response": response.text
    })




@login_required
def superAdmin(request):
    posts = Post.objects.order_by('-created_at')[:6]
    posts_count = Post.objects.count()
    users = SuperAdmin.objects.count()

    return render(
        request,
        'superadmin.html',
        {
            'posts': posts,
            'posts_count': posts_count,
            'users': users
        }
    )
 

def admin_registration(request):
    return render(request, 'adminregestration.html')

def create_admin(request):
    if request.method == "POST":
        name = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        print(name, email, password)

        serialize_admin = AdminSerializer(data={
            "name": name,
            "email": email,
            "password": password
        }, context=request)

        if serialize_admin.is_valid():
            serialize_admin.save()
        else:
            return JsonResponse({
                "success": False,
                "message": "Invalid data provided"
            }, status=400)

        return redirect('/social/log-admin/')
        
    return JsonResponse({"error": "Invalid method"}, status=405)

def log_admin(request):
    return render(request, 'superadminlogin.html')




def auth_admin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse({"success": False}, status=400)

        login(request, user)
        return redirect('super_admin')  # URL of dashboard

    return JsonResponse({"error": "Invalid method"}, status=405)



def create_post(request):
    return render(request, 'createpost.html')


def post_submitted(request):
    if request.method == "POST":
        image = request.FILES.get("post_image")
        caption = request.POST.get("post_text")

        if not image or not caption:
            return JsonResponse({
                "success": False,
                "message": "Image and caption are required"
            }, status=400)

        try:
            super_admin = request.user.super_admin
        except SuperAdmin.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "Only SuperAdmins can create posts"
            }, status=403)

        # ✅ Upload FIRST
        image_url = upload_image_to_cloudinary(image)

        # ✅ Then save post
        post = Post.objects.create(
            image=image,   # optional if you want local storage
            caption=caption,
            created_by=super_admin
        )

        post_id = post.id # type: ignore
        print("Post created with ID:", post_id)
        print("Image uploaded to Cloudinary:", image_url)

    return JsonResponse({"error": "Invalid method"}, status=405)


#affiliate user regestration
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import AffiliateProfile


def affiliate_register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        instagram_secret = request.POST.get('instagram_secret')
        linkedin_secret = request.POST.get('linkedin_secret')
        facebook_secret = request.POST.get('facebook_secret')
        twitter_secret = request.POST.get('twitter_secret')

        if AffiliateProfile.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('affiliate_register')

        AffiliateProfile.objects.create(
            username=username,
            password=make_password(password),  # hash password
            instagram_secret=make_password(instagram_secret),
            linkedin_secret=make_password(linkedin_secret),
            facebook_secret=make_password(facebook_secret),
            twitter_secret=make_password(twitter_secret),
        )

        messages.success(request, "Affiliate registered successfully")
        return redirect('affiliate_login')

    return render(request, 'regestration.html')

#Affiliated user Login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import AffiliateProfile


def affiliate_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            affiliate = AffiliateProfile.objects.get(username=username)
        except AffiliateProfile.DoesNotExist:
            messages.error(request, "Invalid username or password")
            return redirect('affiliate_login')

        if check_password(password, affiliate.password):
            # ✅ store affiliate id in session
            request.session['affiliate_id'] = affiliate.id
            request.session['affiliate_username'] = affiliate.username

            return redirect('affiliate_dashboard')  # REDIRECT HERE
        else:
            messages.error(request, "Invalid username or password")
            return redirect('affiliate_login')

    return render(request, 'affiliateduserlogin.html')


# Affiliated user dashboard
def affiliate_dashboard(request):
    if not request.session.get('affiliate_id'):
        return redirect('affiliate_login')

    posts = Post.objects.all().order_by('-created_at')

    return render(
        request,
        'affiliate_userdashboard.html',
        {'posts': posts}
    )

def Like_post(request):
    affiliate_id = request.session.get("affiliate_id")
    post_id = request.POST.get("post_id")
    affiliate = AffiliateProfile.objects.get(id=affiliate_id)
    post = Post.objects.get(id=post_id)
    Like.objects.get_or_create(affiliate = affiliate,post=post)
    return JsonResponse({"status":"success"})

def comment_post(request):
    affiliate_id = request.session.get("affiliate_id")
    post_id = request.POST.get("post_id")
    comment_text = request.POST.get("comment_text")
    affiliate = AffiliateProfile.objects.get(id=affiliate_id)
    post = Post.objects.get(id=post_id)
    Comment.objects.create(affiliate = affiliate,post=post,text=comment_text)
    return JsonResponse({"status":"succcess"})

def share_post(request):
    affiliate_id = request.session.get("affiliate_id")
    post_id = request.POST.get("post_id")
    platform = request.POST.get("platform")
    affiliate = AffiliateProfile.objects.get(id=affiliate_id)
    post = Post.objects.get(id=post_id)
    Share.objects.create(affiliate = affiliate,post=post,platform=platform)
    return JsonResponse({"status":"success"})

def affiliate_dashboard(request):
    posts = Post.objects.all().order_by("-created_at")
    return render(request, 'affiliate_userdashboard.html',{'posts': posts})


# # Affiliate post action
# def affiliate_post_actoion(request):
#     if request.method == "POST":
#          AffiliatePostAction.objects.create(
#              affiliate_username = request.Post.get('username'),
#              post_id = request.POST.get('post_id'),
#              action = request.POST.get('actio'),
#              comment_text = request.POST.get('comment','')
#          )
#          return JsonResponse({'status': 'success'})

def posts_list(request):
     posts = Post.objects.all().order_by('-created_at')
     return render(request, 'postslist.html', {'posts': posts})

# def affiliate_dashboard(request):
#     if not request.session.get('affiliate_id'):
#         return redirect('affiliate_login')

#     posts = Post.objects.filter(is_active=True).order_by('-created_at')

#     return render(
#         request,
#         "affiliate_userdashboard.html",
#         {"posts": posts}
#     )
# LIKE POST
@require_POST
def like_post(request):
    affiliate_id = request.session.get("affiliate_id")

    if not affiliate_id:
        return JsonResponse(
            {"error": "Affiliate not logged in"},
            status=403
        )

    post_id = request.POST.get("post_id")

    if not post_id:
        return JsonResponse(
            {"error": "Post ID missing"},
            status=400
        )

    affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
    post = get_object_or_404(Post, id=post_id)

    like, created = Like.objects.get_or_create(
        affiliate=affiliate,
        post=post
    )

    if not created:
        return JsonResponse({
            "status": "already_liked",
            "message": "You already liked this post"
        })

    return JsonResponse({
        "status": "success",
        "message": "Post liked successfully"
    })



# COMMENT POST
@require_POST
def comment_post(request):
    affiliate_id = request.session.get("affiliate_id")

    if not affiliate_id:
        return JsonResponse(
            {"error": "Affiliate not logged in"},
            status=403
        )

    post_id = request.POST.get("post_id")
    comment_text = request.POST.get("comment_text")

    if not post_id or not comment_text:
        return JsonResponse(
            {"error": "Post ID or comment missing"},
            status=400
        )

    affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
    post = get_object_or_404(Post, id=post_id)

    Comment.objects.create(
        affiliate=affiliate,
        post=post,
        text=comment_text
    )

    return JsonResponse({
        "status": "success",
        "message": "Comment added successfully"
    })


# SHARE POST
@require_POST
def share_post(request):
    affiliate_id = request.session.get("affiliate_id")

    if not affiliate_id:
        return JsonResponse(
            {"error": "Affiliate not logged in"},
            status=403
        )

    post_id = request.POST.get("post_id")
    platform = request.POST.get("platform")

    if not post_id or not platform:
        return JsonResponse(
            {"error": "Post ID or platform missing"},
            status=400
        )

    affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
    post = get_object_or_404(Post, id=post_id)

    Share.objects.create(
        affiliate=affiliate,
        post=post,
        platform=platform
    )

    return JsonResponse({
        "status": "success",
        "message": "Post shared successfully"
    })

# #Affiliate user settings and profile management
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from django.contrib.auth.hashers import check_password, make_password
# from .models import AffiliateProfile


# # =========================
# # AFFILIATE PROFILE VIEW
# # =========================
# def affiliate_profile(request):
#     affiliate_id = request.session.get('affiliate_id')

#     if not affiliate_id:
#         return redirect('affiliate_login')

#     affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)

#     return render(
#         request,
#         'affiliate_profile.html',
#         {'affiliate': affiliate}
#     )


# # =========================
# # UPDATE AFFILIATE PROFILE
# # =========================
# @require_POST
# def update_affiliate_profile(request):
#     affiliate_id = request.session.get('affiliate_id')

#     if not affiliate_id:
#         return redirect('affiliate_login')

#     affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)

#     affiliate.username = request.POST.get('username', affiliate.username)

#     # Update secrets only if provided
#     instagram_secret = request.POST.get('instagram_secret')
#     facebook_secret = request.POST.get('facebook_secret')
#     linkedin_secret = request.POST.get('linkedin_secret')
#     twitter_secret = request.POST.get('twitter_secret')

#     if instagram_secret:
#         affiliate.instagram_secret = make_password(instagram_secret)
#     if facebook_secret:
#         affiliate.facebook_secret = make_password(facebook_secret)
#     if linkedin_secret:
#         affiliate.linkedin_secret = make_password(linkedin_secret)
#     if twitter_secret:
#         affiliate.twitter_secret = make_password(twitter_secret)

#     affiliate.save()

#     messages.success(request, "Profile updated successfully")
#     return redirect('settings')


# # =========================
# # CHANGE AFFILIATE PASSWORD
# # =========================
# @require_POST
# def change_affiliate_password(request):
#     affiliate_id = request.session.get('affiliate_id')

#     if not affiliate_id:
#         return redirect('affiliate_login')

#     affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)

#     old_password = request.POST.get('old_password')
#     new_password = request.POST.get('new_password')
#     confirm_password = request.POST.get('confirm_password')

#     if not check_password(old_password, affiliate.password):
#         messages.error(request, "Old password is incorrect")
#         return redirect('settings')

#     if new_password != confirm_password:
#         messages.error(request, "Passwords do not match")
#         return redirect('settings')

#     affiliate.password = make_password(new_password)
#     affiliate.save()

#     messages.success(request, "Password changed successfully")
#     return redirect('settings')


# def affiliate_feed(request):
#     if not request.session.get('affiliate_id'):
#         return redirect('affiliate_login')

#     posts = Post.objects.all().order_by('-created_at')

#     return render(
#         request,
#         'affiliate_userdashboard.html',
#         {'posts': posts}
#     )

# def affiliate_logout(request):
#     request.session.flush()
#     return redirect('affiliate_login')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import check_password, make_password

from .models import AffiliateProfile, Post


# =========================
# AFFILIATE FEED
# =========================
def affiliate_feed(request):
    if not request.session.get('affiliate_id'):
        return redirect('affiliate_login')

    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'affiliate_userdashboard.html', {'posts': posts})


# =========================
# SETTINGS PAGE
# =========================
def settings(request):
    affiliate_id = request.session.get('affiliate_id')
    if not affiliate_id:
        return redirect('affiliate_login')

    affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
    return render(request, 'settings.html', {'affiliate': affiliate})


# =========================
# AFFILIATE PROFILE PAGE
# =========================
def affiliate_profile(request):
    affiliate_id = request.session.get('affiliate_id')
    if not affiliate_id:
        return redirect('affiliate_login')

    affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
    return render(request, 'affiliate_profile.html', {'affiliate': affiliate})


# =========================
# UPDATE PROFILE (POST)
# =========================
@require_POST
def update_affiliate_profile(request):
    affiliate = get_object_or_404(
        AffiliateProfile,
        id=request.session.get('affiliate_id')
    )

    affiliate.username = request.POST.get('username')

    if request.POST.get('instagram_secret'):
        affiliate.instagram_secret = make_password(request.POST.get('instagram_secret'))
    if request.POST.get('facebook_secret'):
        affiliate.facebook_secret = make_password(request.POST.get('facebook_secret'))
    if request.POST.get('linkedin_secret'):
        affiliate.linkedin_secret = make_password(request.POST.get('linkedin_secret'))
    if request.POST.get('twitter_secret'):
        affiliate.twitter_secret = make_password(request.POST.get('twitter_secret'))

    affiliate.save()
    messages.success(request, "Profile updated successfully")
    return redirect('settings')


# =========================
# CHANGE PASSWORD (POST)
# =========================
@require_POST
def change_affiliate_password(request):
    affiliate = get_object_or_404(
        AffiliateProfile,
        id=request.session.get('affiliate_id')
    )

    if not check_password(request.POST.get('old_password'), affiliate.password):
        messages.error(request, "Old password is incorrect")
        return redirect('affiliate_profile')

    if request.POST.get('new_password') != request.POST.get('confirm_password'):
        messages.error(request, "Passwords do not match")
        return redirect('affiliate_profile')

    affiliate.password = make_password(request.POST.get('new_password'))
    affiliate.save()

    messages.success(request, "Password changed successfully")
    return redirect('settings')


# =========================
# LOGOUT
# =========================
def affiliate_logout(request):
    request.session.flush()
    return redirect('affiliate_login')
def edit_affiliate_profile(request):
    affiliate_id = request.session.get('affiliate_id')
    if not affiliate_id:
        return redirect('affiliate_login')

    affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
    return render(request, 'edit_affiliate_profile.html', {'affiliate': affiliate})


def change_password_page(request):
    affiliate_id = request.session.get('affiliate_id')
    if not affiliate_id:
        return redirect('affiliate_login')

    return render(request, 'change_password.html')
