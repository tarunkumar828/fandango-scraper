import asyncio
import re
from playwright.async_api import async_playwright
from datetime import datetime
from decimal import Decimal


state_to_city_slug = {
    "New York": "new-york-ny",
    "California": "los-angeles-ca",
    "Texas": "houston-tx",
    "Florida": "miami-fl",
    "Illinois": "chicago-il",
    "Massachusetts": "boston-ma",
    "Washington": "seattle-wa",
    "Georgia": "atlanta-ga",
    "Pennsylvania": "philadelphia-pa",
    "Arizona": "phoenix-az",
}

# state_to_city_slugs = {
#     "Alabama": ["birmingham-al", "mobile-al", "montgomery-al"],
#     "Alaska": ["anchorage-ak", "fairbanks-ak", "juneau-ak"],
#     "American Samoa": ["pago-pago-as"],
#     "Arizona": ["phoenix-az", "tucson-az", "flagstaff-az"],
#     "Arkansas": ["little-rock-ar", "fayetteville-ar", "fort-smith-ar"],
#     "California": ["los-angeles-ca", "san-francisco-ca", "san-diego-ca", "sacramento-ca"],
#     "Colorado": ["denver-co", "colorado-springs-co", "boulder-co"],
#     "Connecticut": ["hartford-ct", "new-haven-ct", "stamford-ct"],
#     "Delaware": ["wilmington-de", "dover-de"],
#     "District of Columbia": ["washington-dc"],
#     "Florida": ["miami-fl", "orlando-fl", "tampa-fl", "jacksonville-fl"],
#     "Georgia": ["atlanta-ga", "savannah-ga", "augusta-ga"],
#     "Guam": ["hagatna-gu"],
#     "Hawaii": ["honolulu-hi", "kahului-hi", "lihue-hi"],
#     "Idaho": ["boise-id", "idaho-falls-id", "twin-falls-id"],
#     "Illinois": ["chicago-il", "springfield-il", "peoria-il"],
#     "Indiana": ["indianapolis-in", "fort-wayne-in", "south-bend-in"],
#     "Iowa": ["des-moines-ia", "cedar-rapids-ia", "iowa-city-ia"],
#     "Kansas": ["wichita-ks", "topeka-ks", "overland-park-ks"],
#     "Kentucky": ["louisville-ky", "lexington-ky", "bowling-green-ky"],
#     "Louisiana": ["new-orleans-la", "baton-rouge-la", "lafayette-la"],
#     "Maine": ["portland-me", "bangor-me", "augusta-me"],
#     "Maryland": ["baltimore-md", "rockville-md", "frederick-md"],
#     "Massachusetts": ["boston-ma", "worcester-ma", "springfield-ma"],
#     "Michigan": ["detroit-mi", "grand-rapids-mi", "ann-arbor-mi"],
#     "Minnesota": ["minneapolis-mn", "st-paul-mn", "duluth-mn"],
#     "Mississippi": ["jackson-ms", "gulfport-ms", "tupelo-ms"],
#     "Missouri": ["kansas-city-mo", "st-louis-mo", "springfield-mo"],
#     "Montana": ["billings-mt", "missoula-mt", "bozeman-mt"],
#     "Nebraska": ["omaha-ne", "lincoln-ne", "grand-island-ne"],
#     "Nevada": ["las-vegas-nv", "reno-nv", "carson-city-nv"],
#     "New Hampshire": ["manchester-nh", "nashua-nh", "concord-nh"],
#     "New Jersey": ["newark-nj", "jersey-city-nj", "trenton-nj"],
#     "New Mexico": ["albuquerque-nm", "santa-fe-nm", "las-cruces-nm"],
#     "New York": ["new-york-ny", "buffalo-ny", "rochester-ny", "albany-ny"],
#     "North Carolina": ["charlotte-nc", "raleigh-nc", "asheville-nc"],
#     "North Dakota": ["fargo-nd", "bismarck-nd", "grand-forks-nd"],
#     "Northern Mariana Islands": ["saipan-mp"],
#     "Ohio": ["columbus-oh", "cleveland-oh", "cincinnati-oh"],
#     "Oklahoma": ["oklahoma-city-ok", "tulsa-ok", "norman-ok"],
#     "Oregon": ["portland-or", "eugene-or", "salem-or"],
#     "Pennsylvania": ["philadelphia-pa", "pittsburgh-pa", "harrisburg-pa"],
#     "Puerto Rico": ["san-juan-pr", "ponce-pr", "mayaguez-pr"],
#     "Rhode Island": ["providence-ri", "newport-ri"],
#     "South Carolina": ["charleston-sc", "columbia-sc", "greenville-sc"],
#     "South Dakota": ["sioux-falls-sd", "rapid-city-sd"],
#     "Tennessee": ["nashville-tn", "memphis-tn", "knoxville-tn"],
#     "Texas": ["houston-tx", "dallas-tx", "austin-tx", "san-antonio-tx"],
#     "Utah": ["salt-lake-city-ut", "provo-ut", "ogden-ut"],
#     "Vermont": ["burlington-vt", "montpelier-vt"],
#     "Virgin Islands": ["charlotte-amalie-vi"],
#     "Virginia": ["virginia-beach-va", "richmond-va", "norfolk-va"],
#     "Washington": ["seattle-wa", "spokane-wa", "tacoma-wa"],
#     "West Virginia": ["charleston-wv", "morgantown-wv", "huntington-wv"],
#     "Wisconsin": ["milwaukee-wi", "madison-wi", "green-bay-wi"],
#     "Wyoming": ["cheyenne-wy", "casper-wy", "jackson-wy"]
# }




