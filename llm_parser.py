import os
import json
import httpx
from datetime import datetime

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "arcee-ai/trinity-large-preview:free"

SYSTEM_PROMPT = """Ты — ассистент-секретарь. Твоя задача — извлечь из сообщения пользователя информацию о событии для Google Calendar.

Текущая дата и время: {current_datetime}

Ты ДОЛЖЕН вернуть ТОЛЬКО валидный JSON-объект (без markdown, без пояснений, без ```json) со следующими полями:
- "summary": краткое название события (строка)
- "description": описание события, если есть (строка, может быть пустой)
- "start": дата и время начала в формате ISO 8601, например "2026-02-28T14:00:00" (строка)
- "end": дата и время окончания в формате ISO 8601 (строка). Если длительность не указана, поставь +1 час от начала.

Примеры:
Пользователь: "Поставь на завтра в 14:00 встречу с Иваном"
Ответ: {{"summary": "Встреча с Иваном", "description": "", "start": "2026-02-28T14:00:00", "end": "2026-02-28T15:00:00"}}

Пользователь: "Запланируй на 5 марта с 10 до 12 презентацию проекта"
Ответ: {{"summary": "Презентация проекта", "description": "", "start": "2026-03-05T10:00:00", "end": "2026-03-05T12:00:00"}}

Верни ТОЛЬКО JSON, без каких-либо дополнительных символов или пояснений."""


async def parse_event(user_message: str) -> dict | None:
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set")

    current_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S, %A")
    system_prompt = SYSTEM_PROMPT.format(current_datetime=current_dt)

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.1,
        "max_tokens": 500,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(OPENROUTER_URL, json=payload, headers=headers)
        response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"].strip()

    if content.startswith("```"):
        content = content.split("\n", 1)[-1]
    if content.endswith("```"):
        content = content.rsplit("```", 1)[0]
    content = content.strip()

    try:
        event_data = json.loads(content)
    except json.JSONDecodeError:
        return None

    if not {"summary", "start", "end"}.issubset(event_data.keys()):
        return None

    return event_data
