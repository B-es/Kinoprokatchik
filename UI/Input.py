"""Форма добавления и изменения фильма."""

import flet as ft

from data.Kino import Kino, make_kino_dict
from UI.Counter import Counter


class InputForm(ft.Container):
    """Правая панель с формой. Результат отдаёт через ``on_apply``."""

    def __init__(self, on_exit, on_apply, kino: Kino = None, initValue: int = 1):
        super().__init__(expand=True)
        self.on_exit = on_exit
        self.on_apply = on_apply

        number = int(kino.number) if kino is not None else int(initValue)

        self.counter = Counter(initValue=number)
        self.name_field = ft.TextField(label='Название', autofocus=True)
        self.counts_field = ft.TextField(label='Количество серий [...]')
        self.times_field = ft.TextField(label='Время серии в сезоне [...] (мин)')

        self.content = ft.Column(
            controls=[
                self.counter,
                self.name_field,
                self.counts_field,
                self.times_field,
                ft.Row(
                    controls=[
                        ft.TextButton(content='Выйти', on_click=on_exit),
                        ft.TextButton(content='Сохранить', on_click=self._save_click),
                    ]
                ),
            ]
        )

        if kino is not None:
            self.kino = kino
            self.setData(kino)

    def setData(self, kino: Kino) -> None:
        """Заполняет поля данными существующего фильма."""
        self.name_field.value = kino.name
        self.counts_field.value = ', '.join(map(str, kino.episodeCounts))
        self.times_field.value = ', '.join(map(str, kino.episodeTimes))

    @staticmethod
    def _parse(raw: str) -> list:
        """Разбирает строку «12, 14» в список целых чисел."""
        return [int(part) for part in raw.replace(' ', '').split(',') if part]

    def _save_click(self, e):
        try:
            counts = self._parse(self.counts_field.value or '')
            times = self._parse(self.times_field.value or '')
        except ValueError:
            self.counts_field.error = 'Только числа, через запятую'
            self.update()
            return

        name = (self.name_field.value or '').strip()

        if not name:
            self.name_field.error = 'Укажите название'
            self.update()
            return

        if len(counts) != len(times) or not counts:
            self.counts_field.error = 'Число серий и число таймингов должны совпадать'
            self.update()
            return

        self.counts_field.error = None
        self.name_field.error = None
        self.on_apply(
            make_kino_dict(
                number=self.counter.value,
                name=name,
                episodeCounts=counts,
                episodeTimes=times,
            )
        )
