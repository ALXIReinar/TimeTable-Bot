from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Awaitable, Any, Dict

from core.data.postgres import PgSql
from asyncpg import pool


class PgPoolMiddleware(BaseMiddleware):
    def __init__(self, pool_connect: pool.Pool):
        super().__init__()
        self.connection = pool_connect

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> None:
        async with self.connection.acquire() as connection:
            data['psql_pool'] = PgSql(connection)
            return await handler(event, data)