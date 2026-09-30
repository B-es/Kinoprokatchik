"""Счётчик номера фильма."""

import flet as ft


class Counter(ft.Container):
    """Поле «Номер» с кнопками «−» и «+»."""

    def __init__(self, max: int = 100, initValue: int = 1):
        super().__init__()
        self.value = int(initValue)

        self._field = ft.TextField(
            value=str(self.value),
            text_align=ft.TextAlign.RIGHT,
            width=100,
        )

        self.content = ft.Row(
            controls=[
                ft.Text(value='Номер'),
                ft.IconButton(icon=ft.Icons.REMOVE, on_click=self._minus_click),
                self._field,
                ft.IconButton(icon=ft.Icons.ADD, on_click=self._plus_click),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def _set(self, value: int) -> None:
        self.value = value
        self._field.value = str(value)
        self.update()

    def _minus_click(self, e):
        if self.value > 1:
            self._set(self.value - 1)

    def _plus_click(self, e):
        if self.value < 100:
            self._set(self.value + 1)
