from fastapi import FastAPI, HTTPException, Query

from services.config import settings
from services.marketaux_client import (
    QuotaExceeded,
    UpstreamError,
    UpstreamTimeout,
    fetch_news,
)

app = FastAPI(
    title="Financial News Intelligence Agent",
    description="Fetch and structure global financial news",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "message": "Financial News Intelligence Agent API",
        "docs": "/docs",
        "news_endpoint": "/news",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/news")
def get_news(
    symbols: str | None = Query(
        default=None,
        description="Optional comma-separated stock symbols, e.g. AAPL,TSLA",
    ),
    countries: str | None = Query(
        default=None,
        description="Optional comma-separated country codes, e.g. in,us",
    ),
    limit: int = Query(default=3, ge=1, le=3),
):
    if not settings.marketaux_api_token:
        raise HTTPException(
            status_code=500,
            detail="MARKETAUX_API_TOKEN is missing from .env",
        )

    params = {"limit": limit}
    if symbols:
        params["symbols"] = symbols
    if countries:
        params["countries"] = countries

    try:
        payload = fetch_news(**params)
    except QuotaExceeded as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except UpstreamTimeout as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except UpstreamError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="Marketaux returned invalid JSON") from exc

    if "errors" in payload:
        raise HTTPException(status_code=502, detail=payload["errors"])

    articles = []
    for article in payload.get("data", []):
        articles.append({
            "uuid": article.get("uuid"),
            "title": article.get("title"),
            "description": article.get("description"),
            "snippet": article.get("snippet"),
            "url": article.get("url"),
            "source": article.get("source"),
            "published_at": article.get("published_at"),
            "language": article.get("language"),
            "entities": [
                {
                    "symbol": entity.get("symbol"),
                    "name": entity.get("name"),
                    "country": entity.get("country"),
                    "industry": entity.get("industry"),
                    "type": entity.get("type"),
                    "sentiment_score": entity.get("sentiment_score"),
                    "match_score": entity.get("match_score"),
                }
                for entity in article.get("entities") or []
            ],
        })

    return {
        "count": len(articles),
        "meta": payload.get("meta", {}),
        "warnings": payload.get("warnings", []),
        "articles": articles,
    }