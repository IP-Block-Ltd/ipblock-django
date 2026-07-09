> ⚠️ **Status: untested.** This extension is provided as-is and has **not been tested in production**. Please feel free to fork, modify, improve, and open pull requests.
>
> Licensed under **GNU GPLv3** (see [LICENSE](LICENSE)).

# IP Block — Django Middleware

Django middleware that checks every request against the
[ip-block.com](https://www.ip-block.com) service and blocks disallowed clients.

**Targets:** Django 3.2+ (incl. 4.x / 5.x), Python 3.8+.

## Install

```bash
pip install django-ip-block
```

## Register

Add the app and the middleware (near the top, before your views run) in
`settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "ip_block",
]

MIDDLEWARE = [
    "ip_block.middleware.IpBlockMiddleware",
    # ... the rest of your middleware
]
```

## Configure

Add an `IP_BLOCK` dict to `settings.py`. Only the keys you want to override are
required:

```python
IP_BLOCK = {
    "ENABLED": True,
    "SITE_ID": "your-site-id",
    "API_KEY": "your-api-key",
    "API_URL": "https://api.ip-block.com/v1/check",  # default
    "FAIL_OPEN": True,        # allow on error/timeout (default)
    "CACHE_TTL": 300,         # seconds (uses Django cache)
    "TIMEOUT": 1.0,           # seconds
    "BEHIND_PROXY": False,    # trust X-Forwarded-For / CF-Connecting-IP
    "BLOCK_ACTION": "403",    # "403" or "redirect"
    "REDIRECT_URL": "https://www.ip-block.com/blocked.php",
    "BLOCK_MESSAGE": "Access denied.",
    "WHITELIST": ["127.0.0.1", "10.0.0.0/8"],
    "CACHE_ALIAS": "default",  # which CACHES entry to use
}
```

## How it works

- Builds `{api_key, site_id, ip, user_agent, referrer}` and `POST`s it with a
  **1 second timeout**.
- Blocks only when the response is `{"action":"block"}`.
- **Fails open** on any error/timeout/non-2xx/missing `action`
  (set `FAIL_OPEN=False` to fail closed).
- Caches each decision for `CACHE_TTL` seconds using the Django cache framework,
  keyed by `md5(ip|user_agent|referrer)`.
- Honours `WHITELIST` (individual IPs and CIDR ranges).
- Reads the real client IP; with `BEHIND_PROXY=True` it trusts
  `CF-Connecting-IP` then the first `X-Forwarded-For` hop.
