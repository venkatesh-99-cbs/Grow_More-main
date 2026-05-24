# Grow More - Setup, Testing & Deployment Guide

## 🎯 What Has Been Built

### Phase 1: Dynamic Frontend-Backend Synchronization ✅

- **11 API Endpoints** for dynamic content loading
- **Homepage dynamic rendering** - all content from database
- **Hero banners** - automatic carousel
- **Product cards** - CSS-styled with proper structure
- **Product offers** - countdown timers and discount display
- **Category filtering** - all categories from database

### Phase 2: Admin Dashboard & PDF Generation ✅

- **Invoice PDF generation** with reportlab
- **Delivery sheet PDF generation** - printer-friendly
- **Admin invoice download** in orders management
- **Customer invoice downloads** in order detail page
- **Styled admin dashboard** with action buttons
- **Proper order management UI**

### Phase 3: Authentication & OAuth ✅

- **Google OAuth integration** via django-allauth
- **Improved login page** with Google sign-in option
- **Improved register page** with Google sign-up option
- **Custom OAuth adapters** for user creation
- **Session security** fully configured

### Phase 4: Styling Fixes ✅

- **Product card styling** - matches frontend design
- **Login/register forms** - professional styling
- **Admin UI improvements** - invoice download buttons
- **Order detail page** - enhanced layout with download options

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
cd Grow_More-main

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env with your settings
```

**Minimum .env configuration:**

```env
DEBUG=True
SECRET_KEY=your-very-secret-key-min-50-chars
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for dev)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Razorpay (optional for dev)
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=test_secret

# Google OAuth (optional for dev)
GOOGLE_OAUTH_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=secret
```

### 3. Setup Database

```bash
# Run migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
# Follow prompts to create admin user

# (Optional) Load demo products
python manage.py seed_store
```

### 4. Run Development Server

```bash
python manage.py runserver
```

Access:

- **Frontend**: http://localhost:8000
- **Admin Dashboard**: http://localhost:8000/dashboard/
- **Django Admin**: http://localhost:8000/admin/

---

## ✅ Testing Checklist

### Frontend Tests

**Homepage**

- [ ] Visit http://localhost:8000
- [ ] Check hero banner loads from API
- [ ] Verify featured products display
- [ ] Verify deal products section appears
- [ ] Check product card styling
- [ ] Click product card to view detail

**Product Pages**

- [ ] Visit product detail page
- [ ] Check product gallery images
- [ ] Check sizes and colors display
- [ ] Check offer countdown timer (if active)
- [ ] Verify add-to-cart works

**Auth Pages**

- [ ] Visit /accounts/login/ - check styling
- [ ] Check Google OAuth button appears
- [ ] Visit /accounts/register/ - check styling
- [ ] Verify form inputs styled correctly

**Shopping Flow**

- [ ] Add product to cart
- [ ] View cart (icon should update)
- [ ] Go to checkout
- [ ] Login (test email/password)
- [ ] Test Google OAuth login (optional)

### Admin Dashboard Tests

**Products**

- [ ] Go to /dashboard/
- [ ] Navigate to Products section
- [ ] Add new product with images
- [ ] Edit existing product
- [ ] Verify product appears on frontend

**Homepage**

- [ ] Go to Homepage section
- [ ] Add hero banner with image
- [ ] Verify banner appears on homepage
- [ ] Verify banner order works

**Offers**

- [ ] Create new promotional offer
- [ ] Set start/end times
- [ ] Apply to products/categories
- [ ] Verify offer appears on product cards
- [ ] Test countdown timer

**Orders**

- [ ] Create test order (manually or through checkout)
- [ ] View orders in dashboard
- [ ] Check "Download Invoice" button
- [ ] Check "Download Delivery Sheet" button
- [ ] Download PDF files
- [ ] Verify PDF content is correct

### API Endpoint Tests

Open your browser and test each endpoint:

```
GET /api/hero-banners/
GET /api/products/
GET /api/products/1/
GET /api/products/1/offer/
GET /api/offers/active/
GET /api/categories/
GET /api/featured-products/
GET /api/deal-products/
GET /api/homepage/sections/
```

Each should return JSON data. Example response:

```json
{
  "banners": [
    {
      "id": 1,
      "title": "Summer Collection",
      "subtitle": "New arrivals",
      "image": "/media/hero/banner.jpg",
      "button_label": "Shop Now",
      "button_url": "/shop/"
    }
  ]
}
```

### PDF Generation Tests

**Generate Invoice**

```python
python manage.py shell

