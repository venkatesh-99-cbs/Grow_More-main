from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from accounts.forms import AddressForm, LoginForm, ProfileForm, RegisterForm
from accounts.models import Address
from core.services import send_welcome_email
from orders.services import merge_session_cart_into_user


class GrowMoreLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        merge_session_cart_into_user(self.request)
        response = super().form_valid(form)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = " ".join([error for field in form for error in field.errors])
            if not errors:
                errors = " ".join([error for error in form.non_field_errors()])
            return JsonResponse({'success': False, 'errors': errors or 'Invalid credentials'}, status=400)
        return super().form_invalid(form)


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")
    form = RegisterForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
            merge_session_cart_into_user(request)
            send_welcome_email(user)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            messages.success(request, "Welcome to Grow More.")
            return redirect("accounts:profile")
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = " ".join([error for field in form for error in field.errors])
                return JsonResponse({'success': False, 'errors': errors or 'Registration failed'}, status=400)
            if form.errors:
                messages.error(request, "Registration Error - " + "; ".join(form.errors.values()))

    return render(request, "accounts/register.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("core:home")


@login_required
def profile(request):
    profile_form = ProfileForm(request.POST or None, instance=request.user)
    address_form = AddressForm()
    if request.method == "POST" and request.POST.get("form_type") == "profile" and profile_form.is_valid():
        profile_form.save()
        messages.success(request, "Profile updated.")
        return redirect("accounts:profile")
    addresses = request.user.addresses.all()
    orders = request.user.orders.prefetch_related("items__product", "payment").all()[:10]
    return render(
        request,
        "accounts/profile.html",
        {"profile_form": profile_form, "address_form": address_form, "addresses": addresses, "orders": orders},
    )


@login_required
@require_POST
def add_address(request):
    form = AddressForm(request.POST)
    if form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.save()
        messages.success(request, "Address saved.")
    else:
        messages.error(request, "Please check the address details.")
    return redirect("accounts:profile")


@login_required
@require_POST
def delete_address(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, "Address removed.")
    return redirect("accounts:profile")

# Create your views here.

