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
from .models import AffiliateLogin
from django.db import models
from .models import Post
from .models import Post, AffiliatePostAction
from django.contrib.auth.decorators import login_required
from utils.cloudConnect import upload_image_to_cloudinary    

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
def affiliate_register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        instagram_secret = request.POST.get('instagram_secret')
        linkedin_secret = request.POST.get('linkedin_secret')
        facebook_secret = request.POST.get('facebook_secret')
        twitter_secret = request.POST.get('twitter_secret')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('affiliate_register')

        user = User.objects.create_user(
            username=username,
            password=password
        )

        AffiliateProfile.objects.create(
            user = user,
            instagram_secret=make_password(instagram_secret),
            linkedin_secret=make_password(linkedin_secret),
            facebook_secret=make_password(facebook_secret),
            twitter_secret=make_password(twitter_secret),
        )

        messages.success(request, "Registration successful")
        return redirect('affiliate_login')
    

    return render(request, 'regestration.html')

#Affiliated user Login
def affiliate_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            AffiliateLogin.objects.create(
                username=username,
                password=password   # storing as-is (not recommended, but as you want)
            )

            return redirect('affiliate_userdashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "affiliateduserlogin.html")

# Affiliated user dashboard
def affiliate_dashboard(request):
    posts = Post.objects.all().order_by("-created_at")
    return render(request, 'affiliate_userdashboard.html',{'posts': posts})
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