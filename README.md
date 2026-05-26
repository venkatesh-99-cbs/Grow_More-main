# Grow More Django Commerce

Premium men’s fashion e-commerce monolith built with Django templates, SQLite by default, Razorpay-ready checkout, custom staff dashboard, and the original Grow More frontend style preserved.

## Local setup

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_store
python manage.py createsuperuser
python manage.py runserver
```

## Production notes

Set `DEBUG=False`, a strong `SECRET_KEY`, HTTPS `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, Razorpay keys, Neon `DATABASE_URL`, and Cloudinary `CLOUDINARY_URL` in the host environment. The recommended production stack is Render, Neon PostgreSQL, Cloudinary, GitHub, and Cloudflare.

See `ADMIN_DASHBOARD_GUIDE.md` for dashboard operations and the deployment checklist.
