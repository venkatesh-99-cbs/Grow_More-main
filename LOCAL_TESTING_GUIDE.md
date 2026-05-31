# Local Testing Guide for Grow More Redesign

Follow these steps to verify the new features in your local environment.

## 1. Setup Environment
```bash
# Install new dependencies
pip install PyJWT cryptography

# Apply database migrations
python3 manage.py migrate
```

## 2. Authentication & Google Login
- Click the **Login** button in the navbar. It should open a glassmorphism modal.
- Test **Sign In** and **Join Now** (Register) tabs within the modal.
- Verify that **Continue with Google** redirects to the Google OAuth page.
- *Note: For Google Login to work locally, you must configure GOOGLE_OAUTH_CLIENT_ID and SECRET in your .env.*

## 3. Shop & Filtering
- Navigate to the **Shop** page.
- Try the new filters on the sidebar: **Category**, **Brand**, **Price Range**, and **Sizes**.
- Verify that the product grid updates dynamically without a full page refresh.
- Check the **Sort By** dropdown (Featured, Price Low/High, Newest).

## 4. Product Experience
- **Color Swatches**: On product cards and detail pages, click color circles.
- **Size Selection**: Select different sizes. Notice the "Only X left" or "Out of Stock" indicators.
- **Add to Cart**: Ensure the button works and opens the cart sidebar with a success notification.
- **Favorites**: Click the heart icon. It should toggle and show a toast notification.

## 5. Homepage & Intro
- Refresh the homepage. You should see a cinematic **Intro Animation**.
- Test the **Skip** button on the intro.
- Verify the **Hero Slider** animations and the "Current Deals" section.

## 6. Admin Panel
- Go to `/admin/`.
- Check **Hero Banners**: Try creating a banner with a specific **Theme** (e.g., Luxury) and **Animation** (e.g., Scale).
- Check **Promotional Offers**: Create an offer and assign it to a specific **Brand**. Verify it applies to all products of that brand.

## 7. Email System
- Register a new account.
- Check your console (or configured email) for the **Welcome Email**.
- Complete a purchase and verify the **Order Confirmation Email**.

## 8. Security
- Try to access `/orders/shipping-sheet/<order_number>/` as a normal user. It should deny access and show an error message.

## 9. Automated Verification (Advanced)
A professional Playwright test suite has been provided to verify the core user journey.

### Requirements
```bash
pip install playwright
playwright install chromium
```

### Run Tests
```bash
# Ensure the server is running on port 8001
python3 manage.py runserver 8001 &

# Run the verification script
python3 /home/jules/verification/verify_redesign.py
```
This script will verify:
- Intro Animation removal
- Auth Modal functionality
- Shop Filter AJAX integration
- Size Selection & Stock logic
- "Add to Cart" success states
