from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.apps import AppConfig
from django.contrib.auth.models import Group
from django.utils import timezone


class BlogConfig(AppConfig):
    name = 'blog'

    def ready(self):
        Group.objects.get_or_create(name='Users')
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  
    published = models.BooleanField(default=False)  
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)  
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Relacionar o post com o utilizador que o criou


    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.title}'