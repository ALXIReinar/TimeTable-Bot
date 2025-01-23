from aiogram.types import CallbackQuery

from core.data.postgres import PgSql
from core.subcore import bot
from core.timetable.group_actions import confirm_group, accept_group, group_is_null


async def call_hub(call: CallbackQuery, db: PgSql):
    if 'group' in call.data:
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await confirm_group(call)

    elif 'confirm' in call.data:
        await accept_group(call, db)
    elif call.data == 'reject':
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await group_is_null(call.message)
        await call.answer()
    elif call.data == 'cancel':
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await call.answer()

    else:
        await call.answer()