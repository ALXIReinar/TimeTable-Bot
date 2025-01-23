from asyncpg import pool, Record

from typing import List, Callable, Any, Awaitable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from core.timetable.group_actions import group_is_null


class Middleware_CheckGroupCommand(BaseMiddleware):
    def __init__(self, connection: pool.Pool):
        self.cursor = connection

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> None:
        """
        Проверяем параметр группы пользователя на каждый вызов команды
        """
        text = event.text or event.caption or ''
        if text.startswith('/') and text != '/start' and text != '/help':
            async with self.cursor.acquire():
                query = 'SELECT "group" FROM users WHERE tg_id = $1'
                res: List[Record] = await self.cursor.fetch(query, event.chat.id)

            if not res[0][0]:
                await group_is_null(event)
            else:
                return await handler(event, data)

        else:
            return await handler(event, data)
