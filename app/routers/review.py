"""Review router — spaced-repetition flashcard session."""

import asyncio
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.api_client import ApiClient, ApiError
from app.dependencies import get_api_client, require_auth

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


async def _enrich_word(client: ApiClient, entry: dict) -> dict:
    """Fetch full word details for a due-word entry and merge them."""
    word_id = entry.get("word_id")
    if not word_id:
        return entry
    try:
        resp = await client.get(f"/words/{word_id}")
        detail = resp.get("data", resp) if isinstance(resp, dict) else {}
        # Build a flat enriched object the template can use
        translations = detail.get("translations", [])
        examples = detail.get("examples", [])
        return {
            "id": detail.get("id", word_id),
            "word": detail.get("word", f"word #{word_id}"),
            "pronunciation": detail.get("phonetic", ""),
            "translation": translations[0].get("meaning", "") if translations else "",
            "example_sentence": examples[0].get("sentence", "") if examples else "",
            # keep SRS meta
            "mastery_level": entry.get("mastery_level", 0),
            "next_review_at": entry.get("next_review_at"),
        }
    except ApiError:
        return {**entry, "word": f"word #{word_id}", "translation": "", "example_sentence": ""}


@router.get("", response_class=HTMLResponse)
async def review_page(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        resp = await client.get("/review/due")
        # Response: {"success": true, "data": {"words": [{word_id, mastery_level, next_review_at}]}}
        data = resp.get("data", {}) if isinstance(resp, dict) else {}
        due_entries = data.get("words", []) if isinstance(data, dict) else []

        # Enrich each entry with full word data (concurrent fetches)
        words = await asyncio.gather(*[_enrich_word(client, e) for e in due_entries])
        words = list(words)
    except ApiError as e:
        words = []
        error = e.detail
    else:
        error = None
    finally:
        await client.aclose()

    return templates.TemplateResponse(request, "review.html", {
        "words": words,
        "error": error,
    })


@router.post("/submit")
async def submit_review(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    # Expected body: {word_id: int, quality: int (0-5)}
    body = await request.json()
    try:
        resp = await client.post("/review/submit", json=body)
        return JSONResponse(resp)
    except ApiError as e:
        return JSONResponse({"error": e.detail}, status_code=e.status_code)
    finally:
        await client.aclose()
