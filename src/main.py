# main.py
import asyncio
import logging
from bot_config import bot, dp
from database import conn, cursor
from utils import resume_tasks
from handlers import admin, channels, intervals, start_stop
from globals import tasks, previous_prices, last_action_time, last_contract_change_time

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logging.getLogger('aiogram').setLevel(logging.WARNING)

class BadRequestFilter(logging.Filter):
    def filter(self, record):
        return "Bad Request: message is not modified" not in record.getMessage()

logging.getLogger('aiogram.event').addFilter(BadRequestFilter())

async def main():
    logger.info("Запуск..")
    await resume_tasks()
    await dp.start_polling(bot)
    conn.close()
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
