from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardBuilder
from core.config import ADMIN_ID


def get_cancel():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text='Без текста')],
        [KeyboardButton(text='По основному')],
        [KeyboardButton(text='Отменить действие')]
    ])
    return markup

def get_cancel_shorted():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text='Отменить действие')]
    ])
    return markup

def group_list():
    "Клава всех групп из Н-ного кол-ва строк и 4 столбцов"
    markup = InlineKeyboardBuilder()
    layout = ''
    row_count = 0

    with open('./group_structure.txt', 'rt', encoding='utf-8') as file:
        for line in file:
            line = line.replace('\n', '')
            markup.button(text=line, callback_data=f'group_{line}')
            if row_count == 4:
                layout += str(row_count)
                row_count = 0
            row_count += 1
        layout += str(row_count)

    markup.button(text='Пиши, если нет твоей группы', url=f'tg://user?id={ADMIN_ID}')
    markup.button(text='Отмена❌', callback_data='cancel')

    tupl = tuple(map(int, layout))
    markup.adjust(*tupl, 2)
    return markup.as_markup()


def confirm_group_kb(group):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Выбрать другую❌', callback_data='reject'),
            InlineKeyboardButton(text='Подтвердить✅', callback_data=f'confirm_{group}')
        ]
    ])
    return markup

def kb_addinger(tg_id):
    markup = InlineKeyboardBuilder()
    markup.button(text='Добавил расписание👀',  url=f'tg://user?id={tg_id}')
    return markup.as_markup()
