from aiogram.types import Message, CallbackQuery

from core.data.postgres import PgSql
from core.subcore import bot
from core.utils.keyboards import group_list, confirm_group_kb



async def group_is_null(message: Message):
    "Предоставление выбора"
    await message.answer("Найди свою группу", reply_markup=group_list())


async def confirm_group(call: CallbackQuery):
    "Предосмотр выбранной группы"
    await bot.delete_message(call.message.chat.id, call.message.message_id-1)
    split_call = call.data.split('_')
    group = split_call[1]
    await call.message.answer(f'Ты выбрал - {group}', reply_markup=confirm_group_kb(group))
    await call.answer()


async def accept_group(call: CallbackQuery, db: PgSql):
    "Действия после подтверждения выбора"
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    tg_id = call.message.chat.id
    group = call.data.split('_')[1]

    await db.add_group(group, tg_id)

    await call.message.answer('Выполнено!')
    await call.answer()
