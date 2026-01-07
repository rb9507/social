import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,redirect
from social.serilizers import AdminSerializer
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from .models import AffiliateProfile

N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/social-post"
#sending image

@csrf_exempt
def send_image_to_n8n(request):
    if request.method == "POST":
        image = request.FILES.get("image")
        caption = request.POST.get("caption")

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

    return JsonResponse({"error": "Invalid method"}, status=405)
#superadmin login and regestration
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

        return render(request, 'superadmin.html')
    
    return JsonResponse({"error": "Invalid method"}, status=405)


 ##Affiliated user regestration  backend login

 
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

        user = User.objects.create(
            username=username,
            password=make_password(password)
        )

        AffiliateProfile.objects.create(
            user=user,
            instagram_secret=make_password(instagram_secret),
            linkedin_secret=make_password(linkedin_secret),
            facebook_secret=make_password(facebook_secret),
            twitter_secret=make_password(twitter_secret),
        )

        messages.success(request, "Registration successful")
        return redirect('affiliate_register')

    return render(request, 'registration.html')
