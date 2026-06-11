from playwright.sync_api import sync_playwright
import os

def run_cuj(page):
    # Navigate to home page
    print("Navigating to home page...")
    page.goto("http://localhost:8000")
    page.wait_for_timeout(2000)

    # Verify Hero Deal Banner
    hero_banner = page.locator(".deal-banner").first
    if hero_banner.is_visible():
        print("✅ Hero Deal Banner is visible")
    else:
        print("❌ Hero Deal Banner NOT visible")

    # Verify Popup Banner
    popup = page.locator("#deal-popup-container")
    if popup.is_visible():
        print("✅ Popup Banner is visible")
    else:
        print("❌ Popup Banner NOT visible")

    # Screenshot 1: Initial state
    page.screenshot(path="/home/jules/verification/screenshots/1_initial_state.png")
    page.wait_for_timeout(1000)

    # Close Popup Banner
    print("Closing Popup Banner...")
    page.locator(".popup-close").click()
    page.wait_for_timeout(1000)

    # Verify Floating Ball
    ball = page.locator("#floating-deal-ball")
    if ball.is_visible():
        print("✅ Floating Deal Ball appeared")
    else:
        print("❌ Floating Deal Ball NOT visible")

    # Screenshot 2: Floating Ball state
    page.screenshot(path="/home/jules/verification/screenshots/2_floating_ball.png")
    page.wait_for_timeout(1000)

    # Re-open via Ball
    print("Clicking Ball to re-open...")
    page.locator(".ball-expand").click(force=True)
    page.wait_for_timeout(1000)

    if popup.is_visible():
        print("✅ Popup Banner re-appeared")
    else:
        print("❌ Popup Banner failed to re-appear")

    # Verify Limited Badge
    badge = page.locator(".limited-badge").first
    if badge.is_visible():
        print(f"✅ Limited Badge found: {badge.text_content()}")
    else:
        print("❌ Limited Badge NOT visible")

    # Final Screenshot
    page.screenshot(path="/home/jules/verification/screenshots/verification.png")
    page.wait_for_timeout(1000)

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="/home/jules/verification/videos"
        )
        page = context.new_page()
        try:
            run_cuj(page)
        finally:
            context.close()
            browser.close()
