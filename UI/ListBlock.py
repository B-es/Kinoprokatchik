"""Правая зона: список фильмов и панель информации/формы."""

import flet as ft

from UI.Info import InfoPane
from UI.List import KinoList
from UI.Input import InputForm


class ListBlock(ft.Row):
    """Список фильмов слева, информация или форма справа.

    ``isWatching=True`` — блок «Смотрим», ``False`` — блок «Посмотрели».
    Результат изменения данных отдаётся наверх через ``on_changed``.
    """

    def __init__(self, controller, isWatching: bool, on_changed=None):
        super().__init__(expand=True)
        self.controller = controller
        self.isWatching = isWatching
        self.on_changed = on_changed

        self.list_view = KinoList(
            controller=controller,
            isWatching=isWatching,
            owner=self,
            on_save=self._on_save,
        )
        self.info = InfoPane()
        self.form = None

        self.content = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(content=self.list_view, width=500),
                    ft.VerticalDivider(),
                    self.info,
                ],
                expand=True,
            ),
            expand=True,
        )

    async def _on_save(self) -> None:
        """Сохраняет базу после изменения списка."""
        await self.controller.save()

    async def _notify(self) -> None:
        """Сообщает окну, что данные изменились."""
        if self.on_changed is not None:
            await self.on_changed()

    # --- то, что вызывает KinoList через owner ---

    def showInfo(self, kino) -> None:
        """Показывает карточку фильма."""
        self.form = None
        self.info.visible = True
        self.info.new(kino)
        self.update()

    def showForm(self, form: InputForm) -> None:
        """Показывает форму вместо карточки."""
        self.form = form
        self.info.visible = False
        self._set_right(form)
        self.update()

    def refreshInfo(self) -> None:
        """Перерисовывает карточку или открытую форму."""
        if self.form is not None:
            self._set_right(self.form)
            self._safe_update(self.form)
            return
        if self.info.visible and self.info.kino is not None:
            self.info.value = self.info.kinoToStr()
            self._safe_update(self.info)
        self._safe_update(self)

    @staticmethod
    def _safe_update(control) -> None:
        """update() только для контрола, который уже смонтирован на странице."""
        try:
            control.update()
        except RuntimeError:
            pass

    def _set_right(self, control) -> None:
        row = self.content.content
        row.controls[2] = control
        control.expand = True

    # --- API для окна ---

    def showCurrent(self) -> None:
        """Показывает данные текущего фильма после перезагрузки списка."""
        self.form = None
        kino = self.list_view.current_kino
        if kino is not None:
            self.info.kino = kino
            self.info.value = self.info.kinoToStr()
        self.info.visible = kino is not None
        self._set_right(self.info)
        self.update()

    def has_current(self) -> bool:
        return self.list_view.current_kino is not None

    def clear_current(self) -> None:
        self.list_view.current_kino = None
        self.list_view.current_tile = None

    def reload(self) -> None:
        self.list_view.sync()
        self.showCurrent()

    async def add(self, kino=None) -> None:
        """Показывает форму добавления."""
        initValue = len(self.controller.kinosHandler.Kinos) + 1
        self.showForm(
            InputForm(
                kino=kino,
                initValue=initValue,
                on_exit=self.cancel_form,
                on_apply=self._apply_form,
            )
        )

    async def change(self) -> None:
        """Показывает форму изменения текущего фильма."""
        kino = self.list_view.current_kino
        if kino is None:
            return
        self.showForm(
            InputForm(
                kino=kino,
                on_exit=self.cancel_form,
                on_apply=self._apply_form,
            )
        )

    async def delete_current(self) -> None:
        await self.list_view.delete_current()
        await self._notify()

    async def move_current(self) -> None:
        """«Смотрим» → «Посмотрели» и обратно."""
        await self.list_view.move_current()
        await self._notify()

    def cancel_form(self, e=None) -> None:
        self.form = None
        self.info.visible = True
        self._set_right(self.info)
        self.update()

    async def _apply_form(self, data: dict) -> None:
        if self.form is not None and getattr(self.form, 'kino', None) is not None:
            await self.list_view.change_current(data)
        else:
            await self.list_view.add(data)
        self.form = None
        self.info.visible = True
        self._set_right(self.info)
        await self._notify()
