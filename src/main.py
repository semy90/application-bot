import asyncio
import contextlib
import logging
import os

from aiogram import Bot, Dispatcher


from bot.handlers import include_routers
from bot.middlewares import include_middlewares
from database.session import init_db
from bot.handlers.admin import include_admin_routers
from bot.handlers.contact import include_contact_routers


async def main():
    bot = Bot(token=os.getenv("TOKEN"))
    dp = Dispatcher()

    settings = {"path": "../database.sqlite3"}
    session_maker = await init_db(settings)

    include_middlewares(dp, session_maker)

    include_contact_routers(dp)
    include_admin_routers(dp)
    include_routers(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, session_maker=session_maker)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(main())
