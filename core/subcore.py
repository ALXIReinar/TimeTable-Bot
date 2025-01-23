from aiogram import Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties

from core.commands import set_my_commands
from core.data.postgres import PgSql
from core.config import ADMIN_ID, TOKEN, HELP


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))


async def on_startup():
    await bot.send_message(ADMIN_ID, 'Бот запущен!', reply_markup=ReplyKeyboardRemove())

async def start(message: Message, state: FSMContext, db: PgSql):
    await message.answer(f'Привет, {message.from_user.first_name}\n'
                         f'Я тот, кто будет напоминать, куда и когда тебе идти🗓\n'
                         f'/ttable_add - Добавить расписание\n'
                         f'/ttable_update - Обновить расписание')
    tg_id = message.from_user.id
    name = f'{message.from_user.first_name} {message.from_user.last_name}'
    await db.add_user(tg_id, name)
    await set_my_commands(bot)

    await state.update_data(activity='command')


async def bot_help(message: Message):
    await message.answer(HELP)