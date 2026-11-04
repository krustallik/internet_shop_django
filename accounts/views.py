from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from main.models import Category
from .forms import UserRegistrationForm
from django.contrib import messages
from django.views.decorators.http import require_POST

def _nav_categories():
    return Category.objects.filter(is_active=True).order_by("name")

def register_view(request):
    if request.user.is_authenticated:
        return redirect('main:product_list')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your account is ready. Welcome to the shop.')
            return redirect('main:product_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {
        'form': form,
        'categories': _nav_categories(),
    })
def login_view(request):
    if request.user.is_authenticated:
        return redirect('main:product_list')

    next_url = request.GET.get('next') or request.POST.get('next') or ''
    form = AuthenticationForm(data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        # Only redirect to a same-host URL supplied by the request.
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect('main:product_list')

    return render(request, 'accounts/login.html', {
        'form': form,
        'next': next_url,
        'categories': _nav_categories(),
    })

@require_POST
def logout_view(request):
    logout(request)
    return redirect('main:product_list')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {
        'categories': _nav_categories(),
    })
