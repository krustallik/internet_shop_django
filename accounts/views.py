from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from main.models import Category
from .forms import UserRegistrationForm
from django.contrib import messages

def _nav_categories():
    return Category.objects.filter(is_active=True).order_by("name")

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # змініть на вашу головну
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Реєстрація успішна! Ласкаво просимо.')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})
def login_view(request):
    if request.user.is_authenticated:
        return redirect('main:product_list')

    next_url = request.GET.get('next') or request.POST.get('next') or ''
    form = AuthenticationForm(data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        # безпечно повертаємося на next, якщо він свій
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect('main:product_list')

    return render(request, 'accounts/login.html', {
        'form': form,
        'next': next_url,
        'categories': _nav_categories(),
    })

def logout_view(request):
    logout(request)
    return redirect('main:product_list')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('main:product_list')

    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('main:product_list')

    return render(request, 'accounts/register.html', {
        'form': form,
        'categories': _nav_categories(),
    })

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {
        'categories': _nav_categories(),
    })


# --- Middleware захисту /admin/ ---

class AdminAccessRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            user = request.user
            if not user.is_authenticated or not user.is_staff:
                return redirect('main:product_list')
        return self.get_response(request)
