from .forms import PostForm, UserRegisterForm, CommentForm, ContactForm, ProfileUpdateForm, ProfilePictureForm
from .models import Post, Comment, Profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.test import TestCase
from django.http import JsonResponse
from django.contrib.auth.forms import UserChangeForm


# Create your views here.

def custom_logout(request):
    logout(request)
    return redirect('post_list')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  
            group = Group.objects.get(name='Users')
            user.groups.add(group)
            
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been successfully created! You can now log in.')
            return redirect('login')  
    else:
        form = UserRegisterForm()
    return render(request, 'blog/register.html', {'form': form})

def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    
    query = request.GET.get('q')  
    
    if query:
        posts = Post.objects.filter(title__icontains=query)  
    else:
        posts = Post.objects.all().order_by('title')
    
    is_super_admin = request.user.groups.filter(name="Super Admin").exists()
    is_user_with_account = request.user.groups.filter(name="Users").exists()
    
    context = {
        'posts': posts,
        'is_super_admin': is_super_admin,
        'is_user_with_account': is_user_with_account,
        'query': query  
    }
    
    return render(request, 'blog/post_list.html', context)

@login_required(login_url='/login/')
def new_post(request):
    
    if request.user.groups.filter(name__in=['Super Admin', 'Users']).exists():
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user  
                post.save()
                return redirect('post_list')
        else:
            form = PostForm()
        return render(request, 'blog/new_post.html', {'form': form})
    else:
        return redirect('post_list')

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.user == post.author or request.user.is_superuser:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES, instance=post)
            if form.is_valid():
                form.save()
                return redirect('post_detail', pk=post.pk)
        else:
            form = PostForm(instance=post)
        return render(request, 'blog/edit_post.html', {'form': form, 'post': post})
    else:
        return redirect('post_list')

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user == post.author or request.user.groups.filter(name='Super Admin').exists():
        post.delete()
        return redirect('post_list')
    else:
        return redirect('post_list')

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    comments = post.comments.all()  # type: ignore
    
    editing_comment_id = request.GET.get('edit_comment')

    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = request.user  
            comment.save()
            return redirect('post_detail', pk=post.pk)  
    else:
        comment_form = CommentForm()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'editing_comment_id': int(editing_comment_id) if editing_comment_id 
        else None
    })
    
def about(request):
    return render(request, 'blog/about.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
        else:
            messages.error(request, 'There was an error with your submission. Please try again.')
    else:
        form = ContactForm()

    return render(request, 'blog/contact.html', {'form': form})

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user == comment.user or request.user.is_superuser:
        if request.method == 'POST':
            form = CommentForm(request.POST, instance=comment)
            if form.is_valid():
                form.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': form.errors}, status=400)
    return JsonResponse({'success': False}, status=403)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user == comment.user or request.user.is_superuser:
        post_id = comment.post.pk
        comment.delete()
        return redirect('post_detail', pk=post_id)
    else:
        return redirect('post_list')




@login_required
def profile_view(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)  # Garante que o perfil existe
    if request.method == 'POST':
        user_form = ProfileUpdateForm(request.POST, instance=request.user)
        picture_form = ProfilePictureForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and picture_form.is_valid():
            user_form.save()
            picture_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        user_form = ProfileUpdateForm(instance=request.user)
        picture_form = ProfilePictureForm(instance=user_profile)

    context = {
        'user_form': user_form,
        'picture_form': picture_form
    }
    return render(request, 'blog/profile.html', context)

