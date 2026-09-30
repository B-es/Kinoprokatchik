"""Окно приложения: шапка, вкладки, загрузка и сохранение данных."""

import flet as ft

from data.config import STORAGE_DRIVE, STORAGE_LOCAL
from data.DataController import DataController
from data.storage import MODE_TITLES
from UI.Body import Body
from UI.ExitDialog import confirm_exit
from UI.StoragePick import MODE_ICONS, StoragePick
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
        if await confirm_exit(page, on_save=active['controller'].save):
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

    # Контроллер может смениться при переключении хранилища, поэтому держим его в словаре.
    active = {'controller': controller}

    mode_icon = ft.Icon(icon=MODE_ICONS.get(controller.mode, ft.Icons.STORAGE_OUTLINED), size=18)
    mode_text = ft.Text(
        value=MODE_TITLES.get(controller.mode, controller.mode),
        theme_style=ft.TextThemeStyle.LABEL_LARGE,
    )

    def show_mode(mode: str) -> None:
        mode_text.value = MODE_TITLES.get(mode, mode)
        mode_icon.icon = MODE_ICONS.get(mode, ft.Icons.STORAGE_OUTLINED)
        page.update()

    # --- интерфейс ---
    loading = ft.Text(value='')
    problem = ft.Text(value='', color=ft.Colors.ERROR)

    def refresh_buttons() -> None:
        body.button_menu.setState(body.list_block.has_current())
        body.button_menu_watched.setState(body.list_block_watched.has_current())

    async def sync_state() -> None:
        """После изменения данных обновляем доступность кнопок."""
        refresh_buttons()
        page.update()

    async def reload_data() -> None:
        """Перечитывает базу из текущего хранилища."""
        await read_database()
        body.refresh()
        page.update()

    body = Body(controller=controller, on_reload=reload_data, on_changed=sync_state)

    async def read_database() -> None:
        """Читает базу и показывает ошибку вместо падения, если не получилось."""
        current = active['controller']
        loading.value = f'Загружаю данные: {MODE_TITLES.get(current.mode, current.mode)}…'
        loading.visible = True
        problem.value = ''
        page.update()
        try:
            await current.load()
        except Exception as error:  # noqa: BLE001 — показываем пользователю причину
            problem.value = f'Не удалось прочитать базу: {error}'
        loading.visible = False
        page.update()

    async def confirm_move() -> bool:
        """Спрашиваем, переносить ли текущий список в новое хранилище."""
        answer = {'ok': False}

        async def apply(e):
            answer['ok'] = True
            page.pop_dialog()

        async def cancel(e):
            page.pop_dialog()

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text(value='Смена хранилища'),
                content=ft.Text(
                    value='Перенести текущий список в новое хранилище?\n\n'
                    'Для Google Drive откроется браузер для входа в аккаунт.',
                ),
                actions=[
                    ft.TextButton(content='Только переключить', on_click=cancel),
                    ft.TextButton(content='Перенести', on_click=apply),
                ],
            )
        )
        return answer['ok']

    async def switch_storage(mode: str) -> None:
        """Переключает базу на другой носитель, при желании перенося список."""
        body.button_menu.setEnabled(False)
        body.button_menu_watched.setEnabled(False)
        loading.value = f'Готовлю {MODE_TITLES.get(mode, mode)}…'
        loading.visible = True
        page.update()

        new_controller = DataController(mode)
        try:
            if await confirm_move():
                await new_controller.migrate(mode)
            else:
                await new_controller.load()
            active['controller'] = new_controller
            body.setController(new_controller)
            problem.value = ''
        except Exception as error:  # noqa: BLE001 — причину показываем пользователю
            problem.value = f'Не удалось переключить хранилище: {error}'
            loading.visible = False
            page.update()
            return

        loading.visible = False
        show_mode(mode)
        await reload_data()
        refresh_buttons()

    storage_pick = StoragePick(current_mode=controller.mode, on_change=switch_storage)

    page.appbar = ft.AppBar(
        leading=ft.Row(controls=[storage_pick], tight=True),
        leading_width=56,
        title=title,
        center_title=True,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        actions=[ft.Row(controls=[mode_icon, mode_text], tight=True), theme_pick],
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
