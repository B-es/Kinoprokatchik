"""Карточка с информацией о выбранном фильме."""

import flet as ft

from data.Kino import Kino


class InfoPane(ft.Markdown):
    """InfoPane(ft.Markdown) — показывает данные фильма в виде markdown."""

    def __init__(self, kino: Kino = None):
        super().__init__()
        self.kino = kino
        self.selectable = True
        self.extension_set = ft.MarkdownExtensionSet.GITHUB_FLAVORED
        self.code_theme = 'darcula'
        if kino is not None:
            self.value = self.kinoToStr()

    def _safe_update(self) -> None:
        """update() только если контрол уже на странице."""
        try:
            self.update()
        except RuntimeError:
            pass

    def new(self, kino: Kino) -> None:
        self.kino = kino
        self.value = self.kinoToStr()
        self._safe_update()

    def clear(self) -> None:
        self.kino = None
        self.value = ''
        self._safe_update()

    def kinoToStr(self) -> str:
        kino = self.kino
        if kino is None:
            return ''
        return (
            f'# Номер: {kino.number}\n'
            f'## Название: {kino.name}\n'
            f'## Кол-во сезонов: {kino.seasonCount}\n'
            f'## Кол-во серий: {kino.episodeCounts}\n'
            f'## Время серии в сезоне: {kino.episodeTimes}\n'
            f'## Общее время просмотра: {kino.totalTime:.1f} мин\n'
            f"## Просмотрено: {'+' if kino.isWatched else '-'}"
        )
