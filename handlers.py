#ФАЙЛ С РУЧКАМИ
from datetime import datetime
from typing import Dict, Optional

from aiogram.filters.command import Command
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from reply_keyboards import main_kb, tasks_menu_kb, status_kb, cancel_kb

import database.requests as rq

router = Router()



#Ручка для начала
@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(f'''Привет, {message.from_user.full_name}! Добро пожаловать на мой ToDoList!👋
Чтобы пользоваться ботом используй меню возле клавиатуры или команды ниже.
/add - добавить событие
/show - показать события''', reply_markup=main_kb)


@router.message(F.text == "📋 Показать список событий")
async def add_event_from_button(message: types.Message):
    await show_command(message)


class Addtask(StatesGroup):
    title = State()
    priority = State()
    deadline = State()

temp_tasks: Dict[int, Dict[str, Optional[str]]] = {}

@router.message(Command("add"))
async def add_command(message: types.Message, state: FSMContext):
    await message.answer("Введите название события", reply_markup=cancel_kb)
    user_add = message.from_user.id
    await state.set_state(Addtask.title)
    temp_tasks[user_add] = {
        'user_id': user_add,
        'title': None,
        'priority': None,
        'deadline': None,
        'is_completed': "Не начато❌"
    }


@router.message(Addtask.title)
async def add_title(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        temp_tasks.pop(message.from_user.id, None)
        await message.answer("Создание задачи отменено ✅", reply_markup=main_kb)
        return
    temp_tasks[message.from_user.id]["title"] = message.text
    await state.clear()
    await message.answer("Введите приоритет", reply_markup=cancel_kb)
    await state.set_state(Addtask.priority)


@router.message(Addtask.priority)
async def add_priority(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        temp_tasks.pop(message.from_user.id, None)
        await message.answer("Создание задачи отменено ✅", reply_markup=main_kb)
        return
    temp_tasks[message.from_user.id]["priority"] = message.text
    await state.clear()
    await message.answer("Введите дедлайн в формате ДД.ММ.ГГГГ ЧЧ:ММ", reply_markup=cancel_kb)
    await state.set_state(Addtask.deadline)

@router.message(Addtask.deadline)
async def add_deadline(message: types.Message, state: FSMContext):
    try:
        if message.text == "❌ Отмена":
            await state.clear()
            temp_tasks.pop(message.from_user.id, None)
            await message.answer("Создание задачи отменено ✅", reply_markup=main_kb)
            return
        deadline = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
        now = datetime.now()
        if deadline <= now:
            await message.answer(
                "Ошибка: дедлайн должен быть позже текущего времени. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ ЧЧ:ММ, которая будет в будущем.",
                reply_markup=cancel_kb)
            return
        temp_tasks[message.from_user.id]["deadline"] = deadline
        await state.clear()
        await rq.add_task(temp_tasks[message.from_user.id])
        await message.answer("Задача успешно добавлена!", reply_markup=main_kb)
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ ЧЧ:ММ", reply_markup=cancel_kb)




@router.message(Command("show"))
@router.message(F.text == "📋 Показать список событий")
async def show_command(message: types.Message):
    tasks = await rq.select_task(message.from_user.id)
    if not tasks:
        await message.answer("У тебя нет никаких задач!", reply_markup=tasks_menu_kb)
        return

    for task in tasks:
        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="📝 Изменить название", callback_data=f"edit_title:{task.id}"))
        kb.row(InlineKeyboardButton(text="📌 Изменить приоритет", callback_data=f"edit_priority:{task.id}"))
        kb.row(InlineKeyboardButton(text="⏳ Изменить дедлайн", callback_data=f"edit_deadline:{task.id}"))
        kb.row(InlineKeyboardButton(text="✏️ Изменить статус", callback_data=f"edit_status:{task.id}"))
        kb.row(InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_task:{task.id}"))

        await message.answer(
            f"📌 *{task.title}*\n"
            f"Приоритет: {task.priority}\n"
            f"Дедлайн: {task.deadline.strftime('%d.%m.%Y %H:%M') if task.deadline else '—'}\n"
            f"Статус: {task.is_completed}",
            parse_mode="Markdown",
            reply_markup=kb.as_markup()
        )

    # Клавиатура снизу
    await message.answer("Выберите действие:", reply_markup=tasks_menu_kb)


class EditTitle(StatesGroup):
    new_title = State()

@router.callback_query(F.data.startswith("edit_title:"))
async def callback_edit_title(callback: types.CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split(":")[1])
    await state.update_data(task_id=task_id, msg_id=callback.message.message_id, chat_id=callback.message.chat.id)
    await callback.message.answer("Введите новое название задачи:")
    await state.set_state(EditTitle.new_title)

@router.message(EditTitle.new_title)
async def process_edit_title(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await rq.update_title(data["task_id"], message.text)
    await message.answer("✅ Название задачи обновлено")
    await show_command(message)
    await state.clear()

class EditPriority(StatesGroup):
    new_priority = State()

@router.callback_query(F.data.startswith("edit_priority:"))
async def callback_edit_priority(callback: types.CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split(":")[1])
    await state.update_data(task_id=task_id, msg_id=callback.message.message_id, chat_id=callback.message.chat.id)
    await callback.message.answer("Введите новый приоритет задачи:")
    await state.set_state(EditPriority.new_priority)

@router.message(EditPriority.new_priority)
async def process_edit_priority(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await rq.update_priority(data["task_id"], message.text)
    await message.answer("✅ Приоритет задачи обновлён")
    await show_command(message)
    await state.clear()

class EditDeadline(StatesGroup):
    new_deadline = State()

@router.callback_query(F.data.startswith("edit_deadline:"))
async def callback_edit_deadline(callback: types.CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split(":")[1])
    await state.update_data(task_id=task_id, msg_id=callback.message.message_id, chat_id=callback.message.chat.id)
    await callback.message.answer("Введите новый дедлайн задачи в формате ДД.ММ.ГГГГ ЧЧ:ММ:")
    await state.set_state(EditDeadline.new_deadline)

@router.message(EditDeadline.new_deadline)
async def process_edit_deadline(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        deadline = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
        now = datetime.now()
        if deadline <= now:
            await message.answer(
                "Ошибка: дедлайн должен быть позже текущего времени. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ ЧЧ:ММ, которая будет в будущем.",
                reply_markup=cancel_kb)
            return
        await rq.update_deadline(data["task_id"], deadline)
        await message.answer("✅ Дедлайн задачи обновлён")
        await show_command(message)
        await state.clear()
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ ЧЧ:ММ")

class EditStatus(StatesGroup):
    new_status = State()

@router.callback_query(F.data.startswith("edit_status:"))
async def callback_edit_status(callback: types.CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split(":")[1])
    await state.update_data(task_id=task_id, msg_id=callback.message.message_id, chat_id=callback.message.chat.id)
    await callback.message.answer("Введите новый статус задачи:", reply_markup=status_kb)
    await state.set_state(EditStatus.new_status)

@router.message(EditStatus.new_status)
async def process_edit_status(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await rq.update_status(data["task_id"], message.text)
    await message.answer("✅ Статус задачи обновлён")
    await show_command(message)

    await state.clear()


@router.callback_query(F.data.startswith("delete_task:"))
async def callback_delete_task(callback: types.CallbackQuery):
    task_id = int(callback.data.split(":")[1])
    await rq.delete_task(task_id)
    await callback.answer("Задача удалена ✅", show_alert=False)
    await callback.message.delete()


@router.message(F.text == "⬅ Назад")
async def go_back(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите действие:", reply_markup=main_kb)

@router.message(F.text == "➕ Добавить событие")
async def add_event_from_button(message: types.Message, state: FSMContext):
    # Просто вызываем команду /add
    await add_command(message, state=state)



