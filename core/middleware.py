import logging

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse

logger = logging.getLogger("growmore.security")


class LoginRateLimitMiddleware:
    """Small session/IP based throttle for auth endpoints."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST" and request.path in {"/accounts/login/", "/accounts/register/"}:
            ip_address = self._client_ip(request)
            key = f"login-rate:{ip_address}:{request.path}"
            attempts = cache.get(key, 0)
            if attempts >= settings.LOGIN_RATE_LIMIT_ATTEMPTS:
                logger.warning("Rate limit exceeded for %s on %s", ip_address, request.path)
                return HttpResponse("Too many attempts. Please wait and try again.", status=429)
            cache.set(key, attempts + 1, settings.LOGIN_RATE_LIMIT_WINDOW)
        return self.get_response(request)

    @staticmethod
    def _client_ip(request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")


class SuspiciousActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        honeypot = request.POST.get("website", "")
        if request.method == "POST" and honeypot:
            logger.warning("Blocked honeypot submission from %s", request.META.get("REMOTE_ADDR"))
            return HttpResponse("Request blocked.", status=429)
        return self.get_response(request)
