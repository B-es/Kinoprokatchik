"""Связка данных и базы на Google Drive.

Асинхронные методы уводят синхронный PyDrive2 в отдельный поток
(``asyncio.to_thread``), чтобы сеть не морозила интерфейс Flet.
"""

import asyncio

from data.Kino import Kino, KinosHandler
from data.drive.drive import Database

__all__ = ['DataController', 'Kino', 'KinosHandler']

_KinoDict = dict


class DataController:
    """Держит ``KinosHandler`` и синхронизирует его с базой на Drive."""

    def __init__(self, settings: dict, file_id: str) -> None:
        self.settings = settings
        self.file_id = file_id
        self._database = None
        self.kinosHandler = KinosHandler(json='[]')

    @property
    def database(self) -> Database:
        """Соединение с Drive создаётся лениво, при первом обращении."""
        if self._database is None:
            self._database = Database(self.settings, self.file_id)
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

    def clearData(self) -> None:
        """Локальная очистка без обращения к сети (совместимость со старым кодом)."""
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
