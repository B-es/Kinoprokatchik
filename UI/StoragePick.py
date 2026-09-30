"""Меню выбора хранилища базы: локальный файл или Google Drive."""

import flet as ft

from data.storage import MODE_TITLES, STORAGE_DRIVE, STORAGE_LOCAL

__all__ = ['MODE_ICONS', 'StoragePick']

#: Иконки режимов хранения.
MODE_ICONS = {
    STORAGE_LOCAL: ft.Icons.FOLDER_OUTLINED,
    STORAGE_DRIVE: ft.Icons.CLOUD_OUTLINED,
}


class StoragePick(ft.PopupMenuButton):
    """Кнопка выбора хранилища. О смене режима сообщает через ``on_change``."""

    def __init__(self, current_mode: str, on_change=None):
        self.current_mode = current_mode
        self.on_mode_change = on_change
        super().__init__(
            icon=MODE_ICONS.get(current_mode, ft.Icons.STORAGE_OUTLINED),
            tooltip=f'База: {MODE_TITLES.get(current_mode, current_mode)}',
        )

        self.items = [
            ft.PopupMenuItem(
                content=ft.Text(value=title),
                icon=MODE_ICONS[mode],
                data=mode,
                checked=mode == current_mode,
                on_click=self.changeMode,
            )
            for mode, title in MODE_TITLES.items()
        ]

    def changeMode(self, e) -> None:
        mode = e.control.data
        if mode == self.current_mode:
            return
        self.current_mode = mode
        for item in self.items:
            item.checked = item.data == mode
        self.icon = MODE_ICONS.get(mode, ft.Icons.STORAGE_OUTLINED)
        self.tooltip = f'База: {MODE_TITLES.get(mode, mode)}'
        self.update()
        if self.on_mode_change is not None:
            self.on_mode_change(mode)