from orders.models import Order
from orders.services import generate_order_invoice_pdf

order = Order.objects.first()
if order:
    pdf = generate_order_invoice_pdf(order)
    with open('test_invoice.pdf', 'wb') as f:
        f.write(pdf.getvalue())
    print("Invoice saved!")
```

**Generate Delivery Sheet**

```python
from orders.services import generate_delivery_sheet_pdf

order = Order.objects.first()
if order:
    pdf = generate_delivery_sheet_pdf(order)
    with open('test_sheet.pdf', 'wb') as f:
        f.write(pdf.getvalue())
    print("Sheet saved!")
```

---

## 🔑 Google OAuth Setup

### Step 1: Create Google Cloud Project

1. Go to https://console.cloud.google.com
2. Create new project: "Grow More"
3. Enable "Google+ API"

### Step 2: Create OAuth Credentials

1. Go to "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. Choose "Web application"
4. Add authorized JavaScript origins:
   - http://localhost:8000
   - https://yourdomain.com
5. Add authorized redirect URIs:
   - http://localhost:8000/accounts/google/login/callback/
   - https://yourdomain.com/accounts/google/login/callback/

### Step 3: Configure Django

1. Copy Client ID and Secret
2. Add to `.env`:
   ```env
   GOOGLE_OAUTH_CLIENT_ID=xxxxx.apps.googleusercontent.com
   GOOGLE_OAUTH_CLIENT_SECRET=secret
   ```
3. In Django Admin (/admin/):
   - Go to Sites and set domain to `localhost:8000`
   - Go to Social Applications
   - Add Google app with Client ID and Secret

### Step 4: Test OAuth

1. Visit /accounts/login/
2. Click "Continue with Google"
3. Sign in with your Google account
4. Verify user is created and logged in

---

## 💳 Razorpay Payment Testing

### Step 1: Get Test Credentials

1. Create account at https://razorpay.com
2. Go to Settings → API Keys
3. Copy Test Key ID and Secret

### Step 2: Configure Django

```env
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=test_secret
RAZORPAY_CURRENCY=INR
```

### Step 3: Test Payment Flow

1. Add products to cart
2. Go to checkout
3. Select Razorpay payment
4. Use test card: `4111 1111 1111 1111`
   - Any future expiry
   - Any CVV
5. Verify payment success

---

## 🏗️ Production Deployment

### Pre-Deployment Checklist

```bash
# 1. Update environment
DEBUG=False
SECRET_KEY=<generate-new-secure-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# 2. Collect static files
python manage.py collectstatic --noinput

# 3. Run migrations
python manage.py migrate --settings=growmore.settings

# 4. Test in production mode
python manage.py runserver --settings=growmore.settings

# 5. Create superuser
python manage.py createsuperuser --settings=growmore.settings
```

### Deploy to Render

1. Push code to GitHub
2. Create new Web Service on Render
3. Select Python environment
4. Build command:
   ```
   pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
   ```
5. Start command:
   ```
   gunicorn growmore.wsgi:application
   ```
6. Add environment variables in Render dashboard
7. Deploy

### Deploy to Railway

1. Connect GitHub repo to Railway
2. Railway auto-detects Django
3. Set environment variables
4. Deploy

---

## 🔍 Troubleshooting

### Homepage Products Not Loading

**Problem**: Featured products section shows "Loading..." but products don't appear

**Solution**:

1. Check browser console for JavaScript errors
2. Visit `/api/featured-products/` to verify API works
3. Check if products are marked as `is_active=True` and `is_featured=True`
4. Ensure static JS files are loading

```bash
# Check Django logs
tail -f /path/to/logs/django.log

