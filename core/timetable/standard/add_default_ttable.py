import os

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from core.subcore import bot
from core.data.postgres import PgSql
from core.utils.state_machine import SaveSteps
from core.utils.keyboards import get_cancel_shorted


async def get_add_standard_flag(message: Message, state: FSMContext):
    await message.answer('Пришли основное расписание своей группы', reply_markup=get_cancel_shorted())
    await state.set_state(SaveSteps.ADD_STANDARD)


async def add_standard_ttable(message: Message, state: FSMContext, db: PgSql):
    addinger = message.chat.id
    if message.text == 'Отменить действие':
        await message.answer("Отменено", reply_markup=ReplyKeyboardRemove())
    else:
        if message.photo and not message.media_group_id:
            group = (await db.check_group(addinger))[0][0]

            file_id = message.photo[-1].file_id
            wrap_file = await bot.get_file(file_id)
            photo = await bot.download_file(wrap_file.file_path)
            f_extension = os.path.splitext(wrap_file.file_path)[-1]
            root_path = f'./images/standard_ttable/' + group + f_extension
            with open(root_path, 'wb') as f:
                f.write(photo.read())
            await db.add_default_ttable(root_path, group, addinger)

            answer = 'Выполнено!'
        elif message.media_group_id:
            answer = 'Отправь только одно фото'
        else:
            answer = 'Отправь только фото'
        await message.answer(answer)

    await state.clear()
