from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(allowed_roles):
    """
    Restrict view to users whose profile.role is in allowed_roles.

    Usage:
        @login_required
        @role_required(['ADMIN', 'MANAGER'])
        def some_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            profile = getattr(request.user, 'profile', None)
            if profile is None or profile.role not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard:dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
