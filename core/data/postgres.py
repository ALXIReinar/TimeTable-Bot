from typing import List
from asyncpg import pool, Record

class PgSql:
    """
    users(id, tg_id, name, group, status)
    tTable(id, lessons, ttable_photo, add_time, day_sent, addinger)
    mailing(id, tg_id, group, status)
    default_ttable(id, ttable_photo, group, addinger)
    """
    def __init__(self, connection: pool.Pool):
        self.cursor = connection

    """
    USERS PROCEDURES
    """
    async def add_user(self, tg_id, name):
        async with self.cursor.acquire() as conn:
            query = "INSERT INTO users (tg_id, name) VALUES($1,$2) ON CONFLICT (tg_id) DO UPDATE SET name = $2"
            await conn.execute(query.format(), tg_id, name)

    async def check_group(self, tg_id):
        async with self.cursor.acquire() as conn:
            query = 'SELECT "group" FROM users WHERE tg_id = $1'
            res: List[Record] = await conn.fetch(query, tg_id)
            return res

    async def add_group(self, group, tg_id):
        async with self.cursor.acquire() as conn:
            query = 'UPDATE users SET "group" = $1 WHERE tg_id = $2'
            await conn.execute(query, group, tg_id)

    """
    TABLE_PROCEDURES    
    """
    async def fresh_ttable_group(self, tg_id):
        async with self.cursor.acquire() as conn:
            query = 'SELECT lessons, ttable_photo, day_sent, addinger FROM "tTable" WHERE "group" = (SELECT "group" FROM users WHERE tg_id = $1) ORDER BY id DESC LIMIT 1'
            res: List[Record] = await conn.fetch(query, tg_id)
            return res

    async def ttable_timestamp(self, tg_id):
        async with self.cursor.acquire() as conn:
            query = 'SELECT add_time FROM "tTable" WHERE "group" = (SELECT "group" FROM users WHERE tg_id = $1) ORDER BY id DESC LIMIT 1'
            res: List[Record] = await conn.fetch(query, tg_id)
            return res

    async def add_ttable(self, text, ttable_photo, day_sent, group, addinger):
        async with self.cursor.acquire() as conn:
            query = 'INSERT INTO "tTable" (lessons, ttable_photo, day_sent, "group", addinger) VALUES($1,$2,$3,$4,$5)'
            await conn.execute(query, text, ttable_photo, day_sent, group, addinger)

    async def update_ttable(self, lessons, photo_path, addinger, group, day_sent):
        async with self.cursor.acquire() as conn:
            query = 'UPDATE "tTable" SET lessons = $1, ttable_photo = $2, addinger = $3 WHERE "group" = $4 AND day_sent = $5'
            await conn.execute(query, lessons, photo_path, addinger, group, day_sent)

    async def add_default_ttable(self, photo_path, group, addinger):
        async with self.cursor.acquire() as conn:
            query = 'INSERT INTO default_ttable (ttable_photo, "group", addinger) VALUES($1,$2,$3) ON CONFLICT ("group") DO UPDATE SET ttable_photo = $1'
            await conn.execute(query, photo_path, group, addinger)

    async def default_ttable(self, group):
        async with self.cursor.acquire() as conn:
            query = 'SELECT ttable_photo, addinger FROM default_ttable WHERE "group" = $1'
            res: List[Record] = await conn.fetch(query, group)
            return res

    """
    MAILING PROCEDURES
    """
    async def create_table(self):
        async with self.cursor.acquire() as conn:
            query = f'''
CREATE TABLE public.mailing
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    tg_id bigint,
    status text COLLATE pg_catalog."default" DEFAULT 'member'::text,
    "group" character varying(10) COLLATE pg_catalog."default",
    CONSTRAINT mailing_pkey PRIMARY KEY (id),
    CONSTRAINT mailing_tg_id_key UNIQUE (tg_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.mailing
    OWNER to postgres;
'''
            await conn.execute(query)


    async def drop_table(self):
        async with self.cursor.acquire() as conn:
            query = f"DROP TABLE mailing"
            await conn.execute(query)

    async def restore_table(self):
        async with self.cursor.acquire() as conn:
            query = f'INSERT INTO mailing (tg_id, "group") SELECT tg_id, "group" FROM users WHERE status = \'member\''
            await conn.execute(query)

    async def reminder_friends(self):
        async with self.cursor.acquire() as conn:
            query = 'SELECT "group" FROM "tTable" WHERE day_sent >= now()::date + interval \'1 day\''
            res: List[Record] = await conn.fetch(query)
            return {record['group'] for record in res}

    async def groupmates_Reminding(self, group):
        async with self.cursor.acquire() as conn:
            query = 'SELECT tg_id FROM mailing WHERE "group" = $1'
            res: List[Record] = await conn.fetch(query, group)
            return [record['tg_id'] for record in res]

    async def groupmates_PostProcess(self):
        async with self.cursor.acquire() as conn:
            query = 'SELECT tg_id, "group" FROM mailing'
            res: List[Record] = await conn.fetch(query)
            return res

    async def morning_processing(self):
        async with self.cursor.acquire() as conn:
            query = 'SELECT "group" FROM "tTable" WHERE day_sent = now()::date'
            res: List[Record] = await conn.fetch(query)
            return res

    async def morning_layout(self, group):
        async with self.cursor.acquire() as conn:
            query = 'SELECT lessons, ttable_photo FROM "tTable" WHERE day_sent = now()::date AND "group" = $1'
            res: List[Record] = await conn.fetch(query, group)
            return res

    async def set_status(self, table_name, tg_id, status):
        async with self.cursor.acquire() as conn:
            query = f"UPDATE {table_name} SET status = $1 WHERE tg_id = $2"
            await conn.execute(query, status, tg_id)


    async def free_request(self, query, *args):
        async with self.cursor.acquire() as conn:
            if "SELECT" in query:
                res: List[Record] = await conn.fetch(query, *args)
                return res
            else:
                await conn.execute(query, *args)
