from aiogram.fsm.state import StatesGroup, State


class SaveSteps(StatesGroup):
    GET_TIMETABLE = State()
    GET_UPDATE_TIMETABLE = State()
    GET_TIMETABLE_NO_TEXT = State()
    GET_GROUP = State()
    ADD_STANDARD = State()
