from datetime import datetime

from aiogram import Bot

from arq import run_worker
from arq.cron import cron
from arq.connections import RedisSettings

from core.config import TOKEN, pool_settings, ARQ_REDIS_HOST
from core.scheduler.sent_list import SentList



async def startup(ctx):
    ctx['bot'] = Bot(token=TOKEN)
    ctx['mailing'] = SentList(ctx['bot'], await pool_settings())

async def shutdown(ctx):
    await ctx['bot'].session.close()


async def ttable_reminder(ctx):
    "Напоминалка"
    mailing = ctx['mailing']
    if datetime.now().hour in range(18, 22):
        await mailing.sent_remind()

async def morning_sent(ctx):
    "Утренняя рассылка"
    mailing = ctx['mailing']
    if datetime.now().weekday() != 6:
        await mailing.morning_ttable()


class WorkerSettings:
    redis_settings = RedisSettings(host=ARQ_REDIS_HOST)
    on_startup = startup
    on_shutdown = shutdown
    cron_jobs = [
        cron(morning_sent, second={0,30}),
        cron(ttable_reminder, second={15,45})
        # cron(morning_sent, hour=6, minute=15),
        # cron(ttable_reminder, hour={18, 19, 20, 21, 22})
    ]

run_worker(WorkerSettings)
