from aiogram import Bot
from aiogram.types import BotCommandScopeDefault, BotCommand


async def set_my_commands(bot: Bot):
    commands = [
        BotCommand(command='/start', description='Запуск бота'),
        BotCommand(command='/ttable_show', description='Посмотреть расписание'),
        BotCommand(command='/ttable_add', description='Добавить расписание'),
        BotCommand(command='/ttable_update', description='Обновить имеющееся расписание'),
        BotCommand(command='/default_ttable_show', description='Посмотреть основное расписание'),
        BotCommand(command='/default_ttable_add', description='Добавить основное расписание'),
        BotCommand(command='/default_ttable_update', description='Обновить основное расписание'),
        BotCommand(command='/edit_group', description='Изменить группу'),
        BotCommand(command='/help', description='Помощь')
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
