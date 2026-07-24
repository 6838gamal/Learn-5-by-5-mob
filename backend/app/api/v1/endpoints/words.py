from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.repositories.word_repository import WordRepository

router = APIRouter()


def ok(data):
    return {"success": True, "data": data, "message": None}


@router.get("/search")
async def search_words(
    language_id: int,
    q: str = Query(..., min_length=1),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = WordRepository(db)
    words = await repo.search(language_id, q)
    return ok({"words": [{"id": w.id, "word": w.word, "phonetic": w.phonetic} for w in words]})


@router.get("/{word_id}")
async def get_word(
    word_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = WordRepository(db)
    word = await repo.get_with_details(word_id)
    if not word:
        raise NotFoundError("Word")
    return ok({
        "id": word.id,
        "word": word.word,
        "phonetic": word.phonetic,
        "audio_url": word.audio_url,
        "part_of_speech": word.part_of_speech,
        "difficulty": word.difficulty,
        "translations": [{"language_id": t.language_id, "meaning": t.meaning, "notes": t.notes} for t in word.translations],
        "examples": [{"sentence": e.sentence, "translation": e.translation, "audio_url": e.audio_url} for e in word.examples],
    })
