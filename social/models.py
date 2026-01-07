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

    def __str__(self):
        return f"Post  - {self.caption[:20]}"