from django.urls import path
from .views import post_list, new_post, post_detail, edit_comment, delete_comment
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 

urlpatterns = [
    path('', post_list, name='post_list'),
    path('new_post/', new_post, name='new_post'),
    path('post/<int:pk>/', post_detail, name='post_detail'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),  
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),  
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout, name='logout'), 
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('comment/edit/<int:comment_id>/', edit_comment, name='edit_comment'),
    path('comment/delete/<int:comment_id>/', delete_comment, name='delete_comment'),
]