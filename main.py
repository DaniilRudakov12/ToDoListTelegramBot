import asyncio

from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import async_sessionmaker

from database.models import async_main, engine
from handlers import router
from notification import notify_deadlines

bot = Bot(token='YOUR BOT FATHER TOKEN')
dp = Dispatcher()

async def main():
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    dp.include_router(router)
    await async_main()
    await dp.start_polling(bot)
    asyncio.create_task(notify_deadlines(bot, async_session_maker))

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")