from camoufox.sync_api import Camoufox

with Camoufox(
    headless=True,           # works fine on GHA runners
    humanize=True,           # human-like cursor movement
    geoip=True,              # auto-match locale to proxy IP
    # proxy={'server': 'http://user:pass@host:port'},
) as browser:
    page = browser.new_page()
    page.goto('https://accounts.google.com')
    print(page.title())
