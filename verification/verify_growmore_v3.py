import asyncio
from playwright.async_api import async_playwright
import os

async def verify_growmore():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # Set viewport to desktop for initial check
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})

        # Navigate to home page
        print("Navigating to home page...")
        try:
            await page.goto('http://localhost:8000', timeout=10000)
        except Exception as e:
            print(f"Failed to navigate: {e}")
            await browser.close()
            return

        await page.wait_for_timeout(2000) # Wait for animations

        # 1. Check Popup Banner visibility
        popup = page.locator('#deal-popup-container')
        if await popup.is_visible():
            print("✅ Popup Banner is visible")
        else:
            print("❌ Popup Banner NOT visible")

        # 2. Check Deal Banner in Hero
        deal_banner = page.locator('.deal-banner').first
        if await deal_banner.is_visible():
            print("✅ Deal Banner is visible")
        else:
            print("❌ Deal Banner NOT visible")

        # 3. Check Floating Ball (should be hidden initially)
        ball = page.locator('#floating-deal-ball')
        if await ball.is_visible():
            print("❌ Floating Ball is visible initially (should be hidden)")
        else:
            print("✅ Floating Ball is hidden initially")

        # 4. Test Closing Popup
        close_btn = page.locator('.popup-close')
        if await close_btn.is_visible():
            await close_btn.click()
            await page.wait_for_timeout(1000)
            if await ball.is_visible():
                print("✅ Floating Ball appeared after closing popup")
            else:
                print("❌ Floating Ball NOT visible after closing popup")

        # 5. Check Product Badges
        badges = page.locator('.limited-badge')
        count = await badges.count()
        if count > 0:
            print(f"✅ Found {count} Limited Badges on product cards")
            # Check if text contains "Ends in"
            text = await badges.first.text_content()
            if "Ends in" in text:
                print(f"✅ Badge timer text looks correct: {text}")
            else:
                print(f"❌ Badge timer text looks wrong: {text}")
        else:
            print("❌ No Limited Badges found")

        await page.screenshot(path='verification/growmore_verify_v3.png', full_page=True)
        print("Screenshot saved to verification/growmore_verify_v3.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_growmore())
