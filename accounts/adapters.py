"""
Custom adapters for allauth OAuth integration.
Handles user creation and account linking during OAuth flows.
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom adapter for account creation and settings"""

    def is_open_for_signup(self, request):
        """Allow signup"""
        return True

    def save_user(self, request, sociallogin, form=None):
        """Customize user creation from social auth"""
        user = super().save_user(request, sociallogin, form)
        # Set user's name from social account
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data
            if extra_data.get('given_name'):
                user.first_name = extra_data.get('given_name')
            if extra_data.get('family_name'):
                user.last_name = extra_data.get('family_name')
            user.save()
        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter for social account integration"""

    def pre_social_login(self, request, sociallogin):
        """
        Handle case where user already exists with the email
        from the social account being linked
        """
        # Check if user with this email already exists
        if sociallogin.is_existing:
            return

        try:
            user = User.objects.get(email=sociallogin.account.extra_data.get('email'))
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass

    def save_user(self, request, sociallogin, form=None):
        """Customize user creation from social login"""
        user = super().save_user(request, sociallogin, form)
        
        # Populate user details from social account data
        extra_data = sociallogin.account.extra_data
        if extra_data:
            if extra_data.get('given_name'):
                user.first_name = extra_data.get('given_name')
            if extra_data.get('family_name'):
                user.last_name = extra_data.get('family_name')
            user.save()
        
        return user

    def populate_user(self, request, sociallogin, data):
        """Populate user instance with data from social account"""
        user = super().populate_user(request, sociallogin, data)
        if data.get('given_name'):
            user.first_name = data.get('given_name')
        if data.get('family_name'):
            user.last_name = data.get('family_name')
        return user
