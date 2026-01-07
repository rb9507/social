from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class SuperAdmin(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name



#code for affiliated user regestration backend

class AffiliateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    instagram_secret = models.CharField(max_length=255)
    linkedin_secret = models.CharField(max_length=255)
    facebook_secret = models.CharField(max_length=255)
    twitter_secret = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
