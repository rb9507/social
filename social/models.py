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
    username = models.CharField(max_length=150,unique=True)
    password = models.CharField(max_length=255,unique=True)

    instagram_secret = models.CharField(max_length=255)
    linkedin_secret = models.CharField(max_length=255)
    facebook_secret = models.CharField(max_length=255)
    twitter_secret = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    affiliate = models.ForeignKey(AffiliateProfile, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.affiliate.username} on Post {self.post.id}" # type: ignore
    

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    affiliate = models.ForeignKey(AffiliateProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'affiliate')
    def __str__(self):
        return f"Like by {self.affiliate.username} on Post {self.post.id}" # type: ignore
    

class Share(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    affiliate = models.ForeignKey(AffiliateProfile, on_delete=models.CASCADE)
    platform = models.CharField(
        max_length=20,
        choices=[
            ('instagram', 'Instagram'),
            ('linkedin', 'LinkedIn'),
            ('facebook', 'Facebook'),
            ('twitter', 'Twitter'),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Share by {self.affiliate.username} on {self.platform}"


# class AffiliatePostAction(models.Model):
#     affiliate_username = models.CharField(max_length=150)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#     action = models.CharField(
#         max_length=20,
#         choices = [
#             ('like','Like'),
#             ('share','Share'),
#             ('comment','Comment')
#         ]
#     )
#     comment_text = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.affiliate_username} - {self.action}"

