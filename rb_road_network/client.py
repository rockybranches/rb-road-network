"""HTTP client for the rb-road-network Worker API.

Standard library only. Every failure is raised as ApiError with a message
meant to be shown to the person running the command.
"""

import json
import os
import urllib.error
import urllib.request
from urllib.parse import quote

DEFAULT_URL = "http://localhost:8787"
# One analysis is a single request; the Worker allows up to 60 s of CPU.
TIMEOUT_S = 120

URL_ENV = "RB_API_URL"
ACCESS_ID_ENV = "RB_ACCESS_CLIENT_ID"
ACCESS_SECRET_ENV = "RB_ACCESS_CLIENT_SECRET"


class ApiError(Exception):
    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Report redirects instead of following them.

    The API never redirects. A redirect means something in front of it, most
    likely the Cloudflare Access login page, answered instead.
    """

    def redirect_request(self, *args, **kwargs):
        return None


class Client:
    def __init__(self, base_url=None, access_id=None, access_secret=None):
        self.base_url = (base_url or os.environ.get(URL_ENV) or DEFAULT_URL).rstrip("/")
        access_id = access_id or os.environ.get(ACCESS_ID_ENV)
        access_secret = access_secret or os.environ.get(ACCESS_SECRET_ENV)
        # Some Cloudflare settings reject Python's default user agent.
        self._headers = {"user-agent": "rb-road-network-cli"}
        if access_id and access_secret:
            # A Cloudflare Access service token; see the README.
            self._headers["CF-Access-Client-Id"] = access_id
            self._headers["CF-Access-Client-Secret"] = access_secret
        self._opener = urllib.request.build_opener(_NoRedirect)

    def page_url(self, fragment=""):
        return f"{self.base_url}/{fragment}"

    # -- transport -----------------------------------------------------------

    def _request(self, method, path, payload=None):
        headers = dict(self._headers)
        data = None
        if payload is not None:
            data = json.dumps(payload).encode()
            headers["content-type"] = "application/json"
        req = urllib.request.Request(
            self.base_url + path, data=data, headers=headers, method=method
        )
        try:
            with self._opener.open(req, timeout=TIMEOUT_S) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise self._error(exc) from None
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            reason = getattr(exc, "reason", exc)
            raise ApiError(f"could not reach {self.base_url}: {reason}") from None

    def _error(self, exc):
        body = exc.read().decode("utf-8", "replace")
        if 300 <= exc.code < 400:
            target = exc.headers.get("location", "")
            if "cloudflareaccess.com" in target:
                return ApiError(
                    f"{self.base_url} is behind Cloudflare Access. Set "
                    f"{ACCESS_ID_ENV} and {ACCESS_SECRET_ENV} to a service token "
                    "that is allowed to reach it.",
                    exc.code,
                )
            return ApiError(
                f"{self.base_url} redirected to {target or 'another address'}; "
                "check the address.",
                exc.code,
            )
        try:
            message = json.loads(body)["error"]
        except (ValueError, KeyError, TypeError):
            message = f"HTTP {exc.code} {exc.reason}"
            if exc.code == 403:
                message += " (if this is behind Cloudflare Access, check the service token)"
        return ApiError(str(message), exc.code)

    def _json(self, method, path, payload=None):
        text = self._request(method, path, payload)
        try:
            return json.loads(text)
        except ValueError:
            raise ApiError(
                f"{self.base_url} did not answer with JSON; check the address."
            ) from None

    # -- API -----------------------------------------------------------------

    def status(self):
        return self._json("GET", "/api/status")

    def create_analysis(self, params):
        return self._json("POST", "/api/analyses", params)

    def analysis(self, analysis_id):
        return self._json("GET", f"/api/analyses/{quote(analysis_id, safe='')}")

    def run_pending(self, analysis_id):
        return self._json("POST", f"/api/analyses/{quote(analysis_id, safe='')}/run")

    def report_tex(self, analysis_id):
        return self._request("GET", f"/api/analyses/{quote(analysis_id, safe='')}/report.tex")

    def area_geojson(self, analysis_id):
        return self._request("GET", f"/api/analyses/{quote(analysis_id, safe='')}/area.geojson")

    def create_batch(self, payload):
        return self._json("POST", "/api/batches", payload)

    def batch(self, batch_id):
        return self._json("GET", f"/api/batches/{quote(batch_id, safe='')}")

    def batch_summary_csv(self, batch_id):
        return self._request("GET", f"/api/batches/{quote(batch_id, safe='')}/summary.csv")
