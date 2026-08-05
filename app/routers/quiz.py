"""Quiz router — knowledge assessment using today's lesson words."""

import random
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.api_client import ApiClient, ApiError
from app.dependencies import get_api_client, require_auth

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _build_questions(words: list[dict]) -> list[dict]:
    """Build multiple-choice translation questions from lesson word objects."""
    if not words:
        return []

    # Extract translations — word objects from lessons/today have:
    # {id, word, phonetic, translations: [{meaning}], examples: [{sentence}]}
    def get_translation(w: dict) -> str:
        trans = w.get("translations", [])
        return trans[0].get("meaning", "") if trans else w.get("translation", "")

    def get_example(w: dict) -> str:
        ex = w.get("examples", [])
        return ex[0].get("sentence", "") if ex else w.get("example_sentence", "")

    questions = []
    all_translations = [get_translation(w) for w in words]

    for i, word in enumerate(words):
        correct = get_translation(word)
        if not correct:
            continue

        # Build 3 distractors from other words' translations
        distractors = [t for j, t in enumerate(all_translations) if j != i and t]
        if len(distractors) >= 3:
            distractors = random.sample(distractors, 3)
        choices = distractors + [correct]
        random.shuffle(choices)

        questions.append({
            "id": str(i),
            "word": word.get("word", ""),
            "hint": word.get("phonetic", ""),
            "choices": choices,
            "correct_answer": correct,
            "type": "translation",
            "word_id": word.get("id"),
        })

    return questions


@router.get("", response_class=HTMLResponse)
async def quiz_page(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    quiz = None
    error = None

    try:
        # 1) Get the user's target language
        profile_resp = await client.get("/auth/me")
        profile = profile_resp.get("data", {}) if isinstance(profile_resp, dict) else {}
        language_id = profile.get("target_language_id")

        if not language_id:
            error = "No target language set. Please complete onboarding first."
        else:
            # 2) Start a quiz attempt
            attempt_resp = await client.post("/quiz/start", json={
                "language_id": language_id,
                "quiz_type": "daily",
            })
            attempt = attempt_resp.get("data", attempt_resp) if isinstance(attempt_resp, dict) else {}
            attempt_id = attempt.get("attempt_id")

            # 3) Fetch today's lesson words to build client-side questions
            lesson_resp = await client.get("/lessons/today")
            lesson = lesson_resp.get("data", lesson_resp) if isinstance(lesson_resp, dict) else {}
            words = lesson.get("words", []) if isinstance(lesson, dict) else []

            questions = _build_questions(words)

            quiz = {
                "id": attempt_id,
                "questions": questions,
                "total": attempt.get("total_questions", len(questions)),
            }

            if not questions:
                error = "No words available for today's quiz. Complete a lesson first."

    except ApiError as e:
        error = e.detail
    finally:
        await client.aclose()

    return templates.TemplateResponse(request, "quiz.html", {
        "quiz": quiz,
        "error": error,
    })


@router.post("/{quiz_id}/answer")
async def answer_question(
    quiz_id: str,
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    body = await request.json()
    # Map from our client format to the backend schema:
    # AnswerRequest(question_type, word_id, answer: dict)
    backend_body = {
        "question_type": body.get("question_type", "translation"),
        "word_id": body.get("word_id"),
        "answer": {"value": body.get("answer", "")},
    }
    try:
        resp = await client.post(f"/quiz/{quiz_id}/answer", json=backend_body)
        return JSONResponse(resp)
    except ApiError as e:
        return JSONResponse({"error": e.detail}, status_code=e.status_code)
    finally:
        await client.aclose()


@router.post("/{quiz_id}/complete")
async def complete_quiz(
    quiz_id: str,
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        resp = await client.post(f"/quiz/{quiz_id}/complete", json={})
        return JSONResponse(resp)
    except ApiError as e:
        return JSONResponse({"error": e.detail}, status_code=e.status_code)
    finally:
        await client.aclose()
