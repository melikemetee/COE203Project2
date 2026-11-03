Student number: 2409111010
GitHub username: beyzaktngl
Implemented parse_price_text() and to_price() functions for robust data cleaning, converting formatted price strings into valid floating-point numbers.

Developed strict URL parsing and security validation logic (make_full_link()) using urlparse and urljoin to prevent processing external or invalid links.

Created helper utilities such as timestamp() for accurate event logging and execution tracking.

Set up script configuration parameters, including HTTP header spoofing (User-Agent), request timeouts, and default execution intervals for scheduled scraping tasks.

Added comprehensive error handling to filter out invalid prices, non-finite values (NaN/Infinity), and broken domain paths.
