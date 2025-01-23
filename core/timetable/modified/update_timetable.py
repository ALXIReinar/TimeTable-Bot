from datetime import datetime

from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from core.timetable.modified.show_timetable import show_ttable
from core.utils.keyboards import get_cancel
from core.utils.state_machine import SaveSteps
from core.data.postgres import PgSql


async def ttable_update_or_add(message: Message, state: FSMContext, db: PgSql):
    day_sent = (await db.free_request(
        'SELECT day_sent FROM "tTable" WHERE "group" = (SELECT "group" FROM users WHERE tg_id = $1) ORDER BY id DESC LIMIT 1',
        message.chat.id))[0]['day_sent']


    "Определение Запроса в БД"
    if  datetime.now().date() < day_sent:
        signature = 'Текущее расписание на {}:\n\n{}'
        answer = f"Введи новое расписание на {day_sent.strftime('%d/%m/%Y')}"
        await state.update_data(update=day_sent)
    else:
        signature = 'Старое расписание на {}:\n\n{}'
        answer = 'Сначала добавь расписание на следующий учебный день\n\nВведите текст'


    "Отправка ч.1"
    await state.update_data(caption=signature)
    await show_ttable(message, state, db)

    "Отправка ч.2"
    await message.answer(answer, reply_markup=get_cancel())
    await state.set_state(SaveSteps.GET_TIMETABLE)
