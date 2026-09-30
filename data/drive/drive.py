"""Обёртка над Google Drive через PyDrive2.

Класс синхронный и ходит в сеть, поэтому в Flet 1.x его методы вызываются
из отдельных потоков через ``asyncio.to_thread`` (см. ``data/DataController.py``).
"""

from pathlib import Path

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


class DriveStorage:
    """Файл-база на Google Drive: чтение и запись JSON-строки."""

    def __init__(self, settings: dict, file_id: str) -> None:
        if not file_id:
            raise ValueError('Не задан ID файла базы данных на Google Drive.')

        gauth = GoogleAuth(settings=settings)
        gauth.LocalWebserverAuth()
        self._drive = GoogleDrive(gauth)
        self._file_id = file_id
        self.file = self._drive.CreateFile({'id': file_id})
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


def upload_file(path: Path, file_id: str = '') -> str:
    """Загружает файл в Google Drive и возвращает его ID.

    Если ``file_id`` передан, содержимое существующего файла перезаписывается.
    Нужно один раз, чтобы перенести локальную базу в облако.
    """
    from data.config import load_settings

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f'Нет файла для загрузки: {path}')

    settings = load_settings()
    if not settings.get('client_config_file'):
        raise ValueError('Не найден client_secrets.json — без него Drive недоступен.')

    gauth = GoogleAuth(settings=settings)
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    handle = drive.CreateFile({'id': file_id}) if file_id else drive.CreateFile()
    if not file_id:
        handle['title'] = path.name
    handle.SetContentFile(str(path))
    handle.Upload()
    return handle['id']
