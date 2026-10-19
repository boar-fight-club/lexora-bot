import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web
from dotenv import load_dotenv
import requests

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def translate_text(text: str, target_lang: str) -> str:
  """Прямой и стабильный запрос к Google Translate без лимитных библиотек"""
  url = "https://translate.googleapis.com/translate_a/single"
  params = {"client": "gtx", "sl": "auto", "tl": target_lang, "dt": "t", "q": text}
  try:
    response = requests.get(url, params=params, timeout=5)
    if response.status_code == 200:
      data = response.json()
      # Собираем переведенный текст из кусочков
      return "".join([item[0] for item in data[0] if item[0]])
  except Exception as e:
    logging.error(f"Ошибка запроса перевода: {e}")
  return None


@dp.message(CommandStart())
async def start_handler(message: types.Message):
  await message.answer(
      "Привет! Я бот-переводчик (Русский ↔ Английский).\n\n"
      "Отправь текст на русском — переведу на английский.\n"
      "Отправь текст на английском — переведу на русский!"
  )


@dp.message()
async def translate_handler(message: types.Message):
  text = message.text
  if not text:
    return

  try:
    # Пробуем перевести на английский
    translated = translate_text(text, "en")

    # Если текст не изменился (или вернулся пустым), значит он уже на английском — переводим на русский
    if not translated or translated.strip().lower() == text.strip().lower():
      translated = translate_text(text, "ru")

    if translated:
      await message.answer(translated)
    else:
      await message.answer(
          "К сожалению, не удалось перевести сообщение. Попробуйте еще раз."
      )
  except Exception as e:
    logging.error(f"Ошибка: {e}")
    await message.answer(
        "К сожалению, не удалось перевести сообщение. Попробуйте еще раз."
    )


# Заглушка веб-сервера для Render Free Web Service
async def handle(request):
  return web.Response(text="Bot is running!")


async def main():
  app = web.Application()
  app.router.add_get("/", handle)
  runner = web.AppRunner(app)
  await runner.setup()
  port = int(os.environ.get("PORT", 8080))
  site = web.TCPSite(runner, "0.0.0.0", port)
  await site.start()

  print("Бот и веб-сервер запущены!")
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())