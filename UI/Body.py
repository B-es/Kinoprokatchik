"""Верхний уровень интерфейса: две вкладки — «Смотрим» и «Посмотрели»."""

import flet as ft

from UI.ListBlock import ListBlock
from UI.ButtonMenu import ButtonMenu


class Body(ft.Container):
    """Две вкладки, разделённые линией; в каждой — список и панель информации."""

    def __init__(self, controller, on_reload=None, on_changed=None):
        super().__init__(expand=True)
        self.controller = controller
        self._on_reload = on_reload
        self._on_changed = on_changed

        self.list_block = ListBlock(
            controller=controller,
            isWatching=True,
            on_changed=self._changed,
        )
        self.list_block_watched = ListBlock(
            controller=controller,
            isWatching=False,
            on_changed=self._changed,
        )

        self.button_menu = ButtonMenu(
            on_reload=self.reload,
            on_delete=self.list_block.delete_current,
            on_add=self.list_block.add,
            on_change=self.list_block.change,
            on_watched=self.list_block.move_current,
            watched=False,
        )
        self.button_menu_watched = ButtonMenu(
            on_reload=self.reload,
            on_delete=self.list_block_watched.delete_current,
            on_add=self.list_block_watched.add,
            on_change=self.list_block_watched.change,
            on_watched=self.list_block_watched.move_current,
            watched=True,
        )

        self.tabs = ft.Tabs(
            length=2,
            selected_index=0,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label='Смотрим', icon=ft.Icons.PLAY_ARROW_OUTLINED),
                            ft.Tab(label='Посмотрели', icon=ft.Icons.CHECK),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            ft.Column(
                                expand=True,
                                controls=[self.list_block, ft.Divider(), self.button_menu],
                            ),
                            ft.Column(
                                expand=True,
                                controls=[
                                    self.list_block_watched,
                                    ft.Divider(),
                                    self.button_menu_watched,
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        )
        self.content = self.tabs

    async def _changed(self) -> None:
        """Оба блока перерисовываются: данные общие, меняется только их группа."""
        if self._on_changed is not None:
            await self._on_changed()

    async def reload(self, e=None) -> None:
        """Перечитать список из базы и перерисовать обе вкладки."""
        if self._on_reload is not None:
            await self._on_reload()
        else:
            self.refresh()

    def refresh(self) -> None:
        """Перерисовать оба блока по текущим данным."""
        self.list_block.reload()
        self.list_block_watched.reload()
        self.button_menu.setState(self.list_block.has_current())
        self.button_menu_watched.setState(self.list_block_watched.has_current())
        self.update()