# Check API response
curl http://localhost:8000/api/featured-products/
```

### PDF Download Returns Error

**Problem**: "PDF generation is not available"

**Solution**:

1. Verify reportlab is installed: `pip list | grep reportlab`
2. Check if order has items: Order must have related OrderItem objects
3. Test generation manually:
   ```python
   python manage.py shell
   from orders.models import Order
   from orders.services import generate_order_invoice_pdf
   order = Order.objects.first()
   pdf = generate_order_invoice_pdf(order)
   print(pdf)  # Should be BytesIO object
   ```

### Google OAuth Not Working

**Problem**: "Client ID not valid" error

**Solution**:

1. Verify credentials in `.env`
2. Check Site domain in Django Admin matches your domain
3. Verify redirect URIs in Google Cloud Console
4. Check Social Applications configuration in Django Admin
5. Test with: `python manage.py shell`

```python
from allauth.socialaccount.models import SocialApp
app = SocialApp.objects.get(provider='google')
print(app.client_id)
```

### Static Files Not Loading in Production

**Problem**: CSS/JS not loading, 404 errors

**Solution**:

1. Collect static files: `python manage.py collectstatic --noinput`
2. Check STATIC_URL and STATIC_ROOT in settings
3. Configure web server (Nginx/Apache) to serve `/static/` directory
4. For Render/Railway, staticfiles should auto-collect

---

## 📚 API Documentation

### GET /api/hero-banners/

Returns active hero banners for carousel

**Response:**

```json
{
  "banners": [
    {
      "id": 1,
      "title": "Summer Collection",
      "subtitle": "...",
      "image": "/media/hero/banner.jpg",
      "button_label": "Shop Now",
      "button_url": "/shop/"
    }
  ]
}
```

### GET /api/products/?featured=true&limit=4

Returns products with filters

**Query Params:**

- `featured=true` - Only featured products
- `trending=true` - Only trending products
- `category=shirts` - Filter by category slug
- `limit=20` - Limit results

### GET /api/offers/active/

Returns currently active promotional offers

**Response:**

```json
{
  "offers": [
    {
      "id": 1,
      "title": "Summer Sale",
      "discount_percent": 30,
      "countdown_end": "2026-05-30T23:59:59Z",
      "image": "/media/offers/summer.jpg"
    }
  ]
}
```

---

## 🎨 Customization

### Change Brand Colors

Edit `static/css/styles.css`:

```css
:root {
  --primary-color: #0066cc;
  --secondary-color: #51e2f5;
  --text-color: #1a1a1a;
  /* ... */
}
```

### Change Homepage Title

Edit `templates/core/home.html`:

```html
<h1>Your New Title Here</h1>
```

### Add Custom Fonts

Edit `templates/base.html`:

```html
<link
  href="https://fonts.googleapis.com/css2?family=Your+Font:wght@400;600&display=swap"
  rel="stylesheet"
/>
```

### Customize Invoice Template

Edit `orders/services.py` in `generate_order_invoice_pdf()` function:

```python
# Change colors, fonts, layout
# Add company logo
# Add custom footer text
```

---

## 📞 Support & Resources

- Django Docs: https://docs.djangoproject.com/en/6.0/
- Razorpay Docs: https://razorpay.com/docs/
- Google OAuth: https://developers.google.com/identity
- Render Deploy: https://render.com/docs
- Railway Deploy: https://docs.railway.app

---

## 📝 Important Notes

1. **Always use `.env`** for sensitive data (never commit credentials)
2. **Enable HTTPS in production** - set `SECURE_SSL_REDIRECT=True`
3. **Back up database regularly** - especially before deployments
4. **Monitor error logs** - set up email alerts for critical errors
5. **Test thoroughly** before deploying to production
6. **Update dependencies regularly** - security patches are important

---

**Happy Building! 🚀**

For any issues or questions, check the Django documentation or reach out for support.
