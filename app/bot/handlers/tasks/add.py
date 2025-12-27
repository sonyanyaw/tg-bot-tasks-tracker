# from aiogram import F
# from aiogram.types import Message
# from aiogram.fsm.context import FSMContext
# from aiogram.filters import Command
# from datetime import datetime

# from app.bot.states.task_add import TaskAdd
# from app.services.task_service import TaskService
# from app.services.user_service import get_or_create_user

# async def add_task_start(message: Message, state: FSMContext):
#     await message.answer("Введите название задачи:")
#     await state.set_state(TaskAdd.waiting_for_title)

# async def process_title(message: Message, state: FSMContext):
#     await state.update_data(title=message.text)
#     await message.answer("Введите время выполнения задачи (формат: ЧЧ:ММ):")
#     await state.set_state(TaskAdd.waiting_for_due_time)

# async def process_due_time(message: Message, state: FSMContext):
#     data = await state.get_data()
#     title = data["title"]

#     # Получаем пользователя (уже создан при /start)
#     user = await get_or_create_user(message)

#     try:
#         due_time = datetime.strptime(message.text, "%H:%M")
#         due_at = datetime.combine(datetime.utcnow().date(), due_time.time())
#     except ValueError:
#         await message.answer("Неверный формат времени. Используйте ЧЧ:ММ")
#         return

#     await TaskService.create_task(user.id, title, due_at)
#     await message.answer(f"✅ Задача '{title}' добавлена на {due_at.strftime('%H:%M')}")
#     await state.clear()

# from aiogram.fsm.state import State, StatesGroup


# class TaskAddState(StatesGroup):
#     title = State()                # название
#     date = State()                 # дата
#     time = State()                 # точное время

#     repeat = State()               # повторение
#     repeat_days = State()          # дни недели (если нужно)

#     need_reminder = State()        # нужно ли напоминание
#     reminder_before = State()      # интервалы до дедлайна
#     reminder_after = State()       # интервалы после дедлайна
#     reminder_after_end = State()   # конец напоминаний

#     confirm = State()              # подтверждение

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.keyboards.reminder_units import units_keyboard
from app.bot.states.task_add import TaskAddState
from app.bot.keyboards.task_repeat import repeat_keyboard
from app.bot.keyboards.task_reminder import need_reminder_keyboard
from app.bot.keyboards.common import confirm_keyboard, week_days_keyboard
from app.services.task_service import TaskService
from app.utils.datetime import parse_time


# from aiogram import Router, F
# from aiogram.types import Message, CallbackQuery
# from aiogram.fsm.context import FSMContext

# from app.bot.states.task_add import TaskAddState
# from app.bot.keyboards.task_repeat import repeat_keyboard
# from app.bot.keyboards.task_reminder import need_reminder_keyboard
# from app.services.task_service import TaskService
# from app.utils.datetime import parse_date, parse_time, combine_date_time

router = Router()

WEEKDAY_MAP = {
    "mon": 0,
    "tue": 1,
    "wed": 2,
    "thu": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6,
}


@router.message(F.text == "➕ Добавить задачу")
async def add_task_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("⏰ На какое время задание? (ЧЧ:MM)")
    await state.set_state(TaskAddState.time)


@router.message(TaskAddState.time)
async def task_time_handler(message: Message, state: FSMContext):
    try:
        time = parse_time(message.text)
    except ValueError:
        await message.answer("❌ Формат времени: ЧЧ:MM")
        return

    await state.update_data(time=time)
    await message.answer("✏️ Введите название задания:")
    await state.set_state(TaskAddState.title)


@router.message(TaskAddState.title)
async def task_title_handler(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())

    await message.answer(
        "🔁 Это ежедневное задание или по дням недели?",
        reply_markup=repeat_keyboard(),
    )
    await state.set_state(TaskAddState.repeat_type)


@router.callback_query(
    TaskAddState.repeat_type,
    F.data.startswith("repeat:")
)
async def repeat_type_handler(callback: CallbackQuery, state: FSMContext):
    repeat = callback.data.split(":")[1]
    await state.update_data(repeat=repeat)

    if repeat == "weekly":
        await state.update_data(repeat_days=set())
        await callback.message.answer(
            "📅 Выберите дни недели:",
            reply_markup=week_days_keyboard(),
        )
        await state.set_state(TaskAddState.repeat_days)
    else:
        await callback.message.answer(
            "🔔 Нужно ли напоминание?",
            reply_markup=need_reminder_keyboard(),
        )
        await state.set_state(TaskAddState.need_reminder)

    await callback.answer()


@router.callback_query(TaskAddState.repeat_days, F.data.startswith("day:"))
async def repeat_day_toggle(callback: CallbackQuery, state: FSMContext):
    day = callback.data.split(":")[1]
    data = await state.get_data()
    days: set = data.get("repeat_days", set())

    if day in days:
        days.remove(day)
    else:
        days.add(day)

    await state.update_data(repeat_days=days)

    await callback.message.edit_reply_markup(
        reply_markup=week_days_keyboard(days)
    )
    await callback.answer()


@router.callback_query(TaskAddState.repeat_days, F.data == "days:done")
async def repeat_days_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    raw_days: set[str] = data.get("repeat_days", set())
    if not data["repeat_days"]:
        await callback.answer("❗ Выберите хотя бы один день", show_alert=True)
        return
    
    weekdays = sorted(WEEKDAY_MAP[d] for d in raw_days)
    await state.update_data(weekdays=weekdays)

    await callback.message.answer(
        "🔔 Нужно ли напоминание?",
        reply_markup=need_reminder_keyboard(),
    )
    await state.set_state(TaskAddState.need_reminder)
    await callback.answer()


