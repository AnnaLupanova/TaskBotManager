import asyncpg
from typing import Optional, Dict, List, Union


class Database:
    """Класс для управления подключением к базе данных и выполнения SQL-запросов."""

    def __init__(self, database_url: str) -> None:
        """
        Инициализирует экземпляр базы данных.
        """
        self.database_url: str = database_url
        self.pool: Optional[asyncpg.Pool] = None

    async def init_pool(self) -> None:
        """Создает пул соединений и инициализирует базу данных."""
        self.pool = await asyncpg.create_pool(self.database_url, min_size=1, max_size=20)
        await self.init_db()

    async def close_pool(self) -> None:
        """Закрывает пул соединений."""
        if self.pool:
            await self.pool.close()

    async def init_db(self) -> None:
        """Инициализирует структуру базы данных."""
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT UNIQUE NOT NULL PRIMARY KEY,
            name TEXT NOT NULL,
            login TEXT NOT NULL,
            username TEXT NOT NULL,
            CONSTRAINT login_unique UNIQUE (login)
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            is_completed BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query)

    async def check_exists_user(self, login: str) -> Optional[asyncpg.Record]:
        """
        Проверяет, существует ли пользователь с указанным логином.
        """
        query = "SELECT * FROM users WHERE login = $1"
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, login)

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[asyncpg.Record]:
        """
        Получает пользователя по Telegram ID.
        """
        query = "SELECT * FROM users WHERE id = $1"
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, telegram_id)

    async def add_user(self, user_id: int, name: str, login: str, username: str) -> None:
        """
        Добавляет нового пользователя в базу данных.
        """
        query = """
        INSERT INTO users (id, name, login, username)
        VALUES ($1, $2, $3, $4);
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, user_id, name, login, username)

    async def add_task(self, user_id: int, title: str, description: str) -> None:
        """
        Добавляет новую задачу для пользователя.
        """
        query = """
        INSERT INTO tasks (user_id, title, description)
        VALUES ($1, $2, $3);
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, user_id, title, description)

    async def get_tasks(self, user_id: int) -> List[asyncpg.Record]:
        """
        Получает список задач для указанного пользователя.
        """
        query = """
        SELECT id, title, description, is_completed 
        FROM tasks
        WHERE user_id = $1
        ORDER BY id;
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, user_id)

    async def get_task_by_id(self, task_id: int) -> Optional[asyncpg.Record]:
        """
        Получает задачу по ее ID.
        """
        query = """
        SELECT id, title, description, is_completed 
        FROM tasks
        WHERE id = $1;
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, task_id)

    async def complete_task(self, task_id: int) -> None:
        """
        Помечает задачу как выполненную.
        """
        query = """
        UPDATE tasks
        SET is_completed = TRUE
        WHERE id = $1;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, task_id)

    async def delete_task(self, task_id: int) -> None:
        """
        Удаляет задачу из базы данных.
        """
        query = """
        DELETE FROM tasks
        WHERE id = $1;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, task_id)
