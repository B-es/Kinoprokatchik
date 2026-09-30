"""Обёртка над Google Drive через PyDrive2.

Класс синхронный и ходит в сеть, поэтому в Flet 1.x его методы вызываются
из отдельных потоков через ``asyncio.to_thread`` (см. ``data/DataController.py``).
"""

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


class Database:
    """Файл-база на Google Drive: чтение и запись JSON-строки."""

    def __init__(self, settings: dict, file_id: str) -> None:
        if not file_id:
            raise ValueError('Не задан ID файла базы данных на Google Drive.')

        gauth = GoogleAuth(settings=settings)
        gauth.LocalWebserverAuth()
        drive = GoogleDrive(gauth)
        self.file = drive.CreateFile({'id': file_id})
        self._strip_leading_newline()

    def _strip_leading_newline(self) -> None:
        """Убирает перевод строки, который Drive иногда добавляет в начало файла."""
        text = self.file.GetContentString()
        if text.startswith('\n'):
            self.file.SetContentString(text.replace('\n', '', 1))

    def get(self) -> str:
        """Получить данные из базы."""
        return self.file.GetContentString()

    def save(self, json: str) -> None:
        """Обновить данные в базе."""
        self.file.SetContentString(json)
        self.file.Upload()

    def clear(self) -> None:
        """Очистить базу."""
        self.file.SetContentString('')
        self.file.Upload()
