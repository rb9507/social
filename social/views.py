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

N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/social-post"
#sending image

@csrf_exempt
def send_image_to_n8n(img,cap):
        image = img
        caption = cap

        if not image or not caption:
            return JsonResponse({"error": "Image and caption required"}, status=400)

        files = {
            "image": (image.name, image.read(), image.content_type)
        }

        data = {
            "caption": caption
        }

        response = requests.post(
            N8N_WEBHOOK_URL,
            files=files,
            data=data,
            timeout=40
        )

        return JsonResponse({
            "success": True,
            "n8n_status": response.status_code
        })

def superAdmin(request):
    return render(request, 'superadmin.html')  

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

        uname=SuperAdmin.objects.get(name=username)
        if uname.password==password:
                return render(request, 'superadmin.html')
        else:
                return JsonResponse({
                    "success": False,
                    "message": "Invalid Password"
                }, status=400)

    return JsonResponse({"error": "Invalid method"}, status=405)

def create_post(request):
    return render(request, 'createpost.html')

def post_submitted(request):
    if request.method == "POST":
        image = request.FILES.get("image")
        caption = request.POST.get("caption")

        post = Post.objects.create(
            image=image,
            caption=caption,
            created_by=SuperAdmin.objects.first()  # Assuming the first SuperAdmin is creating the post
        )

        response = send_image_to_n8n(image, caption)
        return response

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


         




