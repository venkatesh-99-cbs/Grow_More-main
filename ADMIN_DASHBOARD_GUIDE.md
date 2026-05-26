# Grow More Admin Dashboard Guide

This guide explains how to operate the Grow More dashboard professionally, keep catalog data clean, and prepare the project for production deployment.

## Access And Daily Workflow

1. Sign in with a staff or superuser account.
2. Open `/dashboard/`.
3. Review the Overview first: product count, active offers, orders, customers, and paid revenue.
4. Process work in this order: Orders, Products, Categories, Offers, Homepage.
5. Keep one browser tab for the storefront open so you can verify customer-facing changes immediately after saving.

## Products

Use Products for all customer-facing product records.

- Add Product: create a new item with category, description, pricing, stock, sizes, colors, and images.
- Edit: update details, pricing, stock, visibility, featured status, trending status, and gallery images.
- Remove: deletes the product when it is safe to delete. If the product is already part of order history, the dashboard hides it from the storefront instead so historical orders remain accurate.
- Visibility: use `is_active` to hide products that are out of season, discontinued, or not ready for sale.
- Stock: update stock before launching offers to avoid overselling.

Recommended practice: use clear product names, concise descriptions, real product images, accurate colors/sizes, and review the product page after each update.

## Categories

Use Categories to organize the storefront and make browsing easier.

- Add Category: create a new collection or product group.
- Edit: update name, slug, description, activity status, and sort order.
- Remove: deletes unused categories. If products still use the category, the dashboard hides it instead.
- Sort Order: lower numbers appear earlier where category ordering is used.

Recommended practice: keep category names short, avoid duplicate meanings, and hide seasonal categories instead of renaming them into unrelated categories.

## Orders

Use Orders as the operational center for fulfillment.

- Update status as each order moves through Pending, Confirmed, Shipped, and Delivered.
- Download Payment Receipt when the customer or internal accounting needs proof of payment.
- Download Shipping Sheet for packing and dispatch. The sheet includes address, products, size/color, quantity, and dispatch fields.
- Never remove product records just to clean reports. The dashboard preserves order history for customer support and accounting.

Recommended practice: update status immediately after each fulfillment step and keep payment receipts matched to Razorpay records.

## Customers

Use Customers to review customer profiles, saved address counts, and recent product order history.

- Check the customer row before responding to support requests.
- Use recent products to confirm what the customer purchased without opening every order.
- For full details, open the customer-facing order detail page from the profile flow.

Recommended practice: verify customer email, phone, order number, and product list before making support decisions.

## Homepage And Offers

Use Homepage and Offers to control marketing content.

- Keep hero banners seasonal and image-led.
- Use offers for real campaigns with accurate dates, discount percentages, and product/category targeting.
- Test offer countdowns and product prices after saving.

Recommended practice: schedule campaigns before publishing and remove expired campaign messaging quickly.

## Branding

The site header, admin sidebar, and generated PDFs use the Grow More logo at:

`media/products/main/Grow_More_logo.png`

For production, upload the same brand asset to Cloudinary or keep it in the media storage configured for the deployment.

## Deployment And Infrastructure Stack

Purpose -> Service

- Django Hosting -> Render
- Database -> Neon PostgreSQL
- Images And Media -> Cloudinary
- Source Code -> GitHub
- CDN And Security -> Cloudflare

## Production Deployment Process

1. Push the latest code to GitHub.
2. Create a Neon PostgreSQL database and copy the pooled `DATABASE_URL`.
3. Create a Cloudinary account and copy `CLOUDINARY_URL`.
4. Create a Render Web Service connected to the GitHub repository.
5. Use the repository `render.yaml`, or configure manually:
   - Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - Start Command: `gunicorn growmore.wsgi:application`
6. Set Render environment variables from `.env.example`.
7. Add the Render domain and custom Cloudflare domain to `ALLOWED_HOSTS`.
8. Add the exact HTTPS origins to `CSRF_TRUSTED_ORIGINS`.
9. In Cloudflare, point the domain to Render, enable HTTPS, and keep proxy protection enabled.
10. After deploy, create a superuser, upload test media, place a test order, download a payment receipt, and download a shipping sheet.

## Production Checks Before Launch

- `DEBUG=False`
- Strong `SECRET_KEY`
- Neon `DATABASE_URL` includes SSL
- `USE_CLOUDINARY=True`
- `CLOUDINARY_URL` is set
- Render host and Cloudflare domain are in `ALLOWED_HOSTS`
- Cloudflare HTTPS is active
- Razorpay live keys are set
- Staff account can add/edit/remove Products and Categories
- Customer profile shows products under Order History
- Payment Receipt PDF downloads successfully
- Shipping Sheet PDF downloads successfully
