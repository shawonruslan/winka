from camoufox.sync_api import Camoufox
import time

print("🚀 Starting Camoufox...")

with Camoufox(
    headless=False,
    humanize=True,
    geoip=True,
) as browser:
    page = browser.new_page()
    page.set_viewport_size({"width": 1280, "height": 720})

    print("📄 Loading bot detection test page...")
    page.goto('https://bot.sannysoft.com', wait_until='domcontentloaded')
    time.sleep(6)

    print("📄 Loading example.com...")
    page.goto('https://accounts.google.com/', wait_until='domcontentloaded')
    time.sleep(4)

    print(f"✅ Final page title: {page.title()}")

print("✅ Done")
