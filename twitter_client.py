"""Twitter/X v2 posting wrapper with dry-run safety."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class TwitterConfig:
    api_key: str | None = os.environ.get("TWITTER_API_KEY")
    api_secret: str | None = os.environ.get("TWITTER_API_SECRET")
    access_token: str | None = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_secret: str | None = os.environ.get("TWITTER_ACCESS_SECRET")
    dry_run: bool = os.environ.get("TWITTER_DRY_RUN", "1") != "0"


class TwitterPoster:
    def __init__(self, config: TwitterConfig | None = None):
        self.config = config or TwitterConfig()

    def enabled(self) -> bool:
        c = self.config
        return bool(c.api_key and c.api_secret and c.access_token and c.access_secret and not c.dry_run)

    def post(self, text: str):
        if not self.enabled():
            print("[dry-run tweet]")
            print(text)
            return {"dry_run": True, "text": text}
        from requests_oauthlib import OAuth1Session
        c = self.config
        session = OAuth1Session(c.api_key, client_secret=c.api_secret, resource_owner_key=c.access_token, resource_owner_secret=c.access_secret)
        response = session.post("https://api.twitter.com/2/tweets", json={"text": text}, timeout=20)
        if response.status_code >= 300:
            raise RuntimeError(f"Twitter API error {response.status_code}: {response.text[:300]}")
        return response.json()
