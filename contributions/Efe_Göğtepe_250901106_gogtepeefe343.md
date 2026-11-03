## Contributions

### Efe Göğtepe: Configuration and validation helpers

- Set up the project's settings in one place: the target page, the ntfy server,
  the data file, the default check interval (15 minutes), the request timeout and
  a browser `User-Agent` header so the site treats requests like a normal browser.
- `timestamp()`: formats the current date and time for log messages.
- `to_price()`: turns a value into a valid price and rejects anything that is not
  a real positive number (text, booleans, NaN, infinity, zero or negative values).
- `parse_price_text()`: reads prices written like `$1,299.99` on the page and
  converts them to numbers.
- `make_full_link()`: turns a relative product link into a full URL and only
  accepts secure (`https`) links on webscraper.io, so broken or outside links
  are ignored.

