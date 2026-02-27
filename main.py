import os
import logging
import asyncio
from datetime import datetime

from aiohttp import web
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart

from llm_parser import parse_event
from calendar_service import create_event

load_dotenv()

TOKEN = os.getenv("TG_BOT_TOKEN")
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я твой секретарь-бот. 📅\n\n"
        "Просто напиши мне, какое событие создать, например:\n"
        "• «Поставь на завтра в 14:00 встречу с Иваном»\n"
        "• «Запланируй на 5 марта с 10 до 12 презентацию»\n\n"
        "Я разберу сообщение и добавлю событие в Google Calendar."
    )


@dp.message()
async def handle_message(message: Message):
    if not message.text:
        await message.reply("Пожалуйста, отправь текстовое сообщение.")
        return

    await message.reply("⏳ Обрабатываю запрос...")

    try:
        event_data = await parse_event(message.text)
    except Exception as e:
        logging.error(f"LLM parsing error: {e}")
        await message.reply(f"❌ Ошибка при обработке сообщения через LLM:\n{e}")
        return

    if event_data is None:
        await message.reply(
            "❌ Не удалось распознать событие из сообщения.\n"
            "Попробуй сформулировать иначе, например:\n"
            "«Поставь на завтра в 14:00 встречу с Иваном»"
        )
        return

    summary = event_data.get("summary", "Без названия")
    description = event_data.get("description", "")
    start = event_data["start"]
    end = event_data["end"]

    try:
        created = create_event(
            summary=summary,
            start_iso=start,
            end_iso=end,
            description=description,
        )
    except Exception as e:
        logging.error(f"Google Calendar error: {e}")
        await message.reply(f"❌ Ошибка при создании события в Google Calendar:\n{e}")
        return

    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        start_str = start_dt.strftime("%d.%m.%Y %H:%M")
        end_str = end_dt.strftime("%H:%M")
    except Exception:
        start_str = start
        end_str = end

    link = created.get("htmlLink", "")
    link_line = f'🔗 <a href="{link}">Открыть в Google Calendar</a>' if link else ""
    desc_line = f"📝 {description}\n" if description else ""

    await message.reply(
        f"✅ Событие создано!\n\n"
        f"📌 <b>{summary}</b>\n"
        f"🕐 {start_str} – {end_str}\n"
        f"{desc_line}"
        f"{link_line}",
        parse_mode="HTML",
    )


async def health(_request):
    return web.Response(text="I am alive")


async def main():
    bot = Bot(token=TOKEN)

    app = web.AppRunner(web.Application())
    app.app.router.add_get("/", health)
    await app.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(app, "0.0.0.0", port)
    await site.start()
    logging.info(f"Web server started on port {port}")

    logging.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    asyncio.run(main())