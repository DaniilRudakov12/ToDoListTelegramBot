#ФАЙЛ С МОДЕЛЯМИ БАЗЫ ДАННЫХ
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import String, DateTime, BigInteger
from datetime import datetime
import asyncio

engine = create_async_engine('sqlite+aiosqlite:///todo_bot.db')

async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger)  # ID пользователя в Telegram
    title: Mapped[str] = mapped_column(String(255))  # Название события
    priority: Mapped[str] = mapped_column(String(20))  # Приоритет
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)  # Дедлайн
    is_completed: Mapped[str] = mapped_column(String(30))  # Статус выполнения

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(async_main())