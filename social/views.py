import requests
import urllib.parse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,redirect,get_object_or_404
from social.serilizers import AdminSerializer
from social.models import SuperAdmin,Post
from .models import AffiliateProfile
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import models
from .models import Post
from django.contrib.auth.decorators import login_required
from utils.cloudConnect import upload_image_to_cloudinary   
from .models import Like, Post, AffiliateProfile
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import *
from django.shortcuts import get_object_or_404
from .models import Post, Like, Comment, Share, AffiliateProfile
from utils.cloudConnect import upload_image_to_cloudinary    
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import check_password, make_password
from .models import AffiliateProfile, Post
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import AffiliateProfile



N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/social-post"
#sending image

N8N_Image_Url="http://localhost:5678/webhook-test/image-url"

def send_imageurl(image_url) :
    payload = {
        "image_url": image_url
    }

    try:
        response = requests.post(
            N8N_Image_Url,
            json=payload,
            timeout=40
        )
        print("Payload sent to N8N:", payload)
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

    print("N8N Response:", response.text)
    return JsonResponse({
        "success": True,
        "n8n_status": response.status_code,
        "n8n_response": response.text
    })

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
        print("Payload sent to N8N:", payload)
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

    print("N8N Response:", response.text)
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

#super admin registration

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
    print("Post submission received")
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
         # type: ignore
        post_id = post.id # type: ignore
        print("Post created with ID:", post_id)
        print("Image uploaded to Cloudinary:", image_url)
        send_imageurl(image_url)
        return send_image_to_n8n(image_url, caption,post.id) # type: ignore
    else:
        JsonResponse({"error": "Invalid method"}, status=405)


#affiliate user regestration


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
            request.session['affiliate_id'] = affiliate.id # type: ignore
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

def like_post(request):
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


#for affiliate regestration side
@require_POST
def affiliate_like_post(request):
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
def affiliate_comment_post(request):
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
def affiliate_share_post(request):
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




#  AFFILIATE SETTINGS PAGE
def usersettings(request):
    affiliate_id = request.session.get('affiliate_id')
    if not affiliate_id:
        return redirect('affiliate_login')

    affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
    return render(request, 'affiliatesettings.html', {'affiliate': affiliate})


# AFFILIATE PROFILE PAGE
# def affiliate_profile(request):
#     affiliate_id = request.session.get('affiliate_id')
#     if not affiliate_id:
#         return redirect('affiliate_login')

#     affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
#     return render(request, 'affiliate_profile.html', {'affiliate': affiliate})

#UPDATE AFFILIATE PROFILE (POST)
@require_POST
def update_affiliate_profile(request):
    affiliate_id = request.session.get('affiliate_id')

    if not affiliate_id:
        return redirect('affiliate_login')

    affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)

    affiliate.username = request.POST.get("username", affiliate.username)

    if request.POST.get("instagram_secret"):
        affiliate.instagram_secret = make_password(
            request.POST.get("instagram_secret")
        )

    if request.POST.get("facebook_secret"):
        affiliate.facebook_secret = make_password(
            request.POST.get("facebook_secret")
        )

    if request.POST.get("linkedin_secret"):
        affiliate.linkedin_secret = make_password(
            request.POST.get("linkedin_secret")
        )

    if request.POST.get("twitter_secret"):
        affiliate.twitter_secret = make_password(
            request.POST.get("twitter_secret")
        )

    affiliate.save()

    messages.success(request, "Profile updated successfully")
    return redirect('usersettings')

# CHANGE  AFFILIATE USER PASSWORD (POST)
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
    return redirect('usersettings')

# LOGOUT
def affiliate_logout(request):
    request.session.flush()
    return redirect('affiliate_login')





# Affiliate post action
# def affiliate_post_actoion(request):
#     if request.method == "POST":
#          affiliate_post_actoion.objects.create(                         #Affiliate_post_action.objects
#              affiliate_username = request.Post.get('username'),
#              post_id = request.POST.get('post_id'),
#              action = request.POST.get('actio'),
#              comment_text = request.POST.get('comment','')
#          )
#          return JsonResponse({'status': 'success'})
    


#SUPER ADMIN SIDE 
def posts_list(request):
     posts = Post.objects.all().order_by('-created_at')
     return render(request, 'postslist.html', {'posts': posts})



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
def afflilate_settings(request):
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
        super_admin=SuperAdmin.objects.get(id=user.id)

        super_admin.fbtoken=request.POST.get("fbtoken")
        super_admin.instatoken=request.POST.get("instatoken")
        super_admin.lntoken=request.POST.get("lntoken")
        super_admin.save()

        print(user)

        messages.success(request, "Profile updated successfully")
        return render(request, 'profile.html', {'super_admin': super_admin})

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
    super_admin=SuperAdmin.objects.get(id=request.user.id)
    user=super_admin
    resF=delete_facebook_post(post.fbpostid,user.fbtoken)
    resI=delete_instagram_post(post.instapostid, user.instatoken)       
    resL=delete_linkedin_post(post.lnpostid, user.lntoken)
    print("Facebook Deletion Response:", resF)
    print("Instagram Deletion Response:", resI)
    print("LinkedIn Deletion Response:", resL)
    post.delete()
    print("Posts deleted successfully")
    return redirect('posts_list')

def logout_view(request):
    logout(request)
    return redirect('log_admin')

@csrf_exempt
def collect_post_data(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Invalid method"},
            status=405
        )

    try:
        body = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON payload"},
            status=400
        )

    posts = body.get("posts")
    caption= body.get("caption")

    if not isinstance(posts, list):
        return JsonResponse(
            {"error": "`posts` must be a list"},
            status=400
        )

    for post in posts:
        platform = post.get("platform")
        pst=Post.objects.get(id=post.get("postid"))
        pst.caption=caption
        match platform:
            case "facebook":
                pst.fbpostid=post.get("post_id")
                pst.save()
            case "instagram":
                pst.instapostid=post.get("post_id")
                pst.save()
            case "linkedin":
                pst.lnpostid=post.get("post_id")
                pst.save()

    return JsonResponse(
        {
            "status": "success",
            "data": posts
        },
        status=200
    )



def delete_facebook_post(post_id, access_token):
    url = f"https://graph.facebook.com/v19.0/{post_id}"
    response = requests.delete(url, params={"access_token": access_token})
    return response.json()


def delete_instagram_post(media_id, access_token):
    url = f"https://graph.facebook.com/v19.0/{media_id}"
    response = requests.delete(url, params={"access_token": access_token})
    return response.json()



def delete_linkedin_post(post_urn, access_token):
    if not post_urn:
        return {"error": "post_urn is empty"}

    # Ensure string
    post_urn = str(post_urn)

    # Ensure full URN
    if not post_urn.startswith("urn:li:"):
        post_urn = f"urn:li:ugcPost:{post_urn}"

    # Encode URN
    encoded_urn = urllib.parse.quote(post_urn, safe="")

    url = f"https://api.linkedin.com/v2/ugcPosts/{encoded_urn}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    response = requests.delete(url, headers=headers)

    return {
        "status_code": response.status_code,
        "response": response.text or "Deleted"
    }

