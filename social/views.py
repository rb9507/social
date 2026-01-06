import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,redirect
from social.serilizers import AdminSerializer
from social.models import SuperAdmin

N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/social-post"

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

        return redirect('log_admin/')
        
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