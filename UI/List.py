"""Список фильмов и строка-тайл."""

import flet as ft

from data.Kino import Kino, make_kino_dict
from data.DataController import DataController


class KinoTile(ft.ListTile):
    """Строка списка: «номер) название»."""

    def __init__(self, kino: Kino, click=None):
        super().__init__()
        self.kino = kino
        self.data = kino
        self.title = ft.Text(value=f'{kino.number}) {kino.name}')
        self.leading = ft.Icon(name=ft.Icons.MOVIE_OUTLINED)
        self.selected = False
        self.on_click = click

    def pick(self) -> None:
        """Подсвечивает строку."""
        self.selected = True
        self.update()

    def unpick(self) -> None:
        """Снимает подсветку."""
        self.selected = False


class KinoList(ft.ListView):
    """Список фильмов из одной группы: «смотрим» или «посмотрели»."""

    def __init__(self, controller: DataController, isWatching: bool, owner, on_notify=None, on_save=None):
        super().__init__(expand=True, padding=10)
        self.controller = controller
        self.isWatching = isWatching
        self.owner = owner
        self.on_notify = on_notify
        self.on_save = on_save
        self.current_kino: Kino = None
        self.current_tile: KinoTile = None
        self._tiles: dict = {}
        self.loadControls()
        kinos = self._kinos()
        if kinos:
            self.current_kino = kinos[0]
            self.current_tile = self._tiles.get(kinos[0].number)

    def _kinos(self) -> list:
        """Фильмы своей группы (смотрим — ещё не просмотренные)."""
        return self.controller.kinosHandler.getTypedKinos(not self.isWatching)

    def loadControls(self) -> None:
        """Пересобирает строки списка."""
        self.controls = []
        self._tiles = {}
        for kino in self._kinos():
            tile = KinoTile(kino, self.select)
            self._tiles[kino.number] = tile
            self.controls.append(tile)

        if self.current_kino is not None:
            tile = self._tiles.get(self.current_kino.number)
            if tile is not None:
                tile.selected = True
                self.current_tile = tile

    def highlightTile(self, tile: KinoTile) -> None:
        """Оставляет подсвеченной только одну строку."""
        for other in self._tiles.values():
            if other is not tile:
                other.unpick()
        tile.pick()

    def sync(self) -> None:
        """Обновляет содержимое списка после изменения данных."""
        self.loadControls()
        self.update()

    def select(self, e) -> None:
        """Клик по строке."""
        tile = e.control
        self.current_tile = tile
        self.current_kino = tile.data
        self.highlightTile(tile)
        self.owner.showInfo(self.current_kino)

    async def _changed(self) -> None:
        self.loadControls()
        self.owner.refreshInfo()
        self.update()
        if self.on_notify is not None:
            await self.on_notify()
        if self.on_save is not None:
            await self.on_save()

    def append(self, data: dict) -> None:
        """Добавляет фильм (синхронная часть)."""
        self.current_kino = self.controller.kinosHandler.append(data)

    def change(self, data: dict) -> None:
        """Изменяет текущий фильм (синхронная часть)."""
        self.current_kino = self.controller.kinosHandler.update(self.current_kino, data)

    def deleteCurrent(self) -> None:
        """Удаляет текущий фильм (синхронная часть)."""
        if self.current_kino is not None:
            self.controller.kinosHandler.remove(self.current_kino)
            self.current_kino = None
            self.current_tile = None

    def changeWatching(self) -> None:
        """Перекладывает текущий фильм в другую группу (синхронная часть)."""
        if self.current_kino is None:
            return
        if self.isWatching:
            self.controller.kinosHandler.setWatched(self.current_kino)
        else:
            self.controller.kinosHandler.setWatching(self.current_kino)
        self.current_kino = None
        self.current_tile = None

    async def add(self, data: dict) -> None:
        self.append(data)
        await self._changed()

    async def change_current(self, data: dict) -> None:
        self.change(data)
        await self._changed()

    async def delete_current(self) -> None:
        self.deleteCurrent()
        await self._changed()

    async def move_current(self) -> None:
        self.changeWatching()
        await self._changed()
