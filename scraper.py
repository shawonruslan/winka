from camoufox.sync_api import Camoufox
import time

EMAIL = "jahiskeina@gmail.com"

print("🚀 Starting Camoufox...")

with Camoufox(
    headless=False,
    humanize=True,
    geoip=True,
    os="windows",
    screen={"width": 1280, "height": 720},
    window=(1280, 720),
) as browser:
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        device_scale_factor=1,
    )
    page = context.new_page()

    print("📄 Loading Google sign-in...")
    page.goto('https://accounts.google.com/', wait_until='domcontentloaded')
    time.sleep(4)

    print("⌨️  Filling email...")
    email_input = page.locator('input#identifierId')
    email_input.wait_for(state='visible', timeout=15000)
    email_input.click()
    time.sleep(1)
    email_input.fill(EMAIL)
    time.sleep(2)

    print("↩️  Pressing Enter...")
    email_input.press('Enter')

    time.sleep(8)
    print(f"✅ Page title after submit: {page.title()}")
    print(f"✅ Current URL: {page.url}")

    page.screenshot(path='after_email.png', full_page=True)
    print("📸 Screenshot saved")

print("✅ Done")
