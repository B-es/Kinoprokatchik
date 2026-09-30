"""Связка данных и базы: локальный файл или Google Drive.

Асинхронные методы уводят синхронное хранилище (файл или PyDrive2) в
отдельный поток (``asyncio.to_thread``), чтобы ввод-вывод не морозил
интерфейс Flet 1.x.
"""

import asyncio

from data.Kino import Kino, KinosHandler
from data.storage import Storage, open_database

__all__ = ['DataController', 'Kino', 'KinosHandler']

_KinoDict = dict


class DataController:
    """Держит ``KinosHandler`` и синхронизирует его с выбранным хранилищем."""

    def __init__(self, mode: str, settings: dict = None) -> None:
        self.mode = mode
        self.settings = settings
        self._database = None
        self.kinosHandler = KinosHandler(json='[]')

    @property
    def database(self) -> Storage:
        """Хранилище создаётся лениво, при первом обращении (и может открыть браузер)."""
        if self._database is None:
            self._database = open_database(self.mode, self.settings)
        return self._database

    async def load(self) -> None:
        """Прочитать базу и пересобрать список фильмов."""
        json = await asyncio.to_thread(lambda: self.database.get())
        self.kinosHandler = KinosHandler(json=json)

    async def save(self) -> None:
        """Записать текущее состояние в базу."""
        json = self.kinosHandler.toJson()
        await asyncio.to_thread(lambda: self.database.save(json))

    async def clear(self) -> None:
        """Очистить список и базу."""
        self.kinosHandler.clear()
        await asyncio.to_thread(lambda: self.database.clear())

    async def migrate(self, to: str) -> None:
        """Перенести текущие данные в другое хранилище и переключиться на него."""
        json = self.kinosHandler.toJson()
        target = open_database(to, self.settings)
        await asyncio.to_thread(lambda: target.save(json))
        self.mode = to
        self._database = target

    def clearData(self) -> None:
        """Локальная очистка без обращения к хранилищу (совместимость со старым кодом)."""
        self.kinosHandler.clear()

    def append(self, dict: _KinoDict = None, dicts: list = None) -> None:
        if dict is not None:
            self.kinosHandler.append(dict)
        elif dicts is not None:
            for kino in dicts:
                self.kinosHandler.append(kino)

    def update(self, prevKino: Kino, dict: _KinoDict):
        return self.kinosHandler.update(prevKino, dict)

    def removeAt(self, index: int) -> None:
        self.kinosHandler.removeAt(index)

    def remove(self, kino: Kino) -> int:
        return self.kinosHandler.remove(kino)
