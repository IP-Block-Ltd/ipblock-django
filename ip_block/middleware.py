"""Django middleware entry point."""

import ipaddress

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect

from .client import IpBlockClient
from .conf import get_config


class IpBlockMiddleware:
    """Blocks requests rejected by the ip-block.com service.

    Add to ``MIDDLEWARE`` near the top:

        MIDDLEWARE = [
            "ip_block.middleware.IpBlockMiddleware",
            ...
        ]
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.config = get_config()
        self.client = IpBlockClient(self.config)

    def __call__(self, request):
        blocked_response = self._maybe_block(request)
        if blocked_response is not None:
            return blocked_response
        return self.get_response(request)

    def _maybe_block(self, request):
        if not self.config["ENABLED"]:
            return None

        ip = self._client_ip(request)
        if not ip or self._is_whitelisted(ip):
            return None

        user_agent = request.META.get("HTTP_USER_AGENT", "")
        referrer = request.META.get("HTTP_REFERER", "")

        if not self.client.is_blocked(ip, user_agent, referrer):
            return None

        if self.config["BLOCK_ACTION"] == "redirect":
            return HttpResponseRedirect(self.config["REDIRECT_URL"])

        return HttpResponseForbidden(self.config["BLOCK_MESSAGE"])

    def _client_ip(self, request):
        if self.config["BEHIND_PROXY"]:
            cf = request.META.get("HTTP_CF_CONNECTING_IP")
            if cf:
                return cf.strip()
            xff = request.META.get("HTTP_X_FORWARDED_FOR")
            if xff:
                return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")

    def _is_whitelisted(self, ip):
        whitelist = self.config["WHITELIST"]
        if not whitelist:
            return False
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            return False
        for entry in whitelist:
            try:
                if "/" in entry:
                    if addr in ipaddress.ip_network(entry, strict=False):
                        return True
                elif addr == ipaddress.ip_address(entry):
                    return True
            except ValueError:
                continue
        return False
