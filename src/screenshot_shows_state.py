import pandas as pd
import os
import asyncio
import ast
import json
from playwright.async_api import async_playwright

OUTPUT_DIR = "screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def take_seat_counts_from_csv(INPUT_CSV, OUTPUT_CSV, debug=False):
    print("STARTED RUNNING")
    df = pd.read_csv(INPUT_CSV)

    results = []  # store results for all showtimes

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
            locale="en-US",
            geolocation={"longitude": -112.07, "latitude": 33.45},
            permissions=["geolocation"],
            viewport={'width': 1280, 'height': 1000}
        )
        page = await context.new_page()

        for idx, row in df.iterrows():
            try:
                raw_data = row.get("showtimes_data")
                if pd.isna(raw_data):
                    print(f"[{idx}] Skipped empty showtimes_data")
                    continue

                showtime_blocks = ast.literal_eval(raw_data)

                for block_idx, block in enumerate(showtime_blocks):
                    theater = block.get("theater", "unknown").replace(" ", "_").replace("/", "-")
                    location = block.get("location", "unknown").replace(" ", "_").replace("/", "-")
                    showtimes = block.get("showtimes", [])
                    urls = block.get("show_urls", [])
                    date = row.get("date", "unknown")

                    for i, (time, url) in enumerate(zip(showtimes, urls)):
                        try:
                            print(f"[{idx}-{block_idx}-{i}] Visiting: {url}")
                            await page.goto(url, timeout=60000)
                            print("    Page title:", await page.title())
                            await page.wait_for_timeout(2000)

                            # Dismiss language popup if any
                            try:
                                popup_detected = False
                                modal_text_el = await page.query_selector("div[class*='modal'], div[class*='popup']")
                                if modal_text_el:
                                    popup_detected = True
                                if popup_detected:
                                    print(f"    ⚠️ Language popup found. Attempting to dismiss...")
                                    buttons = page.locator("button:has-text('OK')")
                                    count = await buttons.count()
                                    for j in range(count):
                                        btn = buttons.nth(j)
                                        if await btn.is_visible():
                                            await btn.click()
                                            await page.wait_for_timeout(1000)
                                            break
                            except Exception as e:
                                print(f"    ⚠️ No popup or failed to dismiss it: {e}")

                            if debug:
                                debug_path = os.path.join(OUTPUT_DIR, f"debug_{idx}_{block_idx}_{i}.png")
                                await page.screenshot(path=debug_path, full_page=True)

                            try:
                                await page.wait_for_selector("div#seatPicker", timeout=8000)
                            except Exception as e:
                                print(f"    ⚠️ seatPicker not visible: {e}, waiting 5s fallback...")
                                await page.wait_for_timeout(5000)

                            # Count reserved and available seats
                            reserved_count = await page.locator("div.reservedSeat").count()
                            available_count = await page.locator("div.availableSeat").count()
                            reserved_seats = await page.locator("div.reservedSeat").evaluate_all(
                                "els => els.map(el => el.getAttribute('aria-label'))"
                            )
                            available_seats = await page.locator("div.availableSeat").evaluate_all(
                                "els => els.map(el => el.getAttribute('aria-label'))"
                            )

                            print(f"    🎟 Reserved: {reserved_count}, Available: {available_count}")

                            # Append each showtime result to list
                            results.append({
                                "row_index": idx,
                                "theater": theater,
                                "location": location,
                                "date": date,
                                "time": time,
                                "url": url,
                                "reserved_count": reserved_count,
                                "available_count": available_count,
                                "reserved_seats": json.dumps(reserved_seats),
                                "available_seats": json.dumps(available_seats)
                            })

                        except Exception as e:
                            print(f"    ❌ Failed for showtime {i} at theater block {block_idx}: {e}")

            except Exception as e:
                print(f"❌ Row error at index {idx}: {e}")

        await browser.close()

    # Create new DataFrame with all results
    results_df = pd.DataFrame(results)
    # OUTPUT_CSV = "OUTPUT_RESULTS.csv"
    results_df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Saved results to {OUTPUT_CSV}")


if __name__ == "__main__":
    INPUT_CSV = "coolie_presales.csv"  # replace with your file
    asyncio.run(take_seat_counts_from_csv(INPUT_CSV, debug=False))
