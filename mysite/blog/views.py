from .models import Post, Comment
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm, UserRegisterForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages


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
            messages.success(request, f'A tua conta foi criada com sucesso! Podes fazer login.')
            return redirect('login')  
    else:
        form = UserRegisterForm()
    return render(request, 'blog/register.html', {'form': form})

def post_list(request):
    posts = Post.objects.all().order_by('title')
    
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

@login_required
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
        return render(request, 'blog/new_post.html', {'form': form, 'post': post})
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
    
    comments = post.comments.all() 
    
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
        'comment_form': comment_form
    })