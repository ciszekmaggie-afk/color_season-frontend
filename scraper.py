import asyncio
from playwright.async_api import async_playwright
import pandas as pd

import aiohttp
import os

# The "Map" of how each website stores its data
CONFIG = {
    "princess_polly": {
        "url": "https://www.princesspolly.com/collections/dresses",
        "card": ".product-card",
        "name": ".product-card__title",
        "price": ".product-card__price",
        "img": "img.product-card__image"
    },
    "oh_polly": {
        "url": "https://www.ohpolly.com/collections/all-clothing",
        "card": ".product-item",
        "name": ".product-item__title",
        "price": ".product-item__price",
        "img": "img"
    }
}

async def scrape_site(browser, site_name, info):
    print(f"🕵️  Scraping {site_name}...")
    page = await browser.new_page()
    await page.goto(info['url'], wait_until="networkidle")

    # Scroll down to load "Lazy" images
    for _ in range(3):
        await page.mouse.wheel(0, 2000)
        await asyncio.sleep(1)

    products = []
    cards = await page.query_selector_all(info['card'])


    # Ensure images directory exists
    os.makedirs(f"images/{site_name}", exist_ok=True)

    async def download_image(session, url, path):
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    with open(path, 'wb') as f:
                        f.write(await resp.read())
        except Exception:
            pass

    async with aiohttp.ClientSession() as session:
        for idx, card in enumerate(cards[:20]): # Start with 20 items for testing
            try:
                name = await card.query_selector(info['name'])
                price = await card.query_selector(info['price'])
                img = await card.query_selector(info['img'])
                name_text = await name.inner_text() if name else "N/A"
                price_text = await price.inner_text() if price else "N/A"
                img_url = await img.get_attribute("src") if img else "N/A"

                # Download image if possible
                img_filename = f"images/{site_name}/{idx}.jpg"
                if img_url and img_url != "N/A":
                    await download_image(session, img_url, img_filename)
                else:
                    img_filename = ""

                products.append({
                    "store": site_name,
                    "name": name_text,
                    "price": price_text,
                    "image_url": img_url,
                    "image_path": img_filename
                })
            except Exception as e:
                continue

    await page.close()
    return products

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) # Set to False to watch it work!
        all_results = []


        for site, info in CONFIG.items():
            site_data = await scrape_site(browser, site, info)
            all_results.extend(site_data)


        # Save everything to a CSV file (The start of your database)
        df = pd.DataFrame(all_results)
        df.to_csv("clothing_data.csv", index=False)
        print("✅ Success! Data and images saved.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())