"""Панель кнопок управления списком."""

import flet as ft


class ButtonMenu(ft.Container):
    """Кнопки: обновить, удалить, добавить, изменить, перенести."""

    def __init__(self, on_reload, on_delete, on_add, on_change, on_watched, watched: bool = False):
        super().__init__()
        self.on_reload = on_reload
        self.on_delete = on_delete
        self.on_add = on_add
        self.on_change = on_change
        self.on_watched = on_watched
        self.watched = watched

        self._delete_button = self._button(ft.Icons.DELETE_OUTLINED, 'Удалить', on_delete)
        self._change_button = self._button(ft.Icons.CHANGE_CIRCLE_OUTLINED, 'Изменить', on_change)
        self._watched_button = self._button(
            ft.Icons.CHECK_CIRCLE_OUTLINE, 'Смотрим' if watched else 'Посмотрели', on_watched
        )

        self.content = ft.Row(
            controls=[
                self._button(ft.Icons.REPLAY_OUTLINED, 'Обновить', on_reload),
                self._delete_button,
                self._button(ft.Icons.ADD_TASK_OUTLINED, 'Добавить', on_add),
                self._change_button,
                self._watched_button,
            ]
        )
        self.border_radius = 3
        self.padding = 5

    @staticmethod
    def _button(icon, tooltip: str, on_click) -> ft.IconButton:
        return ft.IconButton(icon=icon, tooltip=tooltip, on_click=on_click)

    def setState(self, has_current: bool) -> None:
        """Гасит кнопки, которым нужен выбранный фильм."""
        for button in (self._delete_button, self._change_button, self._watched_button):
            if button.disabled == (not has_current):
                continue
            button.disabled = not has_current
            button.update()
