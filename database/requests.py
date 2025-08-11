#ФАЙЛ С ЗАПРОСАМИ В БД
from database.models import Task
from database.models import async_session
from sqlalchemy import select, update, delete

async def add_task(taskdata):
    async with async_session() as session:
        new_task = Task(
            user_id=taskdata["user_id"],
            title=taskdata["title"],
            priority=taskdata["priority"],
            deadline=taskdata["deadline"],
            is_completed=taskdata["is_completed"]
        )
        session.add(new_task)
        await session.commit()

async def select_task(user_id):
    async with async_session() as session:
        result = await session.scalars(select(Task).where(Task.user_id == user_id))
        return result.all()

async def update_status(task_id, new_status):
    async with async_session() as session:
        task = await session.get(Task, task_id)
        task.is_completed = new_status
        await session.commit()

async def update_title(task_id, new_title):
    async with async_session() as session:
        task = await session.get(Task, task_id)
        task.title = new_title
        await session.commit()

async def update_priority(task_id, new_priority):
    async with async_session() as session:
        task = await session.get(Task, task_id)
        task.priority = new_priority
        await session.commit()

async def update_deadline(task_id, new_deadline):
    async with async_session() as session:
        task = await session.get(Task, task_id)
        task.deadline = new_deadline
        await session.commit()


async def get_task_by_id(task_id):
    async with async_session() as session:
        return await session.get(Task, task_id)

async def delete_task(task_id):
    async with async_session() as session:
        task = await session.get(Task, task_id)
        if task:
            await session.delete(task)
            await session.commit()

async def select_active_tasks(session):
    stmt = select(Task).where(Task.is_completed.in_(["Не начато ❌", "В процессе ⏳"]))
    result = await session.execute(stmt)
    tasks = result.scalars().all()
    return tasks

from sqlalchemy import update

async def update_status_to_overdue(session, task_id: int):
    stmt = (
        update(Task)
        .where(Task.id == task_id)
        .values(is_completed="Просрочено ❗")
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(stmt)
    await session.commit()
