from aiogram.fsm.state import StatesGroup, State

class TaskAdd(StatesGroup):
    waiting_for_due_time = State()
    waiting_for_title = State()
    waiting_for_repeat = State()
    waiting_for_reminder = State()

from aiogram.fsm.state import StatesGroup, State


class TaskAddState(StatesGroup):
    time = State()                  # HH:MM
    title = State()                 # название

    repeat_type = State()           # daily / weekly
    repeat_days = State()           # дни недели
    weekdays = State()

    need_reminder = State()

    reminder_start_before = State()
    reminder_before = State()
    reminder_after = State()
    reminder_after_end = State()

    reminder_before_unit = State()   # minutes / seconds
    reminder_after_unit = State() 

    confirm = State()
