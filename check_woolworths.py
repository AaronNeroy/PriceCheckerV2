#!/usr/bin/env python3
"""
Checks Woolworths product prices using a headless browser (Playwright).
Woolworths blocks direct API calls without valid session cookies,
so we use a real browser session to get around the 403.
"""

import json
import sys
import time
from playwright.sync_api import sync_playwright


def check_woolworths_price(page, product: dict) -> dict | None:
    name = product["name"]
    normal_price = product["normal_price"]

    try:
        search_url = f"https://www.woolworths.com.au/shop/search/products?searchTerm={name.replace(' ', '+')}"
        page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        # Grab rendered product tiles
        tiles = page.query_selector_all("[data-testid='product-tile'], .shelfProductTile, product-tile")
        if not tiles:
            tiles = page.query_selector_all("[class*='product-tile'], [class*='productTile']")

        if not tiles:
            print(f"[Woolworths] No product tiles found for: {name}", file=sys.stderr)
            return None

        tile = tiles[0]

        # Get current price
        price_el = (
            tile.query_selector("[class*='price'] .price--current") or
            tile.query_selector(".price--current") or
            tile.query_selector("[class*='Price']") or
            tile.query_selector("[data-testid='price']")
        )
        if not price_el:
            print(f"[Woolworths] Could not find price for: {name}", file=sys.stderr)
            return None

        price_text = price_el.inner_text().replace("$", "").replace("\n", "").strip().split()[0]
        current_price = float(price_text)

        # Check for "was" price or special/sale badge
        was_el = tile.query_selector("[class*='was-price'], [class*='wasPrice'], .price--was")
        special_badge = tile.query_selector("[class*='special'], [class*='Special'], [class*='sale'], [class*='Sale']")
        on_special = was_el is not None or special_badge is not None or current_price < normal_price

        # Try to get the product URL
        link_el = tile.query_selector("a[href*='/shop/productdetails']")
        product_url = ("https://www.woolworths.com.au" + link_el.get_attribute("href")) if link_el else search_url

        if on_special:
            was_price = normal_price
            if was_el:
                try:
                    was_text = was_el.inner_text().replace("$", "").replace("\n", "").strip().split()[0]
                    was_price = float(was_text)
                except Exception:
                    pass

            return {
                "store": "Woolworths",
                "name": name,
                "normal_price": was_price,
                "sale_price": current_price,
                "savings": round(was_price - current_price, 2),
                "url": product_url,
            }

    except Exception as e:
        print(f"[Woolworths] Error checking '{name}': {e}", file=sys.stderr)

    return None


def main():
    with open("products/products.json") as f:
        config = json.load(f)

    products = config.get("woolworths", [])
    sales = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        # Visit homepage first to establish session/cookies
        page.goto("https://www.woolworths.com.au", wait_until="domcontentloaded", timeout=30000)
        time.sleep(1)

        for product in products:
            result = check_woolworths_price(page, product)
            if result:
                sales.append(result)
                print(f"[Woolworths] SALE: {result['name']} — ${result['sale_price']} (was ${result['normal_price']})")
            else:
                print(f"[Woolworths] No sale: {product['name']}")
            time.sleep(1)

        browser.close()

    with open("woolworths_sales.json", "w") as f:
        json.dump(sales, f, indent=2)

    print(f"\n[Woolworths] {len(sales)} sale(s) found.")


if __name__ == "__main__":
    main()
