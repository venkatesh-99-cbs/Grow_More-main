# Production Deployment Guide - Grow More Fashion E-Commerce

## 1. Pre-Deployment Checklist

### Security Hardening

- [ ] Set `DEBUG = False` in production settings
- [ ] Configure `ALLOWED_HOSTS` with your domain(s)
- [ ] Set secure `SECRET_KEY` (use environment variable)
- [ ] Enable HTTPS everywhere with `SECURE_SSL_REDIRECT = True`
- [ ] Set `SESSION_COOKIE_SECURE = True` and `CSRF_COOKIE_SECURE = True`
- [ ] Configure `SECURE_HSTS_SECONDS = 31536000` (1 year)
- [ ] Set `SECURE_BROWSER_XSS_FILTER = True`
- [ ] Enable `X_FRAME_OPTIONS = 'DENY'` to prevent clickjacking
- [ ] Configure Content Security Policy headers
- [ ] Add rate limiting middleware
- [ ] Implement CORS properly (if API is public)

### Database & Environment

- [ ] Set up PostgreSQL Neon database with SSL
- [ ] Test database connection with `python manage.py dbshell`
- [ ] Create all environment variables (.env file)
- [ ] Backup and migrate data from SQLite if needed
- [ ] Run migrations: `python manage.py migrate --no-input`
- [ ] Collect static files: `python manage.py collectstatic --no-input`
- [ ] Test file uploads to Cloudinary

### Application Health

- [ ] Run `python manage.py check --deploy`
- [ ] Test email backend (SMTP configuration)
- [ ] Verify all external services (Razorpay, Google OAuth, Cloudinary)
- [ ] Test payment gateway in sandbox mode
- [ ] Verify email templates render correctly
- [ ] Test user authentication flows
- [ ] Run security audit: `python manage.py check --deploy --fail-level WARNING`

## 2. Environment Configuration

### Required Environment Variables

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key-here
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:password@neon-hostname/dbname?sslmode=require

# Security
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# AWS/Cloudinary (Optional for Media)
USE_CLOUDINARY=True
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Payment Gateway
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
RAZORPAY_MODE=live  # or 'sandbox' for testing

# OAuth (Google)
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret

# Render/Hosting Platform
PORT=8000
WORKER_CLASS=sync
```

## 3. Database Configuration (PostgreSQL Neon)

### Initial Setup

```bash
# Install PostgreSQL client
pip install psycopg2-binary dj-database-url

# Test connection
python manage.py dbshell

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Connection String Format

```
postgresql://username:password@hostname/database_name?sslmode=require
```

### Connection Pooling (Neon)

```python
# In settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
            'connect_timeout': 10,
        },
        'ATOMIC_REQUESTS': False,
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}
```

## 4. Email Configuration

### Gmail SMTP Setup

1. Enable 2-Factor Authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use app password instead of actual password

### SendGrid Configuration

```python
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
```

### AWS SES Configuration

```python
EMAIL_BACKEND = "django_ses.SESBackend"
AWS_SES_REGION_NAME = "us-east-1"
AWS_SES_REGION_ENDPOINT = "email.us-east-1.amazonaws.com"
```

## 5. Static Files & Media Management

### Cloudinary Setup

```python
# settings.py
if os.environ.get('USE_CLOUDINARY'):
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api

    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
        'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
    }

    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    STATIC_URL = '/static/'
    STATICFILES_STORAGE = 'cloudinary_storage.storage.StaticHashedCloudinaryStorage'
```

### Render Platform Deployment

1. Static files are collected at build time
2. Cloudinary handles media uploads
3. Configure build command: `python manage.py collectstatic --no-input && python manage.py migrate`

## 6. Security Headers & Middleware

### Add to settings.py

```python
MIDDLEWARE = [
    # ... existing middleware ...
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.gzip.GZipMiddleware',  # Enable compression
]

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "'unsafe-inline'", "cdnjs.cloudflare.com"),
    "style-src": ("'self'", "'unsafe-inline'", "fonts.googleapis.com"),
    "img-src": ("'self'", "data:", "https:", "*.cloudinary.com"),
    "font-src": ("'self'", "fonts.gstatic.com"),
    "connect-src": ("'self'", "api.razorpay.com"),
}

X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

## 7. Rate Limiting & DDoS Protection

### Using django-ratelimit

```bash
pip install django-ratelimit
```

```python
# In views.py
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h', method='GET')
def view_name(request):
    pass
