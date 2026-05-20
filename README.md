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

Set `DEBUG=False`, a strong `SECRET_KEY`, HTTPS `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and Razorpay keys in the host environment. SQLite is configured by default; switch `DB_ENGINE` and related variables to PostgreSQL when the store grows.
