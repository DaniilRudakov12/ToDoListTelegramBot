import asyncio
from datetime import datetime, timedelta

from database.requests import select_active_tasks, update_status_to_overdue

#Функция для уведомления о приближающемся дедлайне
async def notify_deadlines(bot, session_maker):
    while True:
        async with session_maker() as session:
            tasks = await select_active_tasks(session)
            now = datetime.now()

            for task in tasks:
                if not task.deadline:
                    continue

                delta = task.deadline - now

                if timedelta(hours=23) <= delta <= timedelta(hours=25):
                    await bot.send_message(task.user_id, f"Напоминание: осталось около 1 дня до дедлайна задачи '{task.title}'")

                elif timedelta(hours=1, minutes=50) <= delta <= timedelta(hours=2, minutes=10):
                    await bot.send_message(task.user_id, f"Срочно! Осталось около 2 часов до дедлайна задачи '{task.title}'")

                elif now > task.deadline:
                    await update_status_to_overdue(session, task.id)
                    await bot.send_message(task.user_id, f"⚠️ Внимание! Дедлайн задачи '{task.title}' просрочен и задача не выполнена!")

        await asyncio.sleep(1)
