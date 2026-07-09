"""HTTP client + caching for the ip-block.com service."""

import hashlib
import logging

import requests
from django.core.cache import caches

logger = logging.getLogger("ip_block")


class IpBlockClient:
    """Queries ip-block.com and caches decisions per client fingerprint."""

    def __init__(self, config):
        self.config = config
        self._cache = caches[config["CACHE_ALIAS"]]

    def is_blocked(self, ip, user_agent, referrer):
        """Return True when the client should be blocked."""
        fingerprint = "{}|{}|{}".format(ip, user_agent, referrer)
        cache_key = "ip_block_" + hashlib.md5(fingerprint.encode("utf-8")).hexdigest()

        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        blocked = self._query(ip, user_agent, referrer)
        self._cache.set(cache_key, blocked, self.config["CACHE_TTL"])
        return blocked

    def _query(self, ip, user_agent, referrer):
        try:
            response = requests.post(
                self.config["API_URL"],
                json={
                    "api_key": self.config["API_KEY"],
                    "site_id": self.config["SITE_ID"],
                    "ip": ip,
                    "user_agent": user_agent,
                    "referrer": referrer,
                },
                headers={"Content-Type": "application/json"},
                timeout=self.config["TIMEOUT"],
            )
            if not (200 <= response.status_code < 300):
                return self._fail()

            data = response.json()
            if not isinstance(data, dict) or "action" not in data:
                return self._fail()

            return data["action"] == "block"
        except Exception as exc:  # noqa: BLE001 - fail open on ANY error
            logger.warning("ip-block check failed: %s", exc)
            return self._fail()

    def _fail(self):
        # fail open => allow => not blocked
        return not self.config["FAIL_OPEN"]
