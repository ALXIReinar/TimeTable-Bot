from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from core.utils.state_machine import SaveSteps


async def no_text(message: Message, state: FSMContext):
    await message.answer('*Только фото*', reply_markup=ReplyKeyboardRemove())
    await state.set_state(SaveSteps.GET_TIMETABLE)
