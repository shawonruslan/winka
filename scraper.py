from camoufox.sync_api import Camoufox
import time

with Camoufox(
    headless=False,        # IMPORTANT: must be False so Xvfb captures it
    humanize=True,
    geoip=True,
    window=(1280, 720),
) as browser:
    page = browser.new_page()
    page.goto('https://accounts.google.com/')
    time.sleep(3)
    page.goto('https://bot.sannysoft.com')
    time.sleep(5)
    print(page.title())
