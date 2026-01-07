from django.db import models

# Create your models here.
class SuperAdmin(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class Post(models.Model):
    image = models.ImageField(upload_to='posts/')
    caption = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(SuperAdmin, on_delete=models.CASCADE)

    def __str__(self):
        return f"Post  - {self.caption[:20]}"