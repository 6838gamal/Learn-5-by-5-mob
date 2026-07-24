"""AI Conversation service — STT, chat, TTS, feedback."""
from datetime import datetime, date, timezone

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import SubscriptionRequiredError, AppException
from app.models.ai import AIConversation, AIMessage


class AIService:
    SYSTEM_PROMPT_TEMPLATE = """
You are a friendly, encouraging language tutor helping a learner practice {language}.
Today's lesson words are: {words}.
Current scenario: {scenario}.

Your job:
1. Conduct a natural conversation using today's words.
2. Gently correct grammatical errors by providing the correct form in parentheses.
3. Encourage the user and praise correct usage of today's words.
4. Keep responses concise (2-3 sentences max) to maintain conversation flow.
5. Return corrections as JSON in this format: [{"original": "...", "corrected": "...", "explanation": "..."}]
   Include this JSON at the end of your message wrapped in <corrections></corrections> tags.
""".strip()

    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def start_conversation(
        self,
        user_id: str,
        language_id: int,
        language_name: str,
        today_words: list[str],
        scenario_id: int | None,
        scenario_title: str | None,
        lesson_date: date | None,
    ) -> AIConversation:
        conversation = AIConversation(
            user_id=user_id,
            language_id=language_id,
            scenario_id=scenario_id,
            lesson_date=lesson_date,
            status="active",
        )
        self.db.add(conversation)

        # Initial AI greeting
        system_prompt = self.SYSTEM_PROMPT_TEMPLATE.format(
            language=language_name,
            words=", ".join(today_words),
            scenario=scenario_title or "Free conversation",
        )
        greeting_response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Hello, I'm ready to practice!"},
            ],
        )
        greeting_text = greeting_response.choices[0].message.content

        greeting_msg = AIMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=greeting_text,
        )
        self.db.add(greeting_msg)
        await self.db.flush()
        return conversation

    async def process_audio_message(
        self,
        conversation: AIConversation,
        audio_bytes: bytes,
        language_name: str,
        today_words: list[str],
        scenario_title: str | None,
    ) -> dict:
        # 1. Transcribe audio
        import io
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.webm"
        transcript_response = await self.client.audio.transcriptions.create(
            model=settings.OPENAI_STT_MODEL,
            file=audio_file,
        )
        user_text = transcript_response.text

        # Save user message
        user_msg = AIMessage(conversation_id=conversation.id, role="user", content=user_text)
        self.db.add(user_msg)

        # 2. Get history for context
        history = [
            {"role": m.role, "content": m.content}
            for m in conversation.messages
        ]
        history.append({"role": "user", "content": user_text})

        # 3. Generate AI reply
        system_prompt = self.SYSTEM_PROMPT_TEMPLATE.format(
            language=language_name,
            words=", ".join(today_words),
            scenario=scenario_title or "Free conversation",
        )
        ai_response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "system", "content": system_prompt}] + history,
        )
        ai_text_raw = ai_response.choices[0].message.content

        # Parse corrections from XML tags
        import re, json
        corrections = []
        corrections_match = re.search(r"<corrections>(.*?)</corrections>", ai_text_raw, re.DOTALL)
        ai_text = re.sub(r"<corrections>.*?</corrections>", "", ai_text_raw, flags=re.DOTALL).strip()
        if corrections_match:
            try:
                corrections = json.loads(corrections_match.group(1).strip())
            except Exception:
                pass

        # 4. Generate TTS audio
        tts_response = await self.client.audio.speech.create(
            model=settings.OPENAI_TTS_MODEL,
            voice=settings.OPENAI_TTS_VOICE,
            input=ai_text,
        )
        audio_content = tts_response.content
        # TODO: upload audio_content to storage, return URL
        audio_url = None  # Placeholder — wire up storage service

        # Save AI message
        ai_msg = AIMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_text,
            audio_url=audio_url,
            corrections=corrections if corrections else None,
        )
        self.db.add(ai_msg)
        await self.db.flush()

        return {
            "user_transcript": user_text,
            "ai_text": ai_text,
            "ai_audio_url": audio_url,
            "corrections": corrections,
        }

    async def end_conversation(self, conversation: AIConversation) -> dict:
        # Generate end-of-session feedback
        history_text = "\n".join(
            f"{m.role.upper()}: {m.content}" for m in conversation.messages
        )
        feedback_prompt = f"""
Review this language learning conversation and provide JSON feedback:
{{
  "score": <0-100>,
  "summary": "<brief overall assessment>",
  "strengths": ["<point>"],
  "errors": [{{"original": "...", "corrected": "...", "explanation": "..."}}],
  "suggestions": ["<improvement tip>"],
  "encouragement": "<motivating closing message>"
}}

Conversation:
{history_text}
""".strip()

        feedback_response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": feedback_prompt}],
            response_format={"type": "json_object"},
        )
        import json
        feedback = json.loads(feedback_response.choices[0].message.content)

        conversation.status = "completed"
        conversation.ai_feedback = json.dumps(feedback)
        conversation.score = feedback.get("score", 0)
        conversation.ended_at = datetime.now(timezone.utc)
        if conversation.started_at:
            conversation.duration_secs = int(
                (conversation.ended_at - conversation.started_at).total_seconds()
            )
        await self.db.flush()
        return feedback
