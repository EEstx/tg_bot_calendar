# Telegram Calendar Bot

Telegram-бот секретарь — создаёт события в Google Calendar из сообщений на естественном языке.

Пишешь боту `Поставь на завтра в 14:00 встречу с Иваном` — он парсит сообщение через LLM и добавляет событие в календарь.

## Стек

- **aiogram 3** — Telegram Bot API
- **Google Calendar API** — создание событий
- **OpenRouter** (arcee-ai/trinity-large-preview:free) — парсинг естественного языка в структурированные данные

## Установка

```bash
pip install -r requirements.txt
```

Скопировать `.env.example` → `.env` и заполнить значения:

```bash
cp .env.example .env
```

## Настройка Google Calendar API

1. Перейти в [Google Cloud Console](https://console.cloud.google.com)
2. Создать новый проект (или выбрать существующий)
3. Включить **Google Calendar API**:
   - `APIs & Services` → `Library` → найти `Google Calendar API` → `Enable`
4. Настроить **OAuth consent screen**:
   - `APIs & Services` → `OAuth consent screen`
   - Тип: `External`
   - Заполнить название приложения и email
   - Во вкладке **Test users** добавить свой Gmail-адрес
5. Создать **OAuth 2.0 credentials**:
   - `APIs & Services` → `Credentials` → `Create Credentials` → `OAuth client ID`
   - Тип приложения: `Desktop app`
   - Скачать JSON и сохранить как `credentials.json` в корень проекта
6. При первом запуске бота откроется браузер для авторизации — после подтверждения создастся `token.json`

## Настройка OpenRouter

1. Зарегистрироваться на [openrouter.ai](https://openrouter.ai)
2. Получить API-ключ: [openrouter.ai/keys](https://openrouter.ai/keys)
3. Вписать ключ в `.env` → `OPENROUTER_API_KEY`

## Настройка Telegram бота

1. Создать бота через [@BotFather](https://t.me/BotFather)
2. Скопировать токен в `.env` → `TG_BOT_TOKEN`

## Запуск

```bash
python main.py
```

## Файлы

| Файл | Описание |
|---|---|
| `main.py` | Точка входа, хендлеры Telegram-бота |
| `llm_parser.py` | Парсинг сообщений через OpenRouter LLM |
| `calendar_service.py` | Интеграция с Google Calendar API |
| `credentials.json` | OAuth-ключи Google (не коммитить!) |
| `token.json` | Авторизационный токен (не коммитить!) |
