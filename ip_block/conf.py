"""Settings resolution with sane defaults.

All values are read from ``settings.IP_BLOCK`` (a dict). Missing keys fall back
to the defaults below.
"""

from django.conf import settings

DEFAULTS = {
    "ENABLED": True,
    "SITE_ID": "",
    "API_KEY": "",
    "API_URL": "https://api.ip-block.com/v1/check",
    "FAIL_OPEN": True,
    "CACHE_TTL": 300,
    "TIMEOUT": 1.0,
    "BEHIND_PROXY": False,
    "BLOCK_ACTION": "403",  # "403" or "redirect"
    "REDIRECT_URL": "https://www.ip-block.com/blocked.php",
    "BLOCK_MESSAGE": "Access denied.",
    "WHITELIST": [],
    "CACHE_ALIAS": "default",
}


def get_config():
    """Return the merged configuration dict."""
    user = getattr(settings, "IP_BLOCK", {}) or {}
    config = dict(DEFAULTS)
    config.update(user)
    return config
