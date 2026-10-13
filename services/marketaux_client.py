import json
import time

import requests

from services.config import settings, PROJECT_ROOT
from services.rate_limiter import allow

CACHE_DIR = PROJECT_ROOT / "data" / "cache"


class QuotaExceeded(Exception):
    pass


class UpstreamTimeout(Exception):
    pass


class UpstreamError(Exception):
    pass


def fetch_news(**params):
    if not allow():
        raise QuotaExceeded("Local daily quota reached")

    query = {
        "api_token": settings.marketaux_api_token,
        "language": "en",
        "must_have_entities": "true",
        **params,
    }
    try:
        r = requests.get(settings.marketaux_base_url, params=query, timeout=15)
    except requests.Timeout as e:
        raise UpstreamTimeout("Marketaux timed out") from e
    except requests.RequestException as e:
        raise UpstreamError("Could not reach Marketaux") from e

    if r.status_code in (402, 429):
        raise QuotaExceeded("Marketaux quota or rate limit hit")
    if not r.ok:
        raise UpstreamError(f"Marketaux returned {r.status_code}")

    payload = r.json()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / f"{int(time.time())}.json").write_text(json.dumps(payload))
    return payload