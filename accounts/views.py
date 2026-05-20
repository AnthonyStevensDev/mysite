from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UsageTracking


def register_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validation checks
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html', {
    'submitted_username': username,
    'submitted_email': email,
})

        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'accounts/register.html', {
    'submitted_username': username,
    'submitted_email': email,
})

        if User.objects.filter(username=username).exists():
            messages.error(request, 'That username is already taken.')
            return render(request, 'accounts/register.html', {
    'submitted_username': username,
    'submitted_email': email,
})

        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with that email already exists.')
            return render(request, 'accounts/register.html', {
    'submitted_username': username,
    'submitted_email': email,
})

        # Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        # Create their usage tracking record
        UsageTracking.objects.create(user=user)

        # Log them in automatically after registering
        login(request, user)
        messages.success(request, f'Welcome {username}! Your account has been created.')
        return redirect('/')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def profile_view(request):
    try:
        usage = UsageTracking.objects.get(user=request.user)
    except UsageTracking.DoesNotExist:
        usage = UsageTracking.objects.create(user=request.user)

    return render(request, 'accounts/profile.html', {
        'usage': usage,
    })