```

## 8. Monitoring & Logging

### Sentry Configuration (Error Tracking)

```bash
pip install sentry-sdk
```

```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False,
    environment=os.environ.get("ENVIRONMENT", "development"),
)
```

### Logging Configuration

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/app.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

## 9. Performance Optimization

### Caching

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'grow_more',
        'TIMEOUT': 300,  # 5 minutes
    }
}
```

### Database Query Optimization

- Use `select_related()` for ForeignKey relationships
- Use `prefetch_related()` for ManyToMany relationships
- Add database indexes on frequently queried fields
- Use `only()` and `defer()` to limit field selection

### Asset Optimization

- Enable compression: `MIDDLEWARE += ['django.middleware.gzip.GZipMiddleware']`
- Use CloudinaryStorage for automatic image optimization
- Minify CSS and JavaScript
- Enable browser caching headers

## 10. Backup & Recovery

### Database Backups

```bash
# PostgreSQL automated backup (Neon handles this)
# Manual backup:
pg_dump $DATABASE_URL > backup.sql

# Restore:
psql $DATABASE_URL < backup.sql
```

### Media Files Backup

- Cloudinary automatically maintains versions
- Enable version control: `CLOUDINARY_STORAGE['VERSION']`

## 11. Monitoring & Uptime

### Health Check Endpoint

```python
# urls.py
path('health/', views.health_check, name='health_check'),
```

```python
# views.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        return JsonResponse({'status': 'healthy'}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=503)
```

### Performance Monitoring

- Use Render's built-in monitoring
- Set up uptime monitoring with services like Uptime Robot
- Configure alerting for errors and performance issues

## 12. Render Deployment

### render.yaml Configuration

```yaml
services:
  - type: web
    name: grow-more
    env: python
    plan: standard
    buildCommand: "pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate"
    startCommand: "gunicorn growmore.wsgi:application"
    envVars:
      - key: DEBUG
        value: false
      - key: ENVIRONMENT
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: grow-more-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: grow-more-cache
          property: connectionString

  - type: pserv
    name: grow-more-cache
    env: redis
    plan: free
    ipWhitelist: []

databases:
  - name: grow-more-db
    engine: postgres
    version: "15"
    plan: standard
```

### Deployment Steps

1. Push code to GitHub
2. Link repository to Render
3. Configure environment variables in Render dashboard
4. Deploy: Push to main branch
5. Monitor deployment logs
6. Test in production

## 13. Post-Deployment Verification

### Checklist

- [ ] Homepage loads without errors
- [ ] Product pages render correctly
- [ ] Authentication works (login/signup/OAuth)
- [ ] Add to cart functionality works
- [ ] Checkout process completes
- [ ] Email confirmation received
- [ ] Admin panel accessible
- [ ] Redirects to HTTPS
- [ ] Static files load correctly
- [ ] Images load from Cloudinary
- [ ] No 404/500 errors in logs
- [ ] Database connection stable
- [ ] Payment gateway test transaction succeeds

### SSL Certificate

- Render provides free SSL certificates
- Auto-renewal enabled
- Verify HTTPS redirect working

## 14. Regular Maintenance

### Weekly

- Check error logs
- Monitor database size
- Verify backups completed
- Test email delivery

### Monthly

- Security updates
- Performance review
- Cost analysis
- User feedback

### Quarterly

- Security audit
- Database optimization
- Cache invalidation
- Dependency updates

## 15. Rollback Procedure

In case of critical issues:

```bash
# Render: View deployment history
# Select previous stable version
# Click "Deploy"

# Manual rollback:
git revert HEAD
git push origin main
```

## Troubleshooting

### Common Issues

**Database Connection Errors**

- Verify DATABASE_URL format
- Check IP whitelist on Neon
- Test with `python manage.py dbshell`

**Static Files Not Loading**

- Run `python manage.py collectstatic --clear --no-input`
- Verify STATIC_ROOT and STATICFILES_DIRS
- Check S3/Cloudinary configuration

**Email Not Sending**

- Verify EMAIL_HOST_USER and PASSWORD
- Check firewall rules for SMTP port
- Review email logs in Django admin

**Payment Gateway Failures**

- Verify RAZORPAY_KEY_ID and SECRET
- Check API key permissions
- Test in sandbox mode first

**Performance Issues**

- Check slow query logs
- Enable database query caching
- Review N+1 query problems
- Optimize asset delivery

---

**Last Updated:** 2026
**Status:** Production Ready ✓
