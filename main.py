"""Точка входа приложения «Кинопрокатчик».

Flet 1.x: приложение запускается через ``ft.run(main)``, где ``main`` может быть
как обычной, так и асинхронной функцией. Долгие операции вынесены в функции
окна, чтобы интерфейс не подвисал.
"""

import flet as ft

from data.config import check_settings, drive_file_id, load_settings
from data.DataController import DataController


async def show_config_error(page: ft.Page, message: str) -> None:
    """Показывает, чего не хватает для запуска, вместо падения со стектрейсом."""
    page.title = 'Кинопрокатчик — настройка'
    await page.window.center()
    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Container(
                expand=True,
                padding=30,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(name=ft.Icons.KEY_OFF_OUTLINED, size=48),
                        ft.Text(
                            value='Нужна настройка',
                            theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                        ),
                        ft.Text(
                            value=message,
                            selectable=True,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                ),
            ),
        )
    )


async def main(page: ft.Page):
    """Собирает интерфейс и передаёт управление окну."""
    error = check_settings()
    if error:
        await show_config_error(page, error)
        return

    controller = DataController(settings=load_settings(), file_id=drive_file_id())

    from UI.Window import start_window

    await start_window(page, controller)


if __name__ == '__main__':
    ft.run(main)
