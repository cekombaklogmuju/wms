from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import UserRegistrationForm, UserProfileForm, LoginForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next') or 'dashboard:dashboard'
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}.')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def register_view(request):
    user_role = getattr(request.user, 'profile', None)
    if user_role is None or user_role.role not in ('ADMIN', 'MANAGER'):
        messages.error(request, 'You do not have permission to register new users.')
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            # Profile auto-created by signal; update with form data
            profile = user.profile
            profile.role = profile_form.cleaned_data['role']
            profile.warehouse = profile_form.cleaned_data['warehouse']
            profile.phone = profile_form.cleaned_data['phone']
            profile.save()
            messages.success(request, f'Account created for {user.username}.')
            return redirect('register')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()

    return render(request, 'accounts/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
def profile_view(request):
    profile = request.user.profile

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        profile_form = UserProfileForm(instance=profile)

    return render(request, 'accounts/profile.html', {
        'profile_form': profile_form,
    })
