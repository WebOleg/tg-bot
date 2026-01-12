import asyncio
import logging
logging.basicConfig(level=logging.INFO)

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import BOT_TOKEN
from database import init_db

from handlers.add_transaction import router as add_router
from handlers.view_stats import router as stats_router
from handlers.forecast import router as forecast_router
from handlers.start import router as start_router


async def set_bot_commands(bot: Bot):
    """Налаштування команд меню бота"""
    commands = [
        BotCommand(command="/start", description="Запустити бота / показати меню"),
        BotCommand(command="/menu", description="Показати головне меню"),
        BotCommand(command="/help", description="Допомога"),
    ]
    await bot.set_my_commands(commands)


async def main():
    logging.info("Бот запускається...")

    # Ініціалізація бази даних
    init_db()

    # Створення бота та диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Налаштування команд меню
    await set_bot_commands(bot)

    # Підключення роутерів
    dp.include_router(start_router)
    dp.include_router(add_router)
    dp.include_router(stats_router)
    dp.include_router(forecast_router)

    logging.info("Бот запущено і очікує повідомлення")

    # Запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
