# Laptop Price Tracker

A Python script that watches the laptop page of the
[webscraper.io test shop](https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops),
remembers every laptop's price in a JSON file, and sends a push notification
to your phone through [ntfy](https://ntfy.sh) when a laptop gets cheaper.

## Features

- Checks the page automatically at a fixed interval (every 15 minutes by default)
- Reads the full name, price, link and description of every laptop
- Saves prices to `laptops.json`, so nothing is lost when the program stops
- Sends a phone notification with the old price, new price, discount and product link
- Detects laptops that are added to the page later
- Keeps the old price if a notification fails, so the alert is retried on the next check
- Never overwrites the saved file when it is broken or when the page could not be read
- Dry-run mode to see what would happen without sending or saving anything

## Requirements

- Python 3.9 or newer
- [requests](https://pypi.org/project/requests/)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
- The ntfy app on your phone (Android or iOS)

## Installation

```bash
python3 -m pip install requests beautifulsoup4
```

## Setting up notifications

1. Install the ntfy app on your phone.
2. Tap **+** and enter a topic name, for example `laptop-price-x7k2`.
3. Leave **Use another server** turned off and tap **Subscribe**.
4. Allow notifications when the app asks.

ntfy topics are public: anyone who knows the name can read its messages.
Choose a name that is hard to guess.

## Usage

Start the tracker with the same topic name you subscribed to:

```bash
python3 laptop_tracker.py --topic laptop-price-x7k2
```

The program keeps running and checks the page every 15 minutes. Press
**Ctrl+C** to stop it.

### Options

| Option | Description | Default |
|---|---|---|
| `--topic` | ntfy topic that receives the alerts (required) | – |
| `--interval` | Minutes between checks (at least 1) | `15` |
| `--file` | JSON file for saved prices | `laptops.json` |
| `--once` | Run a single check and exit | off |
| `--dry-run` | Show what would happen without sending or saving | off |

### Examples

```bash
# Single check, then exit
python3 laptop_tracker.py --topic laptop-price-x7k2 --once

# Preview only: no notification, no file changes
python3 laptop_tracker.py --topic laptop-price-x7k2 --once --dry-run

# Check every 30 minutes and save to another file
python3 laptop_tracker.py --topic laptop-price-x7k2 --interval 30 --file prices.json
```

### Example output

```
Laptop price tracker started: checking every 15 minute(s). Press Ctrl+C to stop.

[2026-11-02 13:10:59] Checking laptop prices...
Found 117 product cards.
Checked 117 laptops: 0 price drop(s).
Saved 117 records to laptops.json.
Next check in 15.0 minutes.
```

## How it works

Each check follows the same steps:

1. **Load** the saved prices from `laptops.json`. If the file does not exist,
   start empty. If it is broken, skip the check and leave the file untouched.
2. **Download** the laptop page with a 10-second timeout and make sure an HTML
   page came back.
3. **Parse** every product card (`.thumbnail`) with Beautiful Soup. The full
   name comes from the link's `title` attribute, because the visible name may
   be shortened. A price such as `$1,149.00` becomes `1149.0`. The product ID
   is the last part of the product link (`.../product/60` → `60`). Cards with
   missing or invalid data are skipped.
4. **Compare** the current prices with the saved ones:
   - First run: save all prices, send nothing.
   - New laptop: save it.
   - Price dropped: send a notification, then save the new price.
   - Notification failed: keep the old price so the alert is retried.
   - Price went up or stayed the same: save the new price.
5. **Save** the records. The data is written to a temporary file first and then
   moved over `laptops.json`, so an interrupted write cannot corrupt it.

The waiting time takes the duration of each check into account, so checks stay
evenly spaced. An unexpected error during one check is printed and the program
moves on to the next check instead of crashing.

## Notification format

```
Laptop price drop
Asus VivoBook X441NA-GA190
Price dropped: $400.00 -> $295.99 (-$104.01)
https://webscraper.io/test-sites/e-commerce/allinone/product/60
```

## Saved data

`laptops.json` stores one record per laptop, keyed by product ID:

```json
{
  "60": {
    "id": "60",
    "name": "Asus VivoBook X441NA-GA190",
    "description": "Asus VivoBook X441NA-GA190 Chocolate Black, 14\", Celeron N3450, 4GB, 128GB SSD, Endless OS, ENG kbd",
    "price": 295.99,
    "link": "https://webscraper.io/test-sites/e-commerce/allinone/product/60",
    "last_seen": "2026-11-02 13:10:59"
  }
}
```

## Testing a price drop

The prices on the test shop do not normally change, so you can simulate a drop:

1. Run the tracker once to create `laptops.json`:
   ```bash
   python3 laptop_tracker.py --topic laptop-price-x7k2 --once
   ```
2. Open `laptops.json` and raise the `price` of any laptop, for example
   `295.99` → `400.0`. Save the file.
3. Run the same command again. The terminal shows `Notification sent: ...`
   and the alert arrives on your phone.
4. Run it once more. It reports `0 price drop(s)`, because the saved price is
   now up to date and the same alert is not sent twice.

## Limitations

- The tracker only runs while the terminal stays open. On macOS you can keep
  the computer awake with `caffeinate -i python3 laptop_tracker.py --topic ...`.
- If the program is stopped, missed checks are not repeated. The next check
  still compares against the saved prices, so a drop that happened in the
  meantime is still reported.
- The script is written for the HTML structure of the webscraper.io test shop.
  If the page layout changes, the selectors in `parse_card` need to be updated.

## Project structure

```
.
├── laptop_tracker.py   # the tracker
├── laptops.json        # saved prices (created on the first run)
└── README.md
```
