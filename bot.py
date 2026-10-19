import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web
from dotenv import load_dotenv
from translate import Translator

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


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
    # Пробуем перевести с русского на английский
    translator_to_en = Translator(from_lang="ru", to_lang="en")
    translated_text = translator_to_en.translate(text)

    # Если текст не изменился, значит, он был на английском — переводим на русский
    if translated_text.strip().lower() == text.strip().lower():
      translator_to_ru = Translator(from_lang="en", to_lang="ru")
      translated_text = translator_to_ru.translate(text)

    await message.answer(translated_text)
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