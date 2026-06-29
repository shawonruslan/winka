from camoufox.sync_api import Camoufox
import time
import os
import re
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta, timezone

EMAIL = os.environ["GOOGLE_EMAIL"]
PASSWORD = os.environ["GOOGLE_PASSWORD"]
RECOVERY_EMAIL = os.environ["RECOVERY_EMAIL"]
RECOVERY_APP_PASSWORD = os.environ["RECOVERY_APP_PASSWORD"].replace(" ", "")


def fetch_google_otp(timeout=120, poll_interval=5):
    """Poll the recovery Gmail inbox via IMAP for a Google verification code."""
    print(f"📬 Connecting to IMAP for {RECOVERY_EMAIL}...")
    start_time = time.time()
    since_time = datetime.now(timezone.utc) - timedelta(minutes=15)

    while time.time() - start_time < timeout:
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
            mail.login(RECOVERY_EMAIL, RECOVERY_APP_PASSWORD)
            mail.select("inbox")

            date_str = since_time.strftime("%d-%b-%Y")
            status, messages = mail.search(
                None,
                f'(FROM "google.com" SINCE "{date_str}")'
            )

            if status == "OK" and messages[0]:
                ids = messages[0].split()
                for msg_id in reversed(ids):
                    status, data = mail.fetch(msg_id, "(RFC822)")
                    if status != "OK":
                        continue

                    msg = email.message_from_bytes(data[0][1])
                    msg_date = email.utils.parsedate_to_datetime(msg["Date"])
                    # Safely handle naive vs aware datetimes
                    if msg_date.tzinfo is None:
                        msg_date = msg_date.replace(tzinfo=timezone.utc)
                    if msg_date < since_time:
                        continue

                    subject_raw = decode_header(msg["Subject"])[0]
                    subject = subject_raw[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(errors="ignore")
                    sender = msg.get("From", "Unknown Sender")
                    print(f"📧 Found email: '{subject}' from '{sender}'")

                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            ctype = part.get_content_type()
                            if ctype in ("text/plain", "text/html"):
                                try:
                                    body += part.get_payload(decode=True).decode(errors="ignore")
                                except Exception:
                                    pass
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode(errors="ignore")
                        except Exception:
                            pass

                    match = re.search(r'(?:code|verification)[^0-9]{0,40}(\d{6})', body, re.IGNORECASE)
                    if not match:
                        match = re.search(r'\b(\d{6})\b', body)

                    if match:
                        code = match.group(1)
                        print(f"✅ OTP found: {code}")
                        mail.logout()
                        return code

            mail.logout()
        except Exception as e:
            print(f"⚠️  IMAP error: {e}")

        print(f"⏳ No OTP yet, waiting {poll_interval}s... ({int(time.time() - start_time)}s elapsed)")
        time.sleep(poll_interval)

    raise TimeoutError(f"❌ No OTP received within {timeout}s")


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
    email_input.press('Enter')

    time.sleep(6)
    page.screenshot(path='1_after_email.png', full_page=True)
    print(f"📍 URL after email: {page.url}")

    # ===== STEP 2: Password =====
    print("⌨️  Filling password...")
    password_input = page.locator('input[name="Passwd"]')
    password_input.wait_for(state='visible', timeout=20000)
    password_input.click()
    time.sleep(1)
    password_input.fill(PASSWORD)
    time.sleep(2)
    password_input.press('Enter')

    time.sleep(10)
    page.screenshot(path='2_after_password.png', full_page=True)
    print(f"📍 URL after password: {page.url}")

    # ===== STEP 3: OTP =====
    print("🔍 Checking if OTP challenge is shown...")

    otp_selectors = [
        'input[name="totpPin"]',
        'input[name="idvAnyPhonePin"]',
        'input[type="tel"]',
        'input#totpPin',
        'input[aria-label*="code" i]',
        'input[aria-label*="verification" i]',
    ]

    otp_input = None
    for sel in otp_selectors:
        loc = page.locator(sel).first
        try:
            loc.wait_for(state='visible', timeout=5000)
            otp_input = loc
            print(f"✅ OTP field found with selector: {sel}")
            break
        except Exception:
            continue

    if otp_input is None:
        print("ℹ️  No OTP challenge detected, skipping...")
        page.screenshot(path='3_no_otp.png', full_page=True)
    else:
        try:
            email_option = page.get_by_text(
                re.compile(r"verification code.*email|recovery email", re.IGNORECASE)
            ).first
            email_option.click(timeout=3000)
            time.sleep(3)
            print("📧 Selected email verification method")
            for sel in otp_selectors:
                loc = page.locator(sel).first
                try:
                    loc.wait_for(state='visible', timeout=5000)
                    otp_input = loc
                    break
                except Exception:
                    continue
        except Exception:
            print("ℹ️  No email option to click (probably already on email-code page)")

        print("📬 Fetching OTP from recovery inbox...")
        otp_code = fetch_google_otp(timeout=120, poll_interval=5)

        print(f"⌨️  Entering OTP: {otp_code}")
        otp_input.click()
        time.sleep(1)
        otp_input.fill(otp_code)
        time.sleep(2)
        otp_input.press('Enter')

        time.sleep(10)
        page.screenshot(path='4_after_otp.png', full_page=True)
        print(f"📍 Final URL: {page.url}")
        print(f"📄 Final title: {page.title()}")

    time.sleep(3)

print("✅ Done")
