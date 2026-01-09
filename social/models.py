from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class SuperAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='super_admin')
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
class Post(models.Model):
    image = models.ImageField(upload_to='media/')
    caption = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(SuperAdmin, on_delete=models.CASCADE)
    imediaid=models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return f"Post  - {self.caption[:20]}"


#affiliated user regestration  for  storing in database
class AffiliateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    instagram_secret = models.CharField(max_length=255)
    linkedin_secret = models.CharField(max_length=255)
    facebook_secret = models.CharField(max_length=255)
    twitter_secret = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


    
#Affiliated user login for storing data in database

class AffiliateLogin(models.Model):
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=255)  # HASHED password
    login_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

#Affiliated userdashboard for storing data in database....
# Super Admin Posts
# class AdminPost(models.Model):
#     caption = models.CharField(max_length=200)
#     description = models.TextField()
#     image = models.ImageField(upload_to='posts/')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.caption

# Affiliate Actions on Posts
class AffiliatePostAction(models.Model):
    affiliate_username = models.CharField(max_length=150)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    action = models.CharField(
        max_length=20,
        choices = [
            ('like','Like'),
            ('share','Share'),
            ('comment','Comment')
        ]
    )
    comment_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.affiliate_username} - {self.action}"

