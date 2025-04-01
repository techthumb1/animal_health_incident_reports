import asyncio
import os
from pyppeteer import launch
from pathlib import Path
import sys

# Download path setup
DOWNLOAD_PATH = str(Path(__file__).resolve().parent.parent / "data" / "wahis_exports")

async def download_wahis_excel():
    # Launch browser with robust flags
    browser = await launch(
        headless=True,
        args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            '--window-size=1920,1080',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled'
        ],
        userDataDir='/tmp/user-data-dir'
    )

    page = await browser.newPage()

    # Set viewport and user agent to mimic real browser
    await page.setViewport({'width': 1920, 'height': 1080})
    await page.setUserAgent(
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/119.0.0.0 Safari/537.36"
    )

    # Ensure download folder exists
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)

    print("Opening WAHIS site...")
    try:
        await page.goto("https://wahis.woah.org", {
            'waitUntil': 'networkidle2',
            'timeout': 60000  # Increased timeout
        })
    except Exception as e:
        print("Failed to load WAHIS:", e)
        await browser.close()
        return

    # Optional screenshot to debug rendering
    await page.screenshot({'path': 'wahis_loaded.png'})

    # Accept cookies if needed
    try:
        await page.click('button#onetrust-accept-btn-handler')
        await asyncio.sleep(2)
    except:
        print("No cookie button found or already accepted.")

    try:
        print("Waiting for export button...")
        await page.waitForSelector('button[title="Export"]', timeout=30000)

        print("Clicking export...")
        await page.click('button[title="Export"]')

        print("Waiting for download to complete...")
        await asyncio.sleep(20)  # Wait for the file to download
    except Exception as e:
        print("Export failed:", e)

    print(f"Export complete. Check the folder: {DOWNLOAD_PATH}")
    await browser.close()

if __name__ == '__main__':
    try:
        asyncio.run(download_wahis_excel())
    except RuntimeError as e:
        if "closed" in str(e) or "no current event loop" in str(e):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(download_wahis_excel())
            except Exception as inner_e:
                print("Failed to run event loop fallback:", inner_e)
                sys.exit(1)
        else:
            raise

        asyncio.set_event_loop(loop)

    loop.run_until_complete(download_wahis_excel())
