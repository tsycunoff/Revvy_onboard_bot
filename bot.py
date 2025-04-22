import logging
from aiogram import Bot, Dispatcher, executor, types
import os

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "dummy_token")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Бот работает!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
