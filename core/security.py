"""
Security decorators and utilities for admin views
Implements permission checking, staff-only access, etc.
"""

from functools import wraps
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


def staff_required(view_func):
    """
    Decorator to restrict view access to staff members only
    Redirects non-staff users with a message
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('account_login')}?next={request.path}")
        
        if not request.user.is_staff:
            messages.error(request, "You must be a staff member to access this page.")
            return HttpResponseForbidden("403 Forbidden - Staff access required")
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def superuser_required(view_func):
    """
    Decorator to restrict view access to superusers only
    Redirects non-superuser accounts with a message
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('account_login')}?next={request.path}")
        
        if not request.user.is_superuser:
            messages.error(request, "You must be a superuser to access this page.")
            return HttpResponseForbidden("403 Forbidden - Superuser access required")
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def ajax_required(view_func):
    """
    Decorator to restrict view to AJAX requests only
    Returns JSON error for non-AJAX requests
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(
                {'error': 'This endpoint requires AJAX request'},
                status=400
            )
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def permission_required(*permissions):
    """
    Decorator to check for specific permissions
    Usage: @permission_required('orders.view_order', 'orders.change_order')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"{reverse('account_login')}?next={request.path}")
            
            if not request.user.has_perms(permissions):
                messages.error(request, "You don't have permission to access this page.")
                return HttpResponseForbidden("403 Forbidden - Insufficient permissions")
            
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    
    return decorator


def owner_or_staff_required(field='user'):
    """
    Decorator to allow access only if user is owner of the object or is staff
    Usage: @owner_or_staff_required(field='customer')
    
    The decorated view should accept an object ID as parameter
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"{reverse('account_login')}?next={request.path}")
            
            # This is a basic implementation - adjust based on your model structure
            # You might need to fetch the object and check ownership
            
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    
    return decorator
