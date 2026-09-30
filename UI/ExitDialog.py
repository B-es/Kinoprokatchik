"""Модальное окно подтверждения выхода."""

import flet as ft


async def confirm_exit(page: ft.Page, on_save=None) -> bool:
    """Спрашивает, сохранять ли изменения перед выходом.

    Возвращает ``True``, если приложение надо закрыть. Если пользователь выбрал
    сохранение, сначала вызывается ``on_save`` (может быть корутиной).
    """
    decision = {'quit': False}

    async def close_dialog(save: bool) -> None:
        if save and on_save is not None:
            page.show_dialog(
                ft.AlertDialog(
                    modal=True,
                    content=ft.Row(
                        controls=[
                            ft.ProgressRing(width=20, height=20, stroke_width=2),
                            ft.Text(value='Сохраняю изменения…'),
                        ],
                        tight=True,
                    ),
                )
            )
            await on_save()
        decision['quit'] = True
        page.pop_dialog()

    async def save_click(e):
        await close_dialog(save=True)

    async def skip_click(e):
        await close_dialog(save=False)

    async def cancel_click(e):
        page.pop_dialog()

    page.show_dialog(
        ft.AlertDialog(
            modal=True,
            title=ft.Text(value='Выход'),
            content=ft.Text(value='Сохранить изменения перед закрытием?'),
            actions=[
                ft.TextButton(content='Сохранить и выйти', on_click=save_click),
                ft.TextButton(content='Выйти без сохранения', on_click=skip_click),
                ft.TextButton(content='Отмена', on_click=cancel_click),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    )

    return decision['quit']
