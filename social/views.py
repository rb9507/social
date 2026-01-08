import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,redirect
from social.serilizers import AdminSerializer
from social.models import SuperAdmin,Post
from django.contrib.auth import authenticate, login
from erp.utils.cloudConnect import upload_image_to_cloudinary

N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/social-post"


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

        if not username or not password:
            return JsonResponse({
                "success": False,
                "message": "Username and password are required"
            }, status=400)

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:
            return JsonResponse({
                "success": False,
                "message": "Invalid username or password"
            }, status=400)

        # Login strictly using request data
        login(request, user)

        posts=Post.objects.all().order_by('-created_at')

        return render(request, 'superadmin.html',{'posts':posts})

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

        post_id = post.id
        print("Post created with ID:", post_id)
        print("Image uploaded to Cloudinary:", image_url)

        return send_image_to_n8n(image_url, caption, post_id)

    return JsonResponse({"error": "Invalid method"}, status=405)
