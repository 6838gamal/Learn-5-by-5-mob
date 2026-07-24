from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.language import Language

router = APIRouter()


def ok(data):
    return {"success": True, "data": data, "message": None}


def lang_to_dict(lang: Language) -> dict:
    return {
        "id": lang.id,
        "code": lang.code,
        "name_en": lang.name_en,
        "name_native": lang.name_native,
        "rtl": lang.rtl,
        "is_ui_lang": lang.is_ui_lang,
        "is_target": lang.is_target,
    }


@router.get("")
async def list_languages(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Language).where(Language.is_active == True))
    langs = result.scalars().all()
    return ok({"languages": [lang_to_dict(l) for l in langs]})


@router.get("/{code}")
async def get_language(code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Language).where(Language.code == code, Language.is_active == True))
    lang = result.scalar_one_or_none()
    if not lang:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Language")
    return ok(lang_to_dict(lang))
