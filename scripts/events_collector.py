import asyncio
import pandas as pd
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_PATH = Path("data/event_records_raw.csv")
BASE_URL = "https://wahis.woah.org/#/event-management"
MAX_PAGES = 10  # Change to 5669 after testing

async def scrape_events():
    records = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(BASE_URL, wait_until="networkidle")

    # Dismiss cookie modal
    try:
        await page.wait_for_selector('text=Cookies management preferences', timeout=8000)
        print("[✓] Cookie modal detected. Accepting cookies...")
        await page.click('text=Accept')
        await page.wait_for_timeout(5000)  # Allow table to load
    except:
        # Wait for the table to become visible
        await page.wait_for_selector("table tbody tr", timeout=60000, state="visible")
        rows = await page.query_selector_all("table tbody tr")

    for row in rows:
        cols = await row.query_selector_all("td")
        for row in rows:
            cols = await row.query_selector_all("td")
            if len(cols) < 7:
                continue

            record = {
                "country": await cols[0].inner_text(),
                "report_number": await cols[1].inner_text(),
                "disease": await cols[2].inner_text(),
                "subtype": await cols[3].inner_text(),
                "reason": await cols[4].inner_text(),
                "start_date": await cols[5].inner_text(),
                "report_date": await cols[6].inner_text(),
            }

            # Extract event ID from the external link icon
            try:
                link = await cols[-1].query_selector("a")
                href = await link.get_attribute("href")
                if "/in-event/" in href:
                    record["event_id"] = href.split("/in-event/")[1].split("/")[0]
                else:
                    record["event_id"] = None
            except:
                record["event_id"] = None

            records.append(record)

        # Move to next page
        try:
            next_btn = await page.query_selector('button[aria-label="Next page"]')
            disabled = await next_btn.get_attribute("disabled")
            if disabled:
                print("[-] Reached last page")
                break
            await next_btn.click()
            await page.wait_for_timeout(3000)
        except Exception as e:
            print(f"[-] Pagination error: {e}")
            break

        await browser.close()
        return records
        break

        await browser.close()

    return records

if __name__ == "__main__":
    result = asyncio.run(scrape_events())
    df = pd.DataFrame(result)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"[✓] Saved {len(df)} records to {OUTPUT_PATH}")
# This script scrapes event data from the WAHIS website using Playwright.
# It collects information about various events, including country, report number,
# disease, subtype, reason, start date, report date, and event ID.
# The data is saved to a CSV file for further analysis.
# The script uses asynchronous programming to handle multiple pages efficiently.
# It also includes error handling for pagination and element selection.