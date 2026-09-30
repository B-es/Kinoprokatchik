"""Хранилище базы: локальный файл на диске.

Класс синхронный, как и ``DriveStorage``, поэтому в Flet 1.x вызывается из
отдельного потока (``asyncio.to_thread`` в ``data/DataController.py``).
"""

import os
from pathlib import Path


class LocalStorage:
    """Файл-база на диске: чтение и запись JSON-строки."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def get(self) -> str:
        """Прочитать базу. Отсутствие файла — это пустая база, а не ошибка."""
        if not self.path.exists():
            return ''
        return self.path.read_text(encoding='utf-8')

    def save(self, json: str) -> None:
        """Записать базу: сначала во временный файл, чтобы не потерять данные."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + '.tmp')
        temporary.write_text(json, encoding='utf-8')
        os.replace(temporary, self.path)

    def clear(self) -> None:
        """Очистить базу, оставив файл на месте."""
        self.save('')
