"""Темы оформления и меню выбора темы."""

import flet as ft


def _dark_gray() -> ft.Theme:
    return ft.Theme(
        font_family='Times New Roman',
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.GREY_300,
            on_primary=ft.Colors.GREY_900,
            secondary=ft.Colors.GREY_600,
        ),
    )


def _dark_red() -> ft.Theme:
    return ft.Theme(
        font_family='Times New Roman',
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.RED,
            on_primary=ft.Colors.WHITE,
            secondary=ft.Colors.RED_ACCENT_700,
        ),
    )


def _light_gray() -> ft.Theme:
    return ft.Theme(
        font_family='Arial',
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_GREY_300,
            on_primary=ft.Colors.BLACK,
            secondary=ft.Colors.BLUE_GREY_100,
        ),
    )


def themes() -> dict:
    """Все доступные темы."""
    return {
        'Серая': _dark_gray(),
        'Красная': _dark_red(),
        'Светлая': _light_gray(),
    }


class ThemePick(ft.PopupMenuButton):
    """Кнопка выбора темы. О выборе сообщает через ``on_change``."""

    def __init__(self, on_change=None):
        self.all_themes = themes()
        self.current_theme = self.all_themes['Красная']
        self.on_theme_change = on_change
        super().__init__(icon=ft.Icons.COLOR_LENS_OUTLINED)

        self.items = [
            ft.PopupMenuItem(
                content=ft.Text(value=name),
                data=name,
                on_click=self.changeTheme,
            )
            for name in self.all_themes
        ]

    def changeTheme(self, e) -> None:
        name = e.control.data
        self.current_theme = self.all_themes[name]
        for item in self.items:
            item.checked = item.data == name
        self.update()
        if self.on_theme_change is not None:
            self.on_theme_change(self.current_theme)
