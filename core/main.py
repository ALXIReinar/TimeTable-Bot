import asyncio

from arq import create_pool

from aiogram import Dispatcher
from aiogram.filters import Command

from arq.connections import RedisSettings

from core.subcore import start, on_startup, bot, bot_help
from core.middlewares.postgres_middleware import PgPoolMiddleware
from core.middlewares.command_middleware import Middleware_CheckGroupCommand
from core.callback_main import call_hub
from core.data.postgres import PgSql
from core.scheduler.sent_list import SentList
from core.timetable.group_actions import group_is_null
from core.timetable.standard.add_default_ttable import get_add_standard_flag, add_standard_ttable
from core.timetable.standard.show_default_ttable import show_default
from core.timetable.modified import add_timetable, show_timetable, update_timetable
from core.utils.state_machine import SaveSteps
from core.config import pool_settings, ARQ_REDIS_HOST


dp = Dispatcher()


async def main():
    pool_connect = await pool_settings()
    arq_connect = await create_pool(RedisSettings(host=ARQ_REDIS_HOST))

    "Миддлвари"
    dp.update.middleware.register(PgPoolMiddleware(pool_connect))
    dp.message.middleware.register(Middleware_CheckGroupCommand(pool_connect))

    "Простые команды"
    dp.message.register(start, Command(commands='start'))
    dp.message.register(show_timetable.show_ttable, Command(commands="ttable_show"))
    dp.message.register(group_is_null, Command(commands='edit_group'))
    dp.message.register(bot_help, Command(commands='help'))

    "Расписание"
    dp.message.register(show_default, Command(commands='default_ttable_show'))
    dp.message.register(add_timetable.get_flag, Command(commands="ttable_add"))
    dp.message.register(update_timetable.ttable_update_or_add, Command(commands='ttable_update'))
    dp.message.register(get_add_standard_flag, Command(commands=['default_ttable_add', 'default_ttable_update']))
    dp.message.register(add_timetable.get_timetable, SaveSteps.GET_TIMETABLE)
    dp.message.register(add_standard_ttable, SaveSteps.ADD_STANDARD)

    "Колл-беки"
    dp.callback_query.register(call_hub)

    dp.startup.register(on_startup)
    await dp.start_polling(
        bot,
        db=PgSql(pool_connect),
        allowed_updates=dp.resolve_used_update_types(),
        arqredis=arq_connect,
        mailing=SentList(bot, pool_connect)
    )

if __name__ == '__main__':
    asyncio.run(main())
