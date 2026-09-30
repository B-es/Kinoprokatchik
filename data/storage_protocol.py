"""Общий контракт хранилища базы.

Приложение не знает, где лежит база: локально или в Google Drive. Любой
бэкенд реализует три метода — ``get``, ``save``, ``clear``, — и создаётся
фабрикой ``open_database`` в ``data/storage.py``.

Методы синхронные и могут ходить в сеть: вызывать их только из отдельного
потока (``asyncio.to_thread``), иначе интерфейс Flet 1.x замёрзнет.
"""

from typing import Protocol, runtime_checkable

__all__ = ['Storage']


@runtime_checkable
class Storage(Protocol):
    """Хранилище JSON-строки."""

    def get(self) -> str:
        """Прочитать данные (пустая строка, если базы ещё нет)."""
        ...

    def save(self, json: str) -> None:
        """Записать данные."""
        ...

    def clear(self) -> None:
        """Очистить данные."""
        ...
