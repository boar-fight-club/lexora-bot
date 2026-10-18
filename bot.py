import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from googletrans import Translator

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
translator = Translator()


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
    # Убираем await, так как в этой версии googletrans перевод синхронный
    translated = translator.translate(text, dest="en")

    # Если текст уже был на английском, переводим на русский
    if (
        translated.src == "en"
        or translated.text.strip().lower() == text.strip().lower()
    ):
      translated = translator.translate(text, dest="ru")

    await message.answer(translated.text)
  except Exception as e:
    logging.error(f"Ошибка: {e}")
    await message.answer(
        "К сожалению, не удалось перевести сообщение. Попробуйте еще раз."
    )


async def main():
  print("Бот запущен!")
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())