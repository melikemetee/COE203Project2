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