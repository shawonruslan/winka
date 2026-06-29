from camoufox.sync_api import Camoufox
import time

EMAIL = "jahiskeina@gmail.com"
PASSWORD = "Shawon63@"

print("🚀 Starting Camoufox...")

with Camoufox(
    headless=False,
    humanize=True,
    geoip=True,
    os="windows",
    window=(1280, 720),
) as browser:
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        device_scale_factor=1,
    )
    page = context.new_page()

    print("📄 Loading Google sign-in...")
    page.goto('https://accounts.google.com/', wait_until='domcontentloaded')
    time.sleep(5)

    # ===== STEP 1: Email =====
    print("⌨️  Filling email...")
    email_input = page.locator('input#identifierId')
    email_input.wait_for(state='visible', timeout=15000)
    email_input.click()
    time.sleep(1)
    email_input.fill(EMAIL)
    time.sleep(2)

    print("↩️  Submitting email...")
    email_input.press('Enter')

    print("⏳ Waiting for password page...")
    time.sleep(6)
    page.screenshot(path='after_email.png', full_page=True)
    print(f"📍 URL after email: {page.url}")

    # ===== STEP 2: Password =====
    print("⌨️  Looking for password field...")
    password_input = page.locator('input[name="Passwd"]')
    try:
        password_input.wait_for(state='visible', timeout=20000)
        print("✅ Password field found")

        password_input.click()
        time.sleep(1)
        password_input.fill(PASSWORD)
        time.sleep(2)

        print("↩️  Submitting password...")
        password_input.press('Enter')

        time.sleep(10)
        page.screenshot(path='after_password.png', full_page=True)
        print(f"📍 Final URL: {page.url}")
        print(f"📄 Final title: {page.title()}")

    except Exception as e:
        print(f"❌ Password step failed: {e}")
        page.screenshot(path='password_error.png', full_page=True)
        print(f"📍 URL at failure: {page.url}")
        print(f"📄 Title at failure: {page.title()}")

    time.sleep(3)

print("✅ Done")
