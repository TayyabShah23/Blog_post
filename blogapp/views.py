from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Blog, Category
from .forms import BlogForm
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login as auth_login 
from django.contrib.auth.models import User,Permission
from django.contrib.contenttypes.models import ContentType


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.save()

            # ✅ Assign blog permissions
            content_type = ContentType.objects.get_for_model(Blog)
            permissions = Permission.objects.filter(content_type=content_type)
            user.user_permissions.set(permissions)
            auth_login(request, user)  # ✅ Correct login method
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def home(request):
    blog_list = Blog.objects.all().order_by('-created_at')
    paginator = Paginator(blog_list, 6)  # 6 blogs per page
    page = request.GET.get('page')
    blogs = paginator.get_page(page)
    return render(request, 'home.html', {'blogs': blogs})

def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, 'blog_detail.html', {'blog': blog})

def categories(request):
    categories = Category.objects.all()
    return render(request, 'categories.html', {'categories': categories})

def category_blogs(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    blog_list = Blog.objects.filter(category=category).order_by('-created_at')

    paginator = Paginator(blog_list, 8)  # Show 8 blogs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'category_blogs.html', {
        'category': category,
        'page_obj': page_obj
    })
    
@login_required(login_url='login')  # Redirects to login page if not logged in
def create_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user  # Assign logged-in user as author
            blog.save()
            return redirect('home')
    else:
        form = BlogForm()
    return render(request, 'create_blog.html', {'form': form})

@login_required
def edit_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id, author=request.user)
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('blog_detail', blog.id)
    else:
        form = BlogForm(instance=blog)
    return render(request, 'Edit_blog.html', {'form': form, 'blog': blog})

@login_required
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id, author=request.user)
    if request.method == 'POST':
        blog.delete()
        return redirect('home')
    return render(request, 'blog_delete.html', {'blog': blog})