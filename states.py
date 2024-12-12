from enum import Enum
from typing import Dict


class States(Enum):
    MAIN_MENU = "MAIN_MENU"
    REGISTERING = "REGISTERING"
    CREATE_TASK_TITLE = "CREATE_TASK_TITLE"
    CREATE_TASK_DESCRIPTION = "CREATE_TASK_DESCRIPTION"
    VIEW_TASKS = "VIEW_TASKS"


class FSM:
    """Управление состояниями пользователей и временными данными."""
    def __init__(self) -> None:
        self.states: Dict[int, States] = {}
        self.data: Dict[int, Dict] = {}

    def set_state(self, user_id: int, state: States) -> None:
        """Устанавливает состояние пользователя."""
        self.states[user_id] = state

    def get_state(self, user_id: int) -> States:
        """Возвращает текущее состояние пользователя."""
        return self.states.get(user_id, States.MAIN_MENU)

    def clear_state(self, user_id: int) -> None:
        """Сбрасывает состояние пользователя на главное меню."""
        self.states[user_id] = States.MAIN_MENU

    def set_data(self, user_id: int, data: Dict) -> None:
        """Сохраняет временные данные пользователя."""
        self.data[user_id] = data

    def get_data(self, user_id: int) -> Dict:
        """Получает временные данные пользователя."""
        return self.data.get(user_id, {})

    def clear_data(self, user_id: int) -> None:
        """Очищает временные данные пользователя."""
        self.data[user_id] = {}
