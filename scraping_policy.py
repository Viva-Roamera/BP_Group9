"""Shared responsible-scraping policy for the production scrapers."""

from __future__ import annotations

import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests


BOT_TOKEN = "Group9StudentResearchBot"
USER_AGENT = (
    f"{BOT_TOKEN}/1.0 "
    "(educational LEGO price-comparison project; "
    "https://github.com/Viva-Roamera/BP_Group9)"
)
DEFAULT_CRAWL_DELAY_SECONDS = 10.0


class RobotsPolicyUnavailable(RuntimeError):
    """Raised when robots.txt cannot be verified safely."""


class RobotsPolicy:
    """Load robots.txt, check every page URL, and pace requests to one site."""

    def __init__(
        self,
        domain: str,
        default_delay: float = DEFAULT_CRAWL_DELAY_SECONDS,
        timeout: float = 10.0,
    ) -> None:
        parsed_domain = urlparse(domain)
        self.domain = f"{parsed_domain.scheme}://{parsed_domain.netloc}"
        self.robots_url = f"{self.domain}/robots.txt"
        self.delay = default_delay
        self.parser: RobotFileParser | None = None
        self.error: str | None = None
        self._last_request_started: float | None = None

        try:
            response = requests.get(
                self.robots_url,
                headers={"User-Agent": USER_AGENT},
                timeout=timeout,
            )
            self._last_request_started = time.monotonic()

            if 200 <= response.status_code < 300:
                parser = RobotFileParser()
                parser.set_url(self.robots_url)
                parser.parse(response.text.splitlines())
                self.parser = parser

                declared_delay = (
                    parser.crawl_delay(BOT_TOKEN)
                    or parser.crawl_delay("*")
                )
                if declared_delay is not None:
                    self.delay = max(self.delay, float(declared_delay))

                print(
                    f"Loaded {self.robots_url}; "
                    f"using a {self.delay:g}-second crawl delay."
                )
            elif 400 <= response.status_code < 500:
                # RFC 9309 treats a 4xx robots response as unavailable, which
                # means no robots rules apply. The normal page response still
                # controls whether the resource can be accessed.
                parser = RobotFileParser()
                parser.parse([])
                self.parser = parser
                print(
                    f"{self.robots_url} returned {response.status_code}; "
                    f"no robots rules apply. Using a {self.delay:g}-second delay."
                )
            else:
                self.error = (
                    f"{self.robots_url} returned HTTP {response.status_code}"
                )
        except requests.RequestException as exc:
            self.error = f"could not retrieve {self.robots_url}: {exc}"

        if self.error:
            message = f"[robots] {self.error}. Scraping this site is disabled."
            print(message)
            raise RobotsPolicyUnavailable(message)

    def can_fetch(self, url: str) -> bool:
        """Return False for another origin, an unreadable policy, or a disallow."""
        parsed_url = urlparse(url)
        url_origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
        if url_origin != self.domain:
            print(f"[robots] Skipping URL outside {self.domain}: {url}")
            return False

        if self.parser is None:
            print(f"[robots] Cannot verify permission; skipping: {url}")
            return False

        allowed = self.parser.can_fetch(BOT_TOKEN, url)
        if not allowed:
            print(f"[robots] Disallowed; skipping: {url}")
        return allowed

    def wait_before_request(self) -> None:
        """Wait long enough to maintain the configured gap between requests."""
        if self._last_request_started is not None:
            elapsed = time.monotonic() - self._last_request_started
            remaining = self.delay - elapsed
            if remaining > 0:
                print(f"Waiting {remaining:.1f} seconds before the next request...")
                time.sleep(remaining)
        self._last_request_started = time.monotonic()
