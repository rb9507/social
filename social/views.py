import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/django-trigger"

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
            timeout=20
        )

        return JsonResponse({
            "success": True,
            "n8n_status": response.status_code
        })

    return JsonResponse({"error": "Invalid method"}, status=405)
