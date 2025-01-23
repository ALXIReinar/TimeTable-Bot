from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext

from core.data.postgres import PgSql
from core.utils.keyboards import kb_addinger


async def show_ttable(message: Message, state: FSMContext, db: PgSql):
    data = await db.fresh_ttable_group(message.chat.id)
    ttable = data[0][0]
    photo = data[0][1]
    date = data[0][2]
    addinger = data[0][3]

    reply_kb = kb_addinger(addinger)
    d_m_y = date.strftime('%d/%m/%Y')

    preform = (await state.get_data()).get('caption')
    if not preform:
        preform = 'Последнее расписание на {}:\n\n{}'
    answer = preform.format(d_m_y, ttable)

    if photo:
        pic = FSInputFile(path=photo)
        await message.answer_photo(photo=pic, caption=answer, reply_markup=reply_kb)
    else:
        await message.answer(answer, reply_markup=reply_kb)
