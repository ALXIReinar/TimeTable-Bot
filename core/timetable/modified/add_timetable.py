import os
from datetime import datetime, timedelta

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from core.subcore import bot
from core.data.postgres import PgSql
from core.timetable.modified.show_timetable import show_ttable

from core.utils.state_machine import SaveSteps
from core.utils.keyboards import get_cancel
from core.utils.decorators import CancelActivity
from core.utils.action_analyze import action_analyzer
from core.utils.need_format import text_processing, day_sent_appointer




async def get_flag(message: Message, state: FSMContext, db: PgSql):
    await state.set_data({})
    ttable_date_sent = await db.ttable_timestamp(message.chat.id)
    add_time = ttable_date_sent[0][0]
    now = datetime.now().date()

    if add_time == now:
        await message.answer("Расписание на следующий учебный день уже было добавлено!")
        await show_ttable(message, state, db)
    else:
        await message.answer("Пришли расписание", reply_markup=get_cancel())
        await state.set_state(SaveSteps.GET_TIMETABLE)


@CancelActivity
async def get_timetable(message: Message, state: FSMContext, db: PgSql):
    chat_id = message.chat.id
    text = f'\n\nРасписание внесено, жди уведомление примерно в 6:30⏰'

    answer, log_mes = '', ''
    group = (await db.check_group(message.chat.id))[0][0]
    day_sent = day_sent_appointer()

    if message.text:

        if message.text == 'По основному':
            photo = await db.default_ttable(group)
            if not len(photo):
                photo = None
                text = ''
                log_mes = 'Для твоей группы ещё не добавлено стандартное расписание\nДобавить его - /add_default_ttable'
            else:
                photo = photo[0][0]
        else:
            photo = None
            answer, log_mes = text_processing(message.text)
        if not log_mes:
            await action_analyzer(state, db, addinger=chat_id, day_sent=day_sent, group=group, answer=answer, photo=photo)
        else:
            await message.answer('Не удалось добавить расписание')
            text = ''


    elif message.photo and not message.media_group_id:
        if message.caption:
            answer, log_mes = text_processing(message.caption)

        file_id = message.photo[-1].file_id
        wrap_file = await bot.get_file(file_id)
        photo = await bot.download_file(wrap_file.file_path)
        f_extension = os.path.splitext(wrap_file.file_path)[-1]
        root_path = f'./images/daily/' + f'{day_sent.strftime("%Y-%m-%d")[:10]}_{group}' + f_extension
        with open(root_path, 'wb') as f:
            f.write(photo.read())

        await action_analyzer(state, db, addinger=chat_id, day_sent=day_sent, group=group, answer=answer, photo=root_path)
    else:
        text = ''
        log_mes = 'Можно добавить только одно фото'

    await state.clear()
    await message.answer(log_mes + text, reply_markup=ReplyKeyboardRemove())
