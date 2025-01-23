# 📅 Timetable Bot

![Python ver](https://img.shields.io/badge/pyhon-3.10-orange)
![aiogram](https://img.shields.io/badge/aiogram-3.13.1-blue)
![postgres](https://img.shields.io/badge/postgre-16-42a4ff)
![arq](https://img.shields.io/badge/arq-0.26.1-yellow)

## 💡Main Idea

1. `Users are divided` into `groups`

2. In a timely manner, `one of the users` of his group `sends a timetable` the following day
3. `The bot sends the timetable` at a set time to `all groups` of users who have sent photos/text of their classes. `Or reminds of its absence` so that users can do it on their own

## 👥 Division into groups

> core > middlewares > command_middleware.py

### Tasks📌

1. According to the condition, we do the mailing by groups. This means that we cannot allow an unindentified user to interact with the bot

    * `The task is to check the status before use`

2. We could limit the user's "affiliation" by prohibiting changing the group, but anyone can make a mistake... Or deliberately provoke an uncomfortable situation by posting anything instead of the necessary information :-)

    * `We need a 100% way to identify the author of the timetable`

### Solution🎯

1. ❌We can install `Middleware` , which will check the `users.group` field on each update. However, this will have a "detrimental" effect `due to endless queries in the database`
✅Before
starting to bombard the bot with updates, the User presses commands, since after an unsuccessful check on them, further communication simply ends. Thus, we narrow down the scope of the `Middleware` by registering them only on the `message` and setting the condition:
```py
if text.startswith('/') and text != '/start' and text != '/help':
    async with self.cursor.acquire():
        query = 'SELECT "group" FROM users WHERE tg_id = $1'
        res: List[Record] = await self.cursor.fetch(query, event.chat.id)

    if not res[0][0]:
        # Пользователь должен выбрать группу
        # > core > timetable > groups_actions.py
    else:
        # Даём пользователю зелёный свет
```
2. ✅Here We simply additionally record the Author of the message by tg_id in the table and attach a keyboard with a hyperlink to it

    ![alt text](https://sun9-69.userapi.com/impg/ECk2RcTODh4IWNyLlHPAlBAybOfARqEMYQkK7A/DTL8l4Iqrek.jpg?size=396x594&quality=95&sign=98b4a07c8b49e9a4b247952f8ad3ca23&type=album)

## Timetable 📅

> core > timetable > modified

> core > timetable > standard

### 📃With changes & 📜Standard

Classic operations:
1. Display - `/ttable_show`
2. Adding - `/ttable_add`
3. Change - `/ttable_update`

* `Display`

    ![Congratulations](https://sun9-73.userapi.com/impg/oo9-2ZHeLhdSileY1tbywFVpbbFHBBaVKCc77Q/XiFkzM8P5_s.jpg?size=490x385&quality=95&sign=dfcd22d971c4b5718f9fbbc44d98f976&type=album)

* `Adding`
    * Text only📝
    * Photos only📷
    * Text📝 + Photo📷
    * «On Basic»

* `Change`
    * Differs from «Adding» by declaring the 🚩flag variable in the FSMContext

## 📤Newsletter & Reminder📨

> core > scheduler

`Arq performs` at specified time intervals The morning Newsletter and the Evening Reminder are `morning_sent()` and `ttable_reminder()`, whose signature is tied in the `SentList` class

#### *The differences between the methods are only in the algorithm for selecting the tg_id for the newsletter*

* > arq_scheduler.py > morning_sent()
    1. Cleaning and filling the table
    2. Search for Groups in the `tTable`, where the relevance of the timetable == today
    3. Forming a list of tuples, in which: 1 - group, 2 - availability of timetable(T/F)
    4. Select all  `tg_id` from `mailing`
    5. Sent timetable for "Good" and the absence for "Bad"

* > arq_scheduler.py > ttable_reminder()

    1. Cleaning and filling the table
    2. We calculate the groups that did not send the schedule
    3. We get the `tg_id` of the "Bad" groups
    4. We are sending a reminder about adding a schedule.

## 💾 DB

#### 4 tables are implemented

1. Table `users`👥
```sql
CREATE TABLE IF NOT EXISTS public.users
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    tg_id bigint NOT NULL,
    name character varying(65) COLLATE pg_catalog."default",
    "group" character varying(10) COLLATE pg_catalog."default",
    status text COLLATE pg_catalog."default" DEFAULT 'member'::text,
    
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_tg_id_key UNIQUE (tg_id)
)
```
#
2. Table of TimeTable of each group `tTable`📅
```sql
CREATE TABLE IF NOT EXISTS public."tTable"
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    lessons text COLLATE pg_catalog."default" NOT NULL,
    ttable_photo character varying(60) COLLATE pg_catalog."default",
    add_time date DEFAULT now(),
    day_sent date NOT NULL,
    "group" character varying(10) COLLATE pg_catalog."default" NOT NULL,
    addinger bigint NOT NULL,
    CONSTRAINT "tTable_pkey" PRIMARY KEY (id),
    CONSTRAINT "tTable_addinger_fkey" FOREIGN KEY (addinger)
        REFERENCES public.users (tg_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)
```
#
3. Floating🌀 table `mailing`📨
```sql
CREATE TABLE IF NOT EXISTS public.mailing
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    tg_id bigint,
    status text COLLATE pg_catalog."default" DEFAULT 'member'::text,
    "group" character varying(10) COLLATE pg_catalog."default",
    CONSTRAINT mailing_pkey PRIMARY KEY (id),
    CONSTRAINT mailing_tg_id_key UNIQUE (tg_id)
)
```
#
4. The smallest Table `default_ttable`🌱
```sql
CREATE TABLE IF NOT EXISTS public.default_ttable
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    ttable_photo character varying(40) COLLATE pg_catalog."default" NOT NULL,
    "group" character varying(10) COLLATE pg_catalog."default" NOT NULL,
    addinger bigint NOT NULL,
    CONSTRAINT default_ttable_pkey PRIMARY KEY (id),
    CONSTRAINT default_ttable_group_key UNIQUE ("group")
        CONSTRAINT "default_ttable_addinger_fkey" FOREIGN KEY (addinger)
        REFERENCES public.users (tg_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)
```

# Thanks For Reading✨😇