async def get_movie_collections(movie_name: str, city_slug: str = "phoenix-az") -> list:
    # city_slug = state_to_city_slug.get(state)
    # if not city_slug:
    #     print(f"[ERROR] Unsupported state: {state}")
    #     return []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        search_url = f"https://www.fandango.com/{city_slug}_movietimes"
        await page.goto(search_url)

        try:
            await page.wait_for_load_state("networkidle", timeout=1000)
        except:
            await page.wait_for_load_state("load", timeout=15000)
            await page.wait_for_timeout(3000)

        await page.wait_for_selector("li.fd-movie", timeout=15000)

        movie_elements = page.locator("li.fd-movie")
        count = await movie_elements.count()
        print(f"Found {count} movie blocks")

        movie_links = []
        for i in range(count):
            el = movie_elements.nth(i)
            link_el = el.locator("a.fd-movie__link")
            title_el = link_el.locator("h3.fd-movie__title")

            try:
                await title_el.wait_for(timeout=3000)
                title = await title_el.inner_text()
                print(f"TITLE : {title}")
                href = await link_el.get_attribute("href")
            except Exception as e:
                print(f"[{i}] Error: {e}")
                continue

            if movie_name.lower() in title.lower():
                movie_links.append(href)

        if not movie_links:
            await browser.close()
            return []

        if "movie-overview" in movie_links[0]:
            full_url = "https://www.fandango.com" + movie_links[0].replace("movie-overview", "movietimes")
        else:
            full_url = "https://www.fandango.com" + movie_links[0]

        await page.goto(full_url)
        await page.wait_for_timeout(3000)
        theater_blocks = await page.query_selector_all("div.movie-showtimes__theater")

        print(f"Found {len(theater_blocks)} theater blocks")
        result = []
        for t in theater_blocks:
            try:
                name_el = await t.query_selector("h2")
                name = await name_el.inner_text() if name_el else "UNKNOWN"
                location_el = await t.query_selector("a[href*='maps']")
                location = await location_el.inner_text() if location_el else "UNKNOWN LOCATION"
                showtime_buttons = await t.query_selector_all("li.showtimes-btn-list__item a")
                showtimes = []
                show_urls = []
                for s in showtime_buttons:
                    try:
                        time_str = await s.inner_text()
                        href = await s.get_attribute("href")
                        if time_str.strip():
                            showtimes.append(time_str.strip())
                            show_urls.append(href)
                    except:
                        continue

                show_count = len(showtimes)
                print(f"Showtimes found: {show_count} → {showtimes}")

                price_el = await t.query_selector(".fd-showtimes__btn")
                price_text = await price_el.inner_text() if price_el else "$15.00"
                price_match = re.search(r"\$\d+(\.\d{1,2})?", price_text)
                price_str = price_match.group().replace("$", "") if price_match else "15.00"
                price = Decimal(price_str)

                occupancy_rate = Decimal("0.6")
                seat_count = 100
                revenue = price * occupancy_rate * show_count * seat_count

                result.append({
                    "movie": movie_name,
                    "status": "now_playing",
                    "theater": name.strip(),
                    "location": location.strip(),
                    "date": datetime.today().strftime("%Y-%m-%d"),
                    "show_count": show_count,
                    "ticket_price": str(price),
                    "revenue_est": str(round(revenue, 2)),
                    "showtimes": showtimes,
                    "show_urls": show_urls
                })

            except Exception as e:
                print(f"[ERROR] Failed parsing theater: {e}")

        await browser.close()
        return result


