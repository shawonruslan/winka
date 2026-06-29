from camoufox import Camoufox
import requests

URL = "https://accounts.google.com"

browser = Camoufox(headless=True)

page = browser.new_page()

page.goto(URL)

page.wait_for_load_state("networkidle")

page.screenshot(
    path="screenshot.png",
    full_page=True
)

browser.close()

# Upload to catbox
with open("screenshot.png", "rb") as f:
    r = requests.post(
        "https://catbox.moe/user/api.php",
        data={
            "reqtype": "fileupload"
        },
        files={
            "fileToUpload": f
        }
    )

print("Image URL:")
print(r.text)
