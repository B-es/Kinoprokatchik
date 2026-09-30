"""Окно приложения: шапка, вкладки, загрузка и сохранение данных."""

import flet as ft

from data.DataController import DataController
from UI.Body import Body
from UI.ExitDialog import confirm_exit
from UI.Theme import ThemePick

__all__ = ['start_window']


async def start_window(page: ft.Page, controller: DataController) -> None:
    """Настраивает окно и запускает цикл работы приложения."""
    page.title = 'Кинопрокатчик'
    page.padding = 0

    # --- закрытие окна ---
    closing = {'done': False}

    async def window_event(e):
        if e.type != ft.WindowEventType.CLOSE:
            return
        if closing['done']:
            return
        if await confirm_exit(page, on_save=controller.save):
            closing['done'] = True
            await page.window.destroy()

    page.window.prevent_close = True
    page.window.width = 1100
    page.window.height = 800
    page.window.resizable = False
    page.window.on_event = window_event

    # --- верхняя панель ---
    title = ft.Text(value='Кинопрокатчик', theme_style=ft.TextThemeStyle.TITLE_MEDIUM)

    def apply_theme(theme: ft.Theme) -> None:
        page.theme = theme
        scheme = theme.color_scheme or ft.ColorScheme()
        title.color = scheme.on_primary
        page.update()

    theme_pick = ThemePick(on_change=apply_theme)
    apply_theme(theme_pick.current_theme)

    # --- интерфейс ---
    loading = ft.Text(value='Загружаю данные из Google Drive…')
    problem = ft.Text(value='', color=ft.Colors.ERROR)

    def refresh_buttons() -> None:
        body.button_menu.setState(body.list_block.has_current())
        body.button_menu_watched.setState(body.list_block_watched.has_current())

    async def sync_state() -> None:
        """После изменения данных обновляем доступность кнопок."""
        refresh_buttons()
        page.update()

    async def reload_data() -> None:
        """Перечитывает базу с Google Drive."""
        await read_database()
        body.refresh()
        page.update()

    body = Body(controller=controller, on_reload=reload_data, on_changed=sync_state)

    async def read_database() -> None:
        """Читает базу и показывает ошибку вместо падения, если не получилось."""
        loading.visible = True
        problem.value = ''
        page.update()
        try:
            await controller.load()
        except Exception as error:  # noqa: BLE001 — показываем пользователю причину
            problem.value = f'Не удалось прочитать базу: {error}'
        loading.visible = False
        page.update()

    page.appbar = ft.AppBar(
        title=title,
        center_title=True,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        actions=[theme_pick],
    )
    page.add(
        ft.Column(
            expand=True,
            controls=[
                loading,
                problem,
                body,
            ],
        )
    )

    await page.window.center()

    # --- первая загрузка ---
    await read_database()
    refresh_buttons()
    body.refresh()
    page.update()