async def check_coming_soon(movie_name: str) -> dict:
    base_url = "https://www.fandango.com/movies-coming-soon"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        current_page = 1
        max_pages = 10

        while current_page <= max_pages:
            print(f"🔄 Checking page {current_page}")
            page_url = f"{base_url}?pn={current_page}"
            print(f"PAGE URL : {page_url}")
            await page.goto(page_url)
            await page.wait_for_timeout(3000)

            movie_cards = page.locator("ul.browse-movielist > li.poster-card")
            count = await movie_cards.count()
            print(f"Found {count} movie cards on page {current_page}")

            for i in range(count):
                card = movie_cards.nth(i)
                try:
                    title_el = card.locator("span.poster-card--title")
                    date_el = card.locator("time.poster-card--release-date")
                    link_el = card.locator("a")

                    title = await title_el.inner_text()
                    release_date = await date_el.inner_text()
                    detail_href = await link_el.get_attribute("href")

                    print(f"TITLE TEXT : {title}")
                    print(f"RELEASE DATE : {release_date}")
                    print(f"DETAIL URL : https://www.fandango.com{detail_href}")

                    if movie_name.lower() in title.lower():
                        full_url = "https://www.fandango.com" + detail_href

                        detail_page = await browser.new_page()
                        await detail_page.goto(full_url.replace("movie-overview", "movietimes"))
                        await detail_page.wait_for_timeout(3000)

                        theaters = await detail_page.query_selector_all("div.movie-showtimes__theater")
                        showtimes_data = []

                        for t in theaters:
                            try:
                                theater_name_el = await t.query_selector("h2")
                                location_el = await t.query_selector("a[href*='maps']")
                                showtime_buttons = await t.query_selector_all("li.showtimes-btn-list__item a")

                                theater_name = await theater_name_el.inner_text() if theater_name_el else "UNKNOWN"
                                location = await location_el.inner_text() if location_el else "UNKNOWN LOCATION"

                                times = []
                                urls = []
                                for s in showtime_buttons:
                                    try:
                                        time_str = await s.inner_text()
                                        href = await s.get_attribute("href")
                                        if time_str.strip():
                                            times.append(time_str.strip())
                                            urls.append(href)
                                    except:
                                        continue

                                if times:
                                    showtimes_data.append({
                                        "theater": theater_name.strip(),
                                        "location": location.strip(),
                                        "showtimes": times,
                                        "show_urls": urls
                                    })
                            except:
                                continue

                        await browser.close()
                        return {
                            "movie": title.strip(),
                            "status": "coming_soon",
                            "release_date": release_date.strip(),
                            "detail_url": full_url,
                            "presales_available": bool(showtimes_data),
                            "showtimes_data": showtimes_data
                        }

                except Exception as e:
                    print(f"[WARN] Movie card error: {e}")
                    continue

            # Pagination fix
            # Check if there's a next page
            try:
                pagination_buttons = page.locator("section.pagination button.pagination__pg-btn")
                count = await pagination_buttons.count()
                page_numbers = []

                for i in range(count):
                    try:
                        data_page = await pagination_buttons.nth(i).get_attribute("data-page")
                        if data_page and data_page.isdigit():
                            page_numbers.append(int(data_page))
                    except:
                        continue

                print(f"🔢 Found page numbers from buttons: {page_numbers}")

                if (current_page + 1) in page_numbers:
                    current_page += 1
                else:
                    print("📄 No more pages.")
                    break
            except Exception as e:
                print(f"[WARN] Pagination detection failed: {e}")
                break


        await browser.close()
        return {"movie": movie_name, "status": "not_found"}


async def search_movie(movie_name: str, city_slug: str = "phoenix-az"):
    print(f"SEARCHING FOR {movie_name} in {city_slug}")
    now_playing_results = await get_movie_collections(movie_name, city_slug)
    if now_playing_results:
        return now_playing_results
    else:
        coming_soon = await check_coming_soon(movie_name)
        return [coming_soon]


# Example usage
if __name__ == "__main__":
    movie = "Coolie"
    city_slug = "phoenix-az"
    results = asyncio.run(search_movie(movie, city_slug))
    for r in results:
        print(r)
