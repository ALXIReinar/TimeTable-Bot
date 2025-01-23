from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from core.data.postgres import PgSql
from core.utils.no_text_variant import no_text


def CancelActivity(func):
    async def wrapper(message: Message, state: FSMContext, db: PgSql):
        if message.text == 'Отменить действие':
            await message.answer('Действие отменено',
                                 reply_markup=ReplyKeyboardRemove())
            await state.clear()
        elif message.text == 'Без текста':
            await state.set_state(state=None)
            await no_text(message, state)
        else:
            await func(message, state, db)
    return wrapper
