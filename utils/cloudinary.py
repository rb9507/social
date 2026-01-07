import cloudinary.uploader

def upload_image_to_cloudinary(django_file):
    result = cloudinary.uploader.upload(
        django_file,
        folder="n8nData"
    )
    return result["secure_url"]