@router.callback_query(TaskAddState.need_reminder, F.data.startswith("reminder:"))
async def need_reminder_handler(callback: CallbackQuery, state: FSMContext):
    need = callback.data.split(":")[1] == "yes"
    await state.update_data(need_reminder=need)

    if not need:
        await state.set_state(TaskAddState.confirm)
        await callback.message.answer("✅ Задача будет без напоминаний")
    else:
        await callback.message.answer(
            "⏳ За сколько времени ДО задачи начинать напоминания?\n"
            "Например (в минутах): 30"
        )
        await state.set_state(TaskAddState.reminder_start_before)

    await callback.answer()


@router.message(TaskAddState.reminder_start_before)
async def reminder_start_before_handler(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число (в минутах)")
        return

    await state.update_data(reminder_start_before=int(message.text))

    await message.answer(
        "⏱ В чём указывать интервал ДО дедлайна?",
        reply_markup=units_keyboard()  # минуты / секунды
    )
    await state.set_state(TaskAddState.reminder_before_unit)

    # await state.set_state(TaskAddState.reminder_before)


@router.callback_query(TaskAddState.reminder_before_unit, F.data.startswith("unit:"))
async def reminder_before_unit_handler(callback: CallbackQuery, state: FSMContext):
    unit = callback.data.split(":")[1]
    await state.update_data(reminder_before_unit=unit)

    await callback.message.answer("🔁 Интервал ДО дедлайна:")
    await state.set_state(TaskAddState.reminder_before)
    await callback.answer()



@router.message(TaskAddState.reminder_before)
async def reminder_before_handler(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число")
        return

    await state.update_data(reminder_before=int(message.text))

    await message.answer(
        "⏱ В чём указывать интервал ПОСЛЕ дедлайна?",
        reply_markup=units_keyboard()  # минуты / секунды
    )
    await state.set_state(TaskAddState.reminder_after_unit)
    # await message.answer(
    #     "🔁 Введите интервал напоминаний ПОСЛЕ дедлайна (в минутах):"
    # )
    # await state.set_state(TaskAddState.reminder_after)


@router.callback_query(TaskAddState.reminder_after_unit, F.data.startswith("unit:"))
async def reminder_after_unit_handler(callback: CallbackQuery, state: FSMContext):
    unit = callback.data.split(":")[1]
    await state.update_data(reminder_after_unit=unit)

    await callback.message.answer(
        "🔢 Введите интервал ПОСЛЕ дедлайна:"
    )
    await state.set_state(TaskAddState.reminder_after)
    await callback.answer()



@router.message(TaskAddState.reminder_after)
async def reminder_after_handler(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число")
        return

    await state.update_data(reminder_after=int(message.text))


    await message.answer(
        "⏹ До какого времени напоминать после дедлайна?\nВведите HH:MM или 0 — чтобы отключить"
    )
    await state.set_state(TaskAddState.reminder_after_end)
    # await callback.answer()


@router.message(TaskAddState.reminder_after_end)
async def reminder_after_end_handler(message: Message, state: FSMContext):
    if message.text == "0":
        await state.update_data(reminder_after_end=None)
    else:
        try:
            end_time = parse_time(message.text)
        except ValueError:
            await message.answer("❌ Формат HH:MM или 0")
            return

        await state.update_data(reminder_after_end=end_time)

    await state.set_state(TaskAddState.confirm)
 

    data = await state.get_data()
    print('[DEBUG] DATA BEFORE CREATE', data)
    # before_units, after_units = '', ''
    if data['reminder_before_unit'] == "minutes":
        before_units = "минут"
    else:
        before_units = "секунд"

    if data['reminder_after_unit'] == "minutes":
        after_units = "минут"
    else:
        after_units = "секунд"

    end_str = data['reminder_after_end'].strftime("%H:%M") if data.get('reminder_after_end') else "не ограничено"

    await message.answer(
        "✅ Подтвердить создание задачи?\n\n"
        f"📝 {data['title']}\n"
        f"⏰ Время: {data['time'].strftime('%H:%M')}\n"
        f"⏳ Напоминание начнётся: {data.get('reminder_start_before', 0)} минут до дедлайна\n"
        f"🔹 Интервал ДО дедлайна: {data.get('reminder_before', 0)} {before_units}\n"
        f"🔹 Интервал ПОСЛЕ дедлайна: {data.get('reminder_after', 0)} {after_units}\n"
        f"⏹ Конец напоминаний после дедлайна: {end_str}",
        reply_markup=confirm_keyboard()
    )



@router.callback_query(
    TaskAddState.confirm,
    F.data.startswith("confirm:")
)
async def task_confirm_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    action = callback.data.split(":")[1]

    if action == "no":
        await callback.message.answer("❌ Создание задачи отменено")
        await state.clear()
        await callback.answer()
        return

    data = await state.get_data()

    if "weekdays" in data:
        data["times"] = [data["time"]] * len(data["weekdays"])

    await TaskService.create_task_from_fsm(
        telegram_user=callback.from_user,
        data=data,
    )

    await callback.message.answer("🎉 Задача создана!")
    await state.clear()
    await callback.answer()


# @router.message(TaskAddState.confirm)
# async def task_confirm_handler(message: Message, state: FSMContext):
#     data = await state.get_data()

#     await TaskService.create_task_from_fsm(
#         telegram_user=message.from_user,
#         data=data,
#     )

#     await message.answer("🎉 Задача создана!")
#     await state.clear()
