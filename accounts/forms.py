from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from accounts.models import Address


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username and User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                "An account with this username already exists.",
                code="invalid",
            )
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return email
        email = email.lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.", code="invalid")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email", "").lower()
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username or email")
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean_username(self):
        value = self.cleaned_data["username"]
        user = User.objects.filter(email__iexact=value).first()
        return user.username if user else value


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ("full_name", "phone", "address_line", "city", "state", "postal_code", "country", "is_default")
        widgets = {"address_line": forms.Textarea(attrs={"rows": 3})}

