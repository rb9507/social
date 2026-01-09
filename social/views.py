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

from utils.cloudConnect import upload_image_to_cloudinary    
from django.contrib.auth import logout

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

def send_caption_to_n8n(caption):
    payload = {
        "caption": caption
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


def superAdmin(request):
    posts = Post.objects.order_by('-created_at')[:6]
    posts_count = Post.objects.count()
    users = AffiliateProfile.objects.count()

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
            messages.error(request, "Invalid username or password")
            return redirect('log_admin')

        login(request, user)
        return redirect('super_admin')  

    return JsonResponse({"error": "Invalid method"}, status=405)



def create_post(request):
    return render(request, 'createpost.html')


def post_submitted(request):
    if request.method == "POST":
        image = request.FILES.get("post_image")
        caption = request.POST.get("post_text")
        user=request.POST.get("user_id")  

        print("Admin User ID:", user)
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


        image_url = upload_image_to_cloudinary(image)

        
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
# Affiliate post action

def affiliate_post_actoion(request):
    if request.method == "POST":
         AffiliatePostAction.objects.create(
             affiliate_username = request.Post.get('username'),
             post_id = request.POST.get('post_id'),
             action = request.POST.get('actio'),
             comment_text = request.POST.get('comment','')
         )
         return JsonResponse({'status': 'success'})


def posts_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'postslist.html', {'posts': posts})

def affiliate_users(request):
    affiliate_profiles = AffiliateProfile.objects.all()
    return render(request, 'affiliateusers.html', {'user': affiliate_profiles})

def setting(request):
    return render(request, 'settings.html')

def profile(request):
    return render(request, 'profile.html')

def update_admin_profile(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        print(user)

        messages.success(request, "Profile updated successfully")
        return redirect('profile')

    return JsonResponse({"error": "Invalid method"}, status=405)

def change_password(request):
    return render(request, 'changepassword.html')

def update_password(request):
    if request.method == "POST":
        current_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password1")
        confirm_password = request.POST.get("new_password2")

        user = request.user

        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect")
            return redirect('change_password')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match")
            return redirect('change_password')

        user.set_password(new_password)
        user.save()


        messages.success(request, "Password updated successfully")
        return render(request, 'profile.html')

    return JsonResponse({"error": "Invalid method"}, status=405)

def editpost(request,post_id):
    post=Post.objects.get(id=post_id)
    return render(request, 'editpost.html', {'post': post})

def submit_editpost(request,post_id):
    if request.method == "POST":
        caption = request.POST.get("caption")
        post=Post.objects.get(id=post_id)
        post.caption=caption
        post.save()
        send_caption_to_n8n(caption)
        #messages.success(request, "Post updated successfully")
        return redirect('posts_list')
    
def del_post(request,post_id):
    post=Post.objects.get(id=post_id)
    post.delete()
    #messages.success(request, "Post deleted successfully")
    return redirect('posts_list')

def logout_view(request):
    logout(request)
    return redirect('log_admin')
