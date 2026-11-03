import argparse
import json
import math
import os
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


SITE_HOST = "webscraper.io"
SITE_ROOT = f"https://{SITE_HOST}"
PAGE_URL = f"{SITE_ROOT}/test-sites/e-commerce/allinone/computers/laptops"
NTFY_SERVER = "https://ntfy.sh"

DEFAULT_FILE = "laptops.json"
DEFAULT_INTERVAL_MINUTES = 15
REQUEST_TIMEOUT = 10

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def to_price(value):
    if isinstance(value, bool):
        return None
    try:
        price = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(price) or price <= 0:
        return None
    return price


def parse_price_text(text):
    if not isinstance(text, str):
        return None
    text = text.strip()
    if not text.startswith("$"):
        return None
    return to_price(text[1:].replace(",", ""))


def make_full_link(href):
    if not isinstance(href, str) or not href.strip():
        return None
    url = urljoin(SITE_ROOT, href.strip())
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != SITE_HOST:
        return None
    if parsed.path in ("", "/"):
        return None
    return url

def fetch_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Page could not be downloaded: {error}")
        return None

    if "html" not in response.headers.get("Content-Type", "").lower():
        print("The server did not return an HTML page.")
        return None

    return BeautifulSoup(response.text, "html.parser")


def parse_card(card):
    link_tag = card.select_one(".title[href]")
    price_tag = card.select_one(".price span") or card.select_one(".price")
    if link_tag is None or price_tag is None:
        return None

    name = " ".join((link_tag.get("title") or link_tag.get_text()).split())
    link = make_full_link(link_tag.get("href"))
    price = parse_price_text(price_tag.get_text(strip=True))
    if not name or link is None or price is None:
        return None

    product_id = urlparse(link).path.rstrip("/").split("/")[-1]
    if not product_id:
        return None

    description_tag = card.select_one(".description")
    description = " ".join(description_tag.get_text().split()) if description_tag else ""

    return {
        "id": product_id,
        "name": name,
        "description": description,
        "price": price,
        "link": link,
        "last_seen": timestamp(),
    }
    def build_message(laptop, old_price):
    new_price = laptop["price"]
    return (
        f"{laptop['name']}\n"
        f"Price dropped: ${old_price:.2f} -> ${new_price:.2f} "
        f"(-${old_price - new_price:.2f})\n"
        f"{laptop['link']}"
    )


def send_notification(topic, laptop, old_price):
    try:
        response = requests.post(
            f"{NTFY_SERVER}/{topic}",
            data=build_message(laptop, old_price).encode("utf-8"),
            headers={"Title": "Laptop price drop"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Notification could not be sent: {error}")
        return False

    print(
        f"Notification sent: {laptop['name']} "
        f"${old_price:.2f} -> ${laptop['price']:.2f}"
    )
    return True


def compare_and_notify(saved, current, topic, dry_run):
    drops = 0

    for product_id, laptop in current.items():
        new_price = laptop["price"]
        old_record = saved.get(product_id)

        if old_record is None:
            print(f"New laptop: {laptop['name']} (${new_price:.2f})")
            saved[product_id] = laptop
            continue

        old_price = to_price(old_record.get("price")) if isinstance(old_record, dict) else None

        if old_price is None:
            print(f"Saved price of {product_id} was invalid; replaced with ${new_price:.2f}.")
            saved[product_id] = laptop
            continue

        if new_price < old_price:
            if dry_run:
                print(
                    f"Would notify: {laptop['name']} "
                    f"${old_price:.2f} -> ${new_price:.2f}"
                )
            elif not send_notification(topic, laptop, old_price):
                continue
            drops += 1

        saved[product_id] = laptop

    return drops
