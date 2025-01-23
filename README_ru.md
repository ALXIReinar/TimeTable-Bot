# 📅 Бот Расписание
![Python ver](https://img.shields.io/badge/pyhon-3.10-orange)
![aiogram](https://img.shields.io/badge/aiogram-3.13.1-blue)
![postgres](https://img.shields.io/badge/postgre-16-42a4ff)
![arq](https://img.shields.io/badge/arq-0.26.1-yellow)


## 💡Основная идея

1. `Пользователи поделены` на `группы`

2. Своевременно `один из пользователей` своей группы `присылает расписание` на следующий день
3. `Бот присылает расписание` в установленное время `всем группам` пользователей, приславших фото/текст своих занятий. `Или напоминает об его отсутсвии`, чтобы пользователи сделали это самостоятельно 


## 👥 Деление по группам

> core > middlewares > command_middleware.py

### Задачи📌

1. По условию, мы делаем рассылку по группам. Это значит, мы не можем позволить неиндетифицированному пользователю взаимодействовать с ботом 
    
    * `Стоит задача проверки статуса перед пользованием`

2. Мы могли бы ограничить "принадлежность" пользователя, запретив менять группу, но любой человек может ошибиться... Или намеренно спровоцировать неудобную ситуацию, выложив что угодно вместо нужной информации :-)

    * `Необходим 100% способ выявления автора расписания`

### Решение🎯

1. ❌Можно поставить `Middleware` , который будет на каждом апдейте проверять поле `users.group` . Однако это `пагубно` скажется `из-за бесконечных запросов в бд`. ..
* ✅Прежде чем начать забрасывать бота апдейтами, Пользователь нажимает команды, так как после неудачной проверки на них дальнейшее общение просто обрывается. Таким образом, мы сужаем круг действия `Middleware`, регистрируя их только на `message` и задавая условие:
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
2. ✅Здесь Мы просто дополнительно фиксируем в таблице Автора сообщения по tg_id и прикрепляем клавиатуру с гипер-ссылкой на него

    ![alt text](https://sun9-69.userapi.com/impg/ECk2RcTODh4IWNyLlHPAlBAybOfARqEMYQkK7A/DTL8l4Iqrek.jpg?size=396x594&quality=95&sign=98b4a07c8b49e9a4b247952f8ad3ca23&type=album)


## Расписание 📅

> core > timetable > modified

> core > timetable > standard

### 📃С изменениями & 📜Стандартное

Классические операции:
1. Отображение - `/ttable_show`
2. Добавление - `/ttable_add`
3. Изменение - `/ttable_update`

* `Отображение`

    ![Congratulations](https://sun9-73.userapi.com/impg/oo9-2ZHeLhdSileY1tbywFVpbbFHBBaVKCc77Q/XiFkzM8P5_s.jpg?size=490x385&quality=95&sign=dfcd22d971c4b5718f9fbbc44d98f976&type=album)

* `Добавление`
    * Только текст📝
    * Только фото📷
    * Текст📝 + Фото📷
    * «По основному»

* `Изменение`
    * Отличается от «Добавление» объявлением переменной-флага 🚩 в FSMContext

#### Сохранять фото было принято локально, в сам проект в форматах

* 📃 Для изменённого расписания "dd-MM-YYYY_ГРУППА"
    > images > daily > 2025-01-24_23И1.jpg
* 📜 Для стандартного расписания "ГРУППА.jpg"
    > images > standard > 23И1.jpg

## 📤Рассылка & Напоминание📨

> core > scheduler

`Arq` в заданные интервалы времени `выполняет` Утреннюю Рассылку и Вчернее напоминание - `morning_sent()` и `ttable_reminder()` , Сигнатура которых завязана в классе `SentList` 

#### *Различия методов только в алгоритме подборки tg_id к рассылке*


* > arq_scheduler.py > morning_sent()

    1. Очистка и наполнение таблицы
    2. Поиск Групп в `tTable`, где актуальность расписания == сегодня
    3. Формирования списка кортежей, в котором: 1 - группа, 2 - наличие расписания(T/F)
    4. Выбираем все tg_id из `mailing`
    5. Отправляем расписание "Хорошим" и отсутствие "Плохим"

* > arq_scheduler.py > ttable_reminder()
    
    1. Очистка и наполнение таблицы
    2. Вычисляем группы, не отправившие расписание
    3. Получаем `tg_id` "Плохих" групп
    4. Отправляем напоминание о добавлении расписания

## 💾 БД

#### Реализованы 4 таблицы

1. Таблица пользователей `users`👥
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
2. Таблица расписания каждой группы `tTable`📅
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
3. Плавающая🌀 таблица рассылок `mailing`📨
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
4. Самая маленькая таблица `default_ttable`🌱
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

# Спасибо За Прочтение✨😇