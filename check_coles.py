#!/usr/bin/env python3
"""
Checks Coles product prices using a headless browser (Playwright)
to bypass bot detection and get real search results + prices.
"""

import json
import sys
import time
from playwright.sync_api import sync_playwright


def check_coles_price(page, product: dict) -> dict | None:
    name = product["name"]
    normal_price = product["normal_price"]

    try:
        search_url = f"https://www.coles.com.au/search?q={name.replace(' ', '+')}"
        page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)  # Let JS render

        # Intercept the API response via network — Coles loads product data as JSON
        # Try to grab price from the rendered product tile
        tiles = page.query_selector_all("[data-testid='product-tile']")
        if not tiles:
            tiles = page.query_selector_all(".product-tile, .coles-targeting-ProductTile")

        if not tiles:
            print(f"[Coles] No product tiles found for: {name}", file=sys.stderr)
            return None

        tile = tiles[0]

        # Get current price
        price_el = (
            tile.query_selector("[data-testid='product-pricing'] .price__value") or
            tile.query_selector(".price__value") or
            tile.query_selector("[class*='price']")
        )
        if not price_el:
            print(f"[Coles] Could not find price element for: {name}", file=sys.stderr)
            return None

        price_text = price_el.inner_text().replace("$", "").replace("\n", "").strip()
        # Sometimes price renders as "5\n.50" or "$5.50"
        price_text = price_text.split()[0]
        current_price = float(price_text)

        # Check for "was" price or special badge
        was_el = tile.query_selector("[class*='was'], [data-testid*='was']")
        special_badge = tile.query_selector("[class*='special'], [class*='Special'], [data-testid*='special']")
        on_special = was_el is not None or special_badge is not None or current_price < normal_price

        if on_special:
            return {
                "store": "Coles",
                "name": name,
                "normal_price": normal_price,
                "sale_price": current_price,
                "savings": round(normal_price - current_price, 2),
                "url": search_url,
            }

    except Exception as e:
        print(f"[Coles] Error checking '{name}': {e}", file=sys.stderr)

    return None


def main():
    with open("products/products.json") as f:
        config = json.load(f)

    products = config.get("coles", [])
    sales = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        # Visit homepage first to get cookies
        page.goto("https://www.coles.com.au", wait_until="domcontentloaded", timeout=30000)
        time.sleep(1)

        for product in products:
            result = check_coles_price(page, product)
            if result:
                sales.append(result)
                print(f"[Coles] SALE: {result['name']} — ${result['sale_price']} (was ${result['normal_price']})")
            else:
                print(f"[Coles] No sale: {product['name']}")
            time.sleep(1)  # Polite delay between requests

        browser.close()

    with open("coles_sales.json", "w") as f:
        json.dump(sales, f, indent=2)

    print(f"\n[Coles] {len(sales)} sale(s) found.")


if __name__ == "__main__":
    main()
