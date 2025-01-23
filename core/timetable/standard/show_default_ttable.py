from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext

from core.data.postgres import PgSql
from core.utils.keyboards import kb_addinger


async def show_default(message: Message, state: FSMContext, db: PgSql):
    group = (await db.check_group(message.chat.id))[0][0]
    ttable = await db.default_ttable(group)
    reply_kb = kb_addinger(ttable[0][1])

    if len(ttable):
        photo = FSInputFile(ttable[0][0])
        await message.answer_photo(photo, reply_markup=reply_kb)
    else:
        await message.answer('У твоей группы не добавлено основное расписание - /add_default_ttable', reply_markup=reply_kb)
