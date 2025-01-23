from datetime import datetime, timedelta

from core.config import FULL_LOCAL_PATH


def aud_point_or_not(lesson):
    lesson_res = lesson.replace('ауд.', '')
    if lesson_res == lesson:
        lesson_res = lesson.replace('ауд', '')
    return lesson_res


def mes_to_ttable(lessons):
    "Переработка сырого текста в Расписание"
    first_lesson = aud_point_or_not(lessons[1])
    fTable = f'<b>{lessons[0]}</b> | {first_lesson[:-1]}'.strip()
    if fTable[-3:].isdigit():
        fTable = fTable.replace(fTable[-3:], f'<i><b>{fTable[-3:]}</b></i>')

    for i in range(1, len(lessons)):
        int_char = lessons[i][-1]
        if int_char.isdigit():
            lesson = aud_point_or_not(lessons[i + 1])[:-1].strip()
            if lesson[-3:].isdigit():
                lesson = lesson.replace(lesson[-3:], f'<i><b>{lesson[-3:]}</b></i>')
            fTable += f'\n<b>{int_char}</b> | {lesson}'
    return fTable


def text_processing(raw_text):
    dummy = raw_text.split(')')
    try:
        answer = mes_to_ttable(dummy)
        log_mes = ''
    except IndexError:
        answer = ''
        log_mes = "Текст не удалось добавить - /help"
    return answer, log_mes


def day_sent_appointer():
    "Алгоритм для вычисления дня отправки"
    next_day = datetime.now() + timedelta(days=1)
    week_day = next_day.weekday()
    if week_day == 6:
        next_day = next_day + timedelta(days=1)
    return next_day

def get_group_structure():
    "Полный список групп"
    with open(FULL_LOCAL_PATH + 'group_structure.txt', 'rt', encoding='utf-8') as file:
        groups = [line.replace('\n', '') for line in file]
    return groups

def get_group_structure_spec(listt):
    "Для определения групп, у которых есть расписание для утренней отправки на сегодня или нет"
    with open(FULL_LOCAL_PATH + 'group_structure.txt', 'rt', encoding='utf-8') as file:
        groups = [(line.replace('\n', ''), 1)
                  if line.replace('\n', '') in listt
                  else (line.replace('\n', ''), 0)
                  for line in file]
    return groups
