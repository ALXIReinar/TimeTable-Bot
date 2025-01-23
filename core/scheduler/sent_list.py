import asyncio

from aiogram.types import FSInputFile
from asyncpg import pool, UndefinedTableError

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter

from core.config import ADMIN_ID
from core.data.postgres import PgSql
from core.utils.need_format import get_group_structure, get_group_structure_spec


class SentList:
    def __init__(self, bot: Bot, connection: pool.Pool):
        self.bot = bot
        self.db = PgSql(connection)


    async def table_management(self):
        try:
            await self.db.drop_table()
            await self.db.create_table()
        except UndefinedTableError:
            await self.db.create_table()

        finally:
            await self.db.restore_table()


    async def send_message(self, chat_id, text, photo=None):
        try:
            if photo:
                pic = FSInputFile(photo)
                await self.bot.send_photo(chat_id, pic, caption=text)
            else:
                await self.bot.send_message(chat_id, text)

        except TelegramForbiddenError:
            await self.db.set_status('users', chat_id, 'banned')
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            return self.send_message(chat_id, text, photo)
        except Exception as e:
            await self.db.set_status('users', chat_id, 'exception')
            await self.bot.send_message(ADMIN_ID, f'#логи\n\n{chat_id}\n{e}')

        else:
            return True

        return False



    async def morning_ttable(self):
        await self.table_management()

        groups_ttable = await self.db.morning_processing()
        total_groups = get_group_structure_spec([record['group'] for record in groups_ttable])

        ids = await self.db.groupmates_PostProcess()

        total = len(ids)
        count = 0

        "Пробегаемся по каждому Человеку"
        for i in range(total):
            "Ищем его группу, чтобы отправить ему расписание этой группы"
            for group_tt in total_groups:
                if ids[i]['group'] == group_tt[0]:
                    text = 'Проверь расписание!\nЕго никто не прислал('
                    photo = None
                    if group_tt[1]:
                        data = await self.db.morning_layout(group_tt[0])
                        text = data[0][0]
                        photo = data[0][1]

                    if await self.send_message(ids[i]['tg_id'], text, photo):
                        count += 1
                    await asyncio.sleep(.05)
                    "Чтобы сократить время, выходим из цикла, когда закончили отправку для этого Человека"
                    break

        await self.bot.send_message(ADMIN_ID,
                                    f'На рассылке\n'
                                    f'Отправлено {count} сообщений из {total}')


    async def sent_remind(self):
        await self.table_management()

        "Вычисляем группы, не отправившие расписание на завтра"
        friends = await self.db.reminder_friends()
        posting_enemies = get_group_structure()
        for _group in friends:
            posting_enemies.remove(_group)

        "Получаем участников таких групп"
        id_list = []
        for group in posting_enemies:
            ids = await self.db.groupmates_Reminding(group)
            id_list.extend(ids)

        total = len(id_list)
        count = 0

        "Напоминаем, чтобы отправили расписание"
        for tg_id in id_list:
            if await self.send_message(tg_id, f'Нет расписания на следующий день\n\nНапоминалка работает с 18 до 22 Настроить рассылку - /ttable_conf'):
                count += 1
            await asyncio.sleep(.05)

        await self.bot.send_message(ADMIN_ID,
                                    f'На рассылке\n'
                                         f'Отправлено {count} сообщений из {total}', disable_notification=True)
