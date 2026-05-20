# Grow More: Local Run and Test Guide

This project is now a single Django monolith. The backend, frontend templates, static assets, database, cart, checkout, authentication, admin dashboard, and product management all run through one Django server.

## 1. Project Structure

```text
Grow_More-main/
├── accounts/          # Authentication, profile, addresses
├── core/              # Homepage, about, contact, security helpers
├── dashboard/         # Custom staff dashboard
├── orders/            # Cart, checkout, orders, payments
├── products/          # Categories, products, product pages
├── growmore/          # Django settings and root URLs
├── templates/         # Django frontend templates
├── static/            # CSS and modular JavaScript
├── media/             # Uploaded images
├── frontend/          # Old static reference frontend only
├── manage.py
├── requirements.txt
├── .env.example
└── Procfile
```

## 2. First-Time Setup

Open PowerShell inside the project folder:

```powershell
cd C:\Users\VENKATESH\OneDrive\Desktop\Grow_More-main
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create your environment file:

```powershell
copy .env.example .env
```

For local development, keep this in `.env`:

```env
DEBUG=True
SECRET_KEY=local-development-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost,testserver
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

## 3. Database Setup

Run migrations:

```powershell
python manage.py migrate
```

Seed starter Grow More products and homepage banners:

```powershell
python manage.py seed_store
```

Create an admin user:

```powershell
python manage.py createsuperuser
```

Follow the prompts for username, email, and password.

## 4. Start the Server

Start the Django development server:

```powershell
python manage.py runserver 127.0.0.1:8000
```

Open the website:

```text
http://127.0.0.1:8000/
```

Important pages:

```text
Home:              http://127.0.0.1:8000/
Shop:              http://127.0.0.1:8000/shop/
Login:             http://127.0.0.1:8000/accounts/login/
Profile:           http://127.0.0.1:8000/accounts/profile/
Custom Dashboard:  http://127.0.0.1:8000/dashboard/
Django Admin:      http://127.0.0.1:8000/admin/
```

## 5. Frontend Server

There is no separate frontend server anymore.

The frontend now runs through Django:

```text
templates/    -> Django HTML templates
static/css/   -> CSS
static/js/    -> modular JavaScript
media/        -> uploaded product and banner images
```

Use only this command during development:

```powershell
python manage.py runserver 127.0.0.1:8000
```

Do not start a separate `python -m http.server` for the old `frontend/` folder unless you only want to view the old static reference files.

## 6. Admin Dashboard Testing

Log in with the superuser account:

```text
http://127.0.0.1:8000/accounts/login/
```

Then open:

```text
http://127.0.0.1:8000/dashboard/
```

Test these dashboard flows:

1. Open `Products`
2. Add a new product
3. Upload or replace product images
4. Mark a product as featured or trending
5. Open `Homepage`
6. Add a hero banner
7. Enable or disable homepage banners
8. Open `Orders`
9. Change an order status from pending to confirmed, shipped, or delivered

The default Django admin is also available:

```text
http://127.0.0.1:8000/admin/
```

## 7. Customer Flow Testing

Open:

```text
http://127.0.0.1:8000/shop/
```

Test the customer journey:

1. Open the shop page
2. Search and filter products
3. Open a product detail page
4. Switch gallery thumbnails
5. Select size and color
6. Add product to cart
7. Open cart drawer
8. Register or log in
9. Open checkout
10. Fill shipping details
11. Select payment method
12. Place order
13. Check order history in profile

Profile page:

```text
http://127.0.0.1:8000/accounts/profile/
```

## 8. Razorpay Testing

Add Razorpay credentials to `.env`:

```env
RAZORPAY_KEY_ID=your_test_key_id
RAZORPAY_KEY_SECRET=your_test_key_secret
RAZORPAY_CURRENCY=INR
```

Restart the Django server after changing `.env`.

Then test checkout again using Razorpay test mode credentials from your Razorpay dashboard.

If Razorpay keys are empty, the app still creates a pending order safely, but live Razorpay checkout will not open.

## 9. Quick Health Checks

Run Django system checks:

```powershell
python manage.py check
```

Run migrations status:

```powershell
python manage.py showmigrations
```

Open Django shell:

```powershell
python manage.py shell
```

Check product API in browser:

```text
http://127.0.0.1:8000/api/products/
```

Expected result: JSON containing product data.

## 10. Static and Media Files

During local development, Django serves static and media files automatically while `DEBUG=True`.

Production static collection:

```powershell
python manage.py collectstatic
```

Uploaded images go into:

```text
media/
```

Do not commit real production customer uploads unless you intentionally want them in the repository.

## 11. Common Problems

### Server says port 8000 is already in use

Start on another port:

```powershell
python manage.py runserver 127.0.0.1:8001
```

Then open:

```text
http://127.0.0.1:8001/
```

### CSS or JavaScript not updating

Hard refresh the browser:

```text
Ctrl + F5
```

Also confirm `DEBUG=True` in `.env`.

### Dashboard redirects to login

You must log in with a staff or superuser account.

Create one:

```powershell
python manage.py createsuperuser
```

### Product images are broken

Check one of these:

1. The product has an uploaded image in dashboard
2. The product has an external image URL
3. `MEDIA_URL` and `MEDIA_ROOT` are configured
4. The server is running with `DEBUG=True` locally

### Cart add fails

Run:

```powershell
python manage.py check
```

Then confirm the page has a CSRF cookie by refreshing the browser once and trying again.

## 12. Production Preparation

Before deploying to Render or Railway:

Set these environment variables in the hosting dashboard:

```env
DEBUG=False
SECRET_KEY=strong-production-secret
ALLOWED_HOSTS=your-domain.com,your-app.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://your-app.onrender.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
RAZORPAY_KEY_ID=your_live_or_test_key
RAZORPAY_KEY_SECRET=your_live_or_test_secret
```

Deployment command from `Procfile`:

```text
python manage.py migrate && python manage.py collectstatic --noinput && gunicorn growmore.wsgi:application
```

## 13. Daily Development Commands

Start work:

```powershell
cd C:\Users\VENKATESH\OneDrive\Desktop\Grow_More-main
.\.venv\Scripts\Activate.ps1
python manage.py runserver 127.0.0.1:8000
```

After model changes:

```powershell
python manage.py makemigrations
python manage.py migrate
```

After resetting starter catalog data:

```powershell
python manage.py seed_store
```

Before committing or deploying:

```powershell
python manage.py check
python manage.py collectstatic --noinput
```

