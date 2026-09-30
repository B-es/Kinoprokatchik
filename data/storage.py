"""Выбор хранилища базы: локальный файл или Google Drive.

Режим берётся из переменной окружения ``KINOPROKATCHIK_STORAGE``, затем из
``storage`` в settings.yaml, и если там ничего нет — подбирается автоматически:
есть ``drive_file_id`` и ``client_secrets.json``, значит облако, иначе файл.
"""

from pathlib import Path

from data.config import (
    STORAGE_AUTO,
    STORAGE_DRIVE,
    STORAGE_LOCAL,
    drive_file_id,
    load_settings,
    storage_mode,
    user_data_dir,
)
from data.drive.drive import DriveStorage
from data.local.local import LocalStorage
from data.storage_protocol import Storage

__all__ = [
    'DATABASE_FILE_NAME',
    'MODE_TITLES',
    'STORAGE_DRIVE',
    'STORAGE_LOCAL',
    'Storage',
    'available_modes',
    'database_path',
    'mode_available',
    'open_database',
    'resolve_mode',
]

#: Имя файла локальной базы в пользовательской папке.
DATABASE_FILE_NAME = 'kinos.json'

#: Человеческие названия режимов для интерфейса.
MODE_TITLES = {
    STORAGE_LOCAL: 'Локальный файл',
    STORAGE_DRIVE: 'Google Drive',
}


def mode_available(mode: str, settings: dict = None) -> bool:
    """Доступен ли режим на этой машине (есть ли учётные данные для Drive)."""
    if mode == STORAGE_LOCAL:
        return True
    settings = settings if settings is not None else load_settings()
    return bool(settings.get('client_config_file')) and bool(drive_file_id())


def available_modes() -> list:
    """Режимы, которые можно включить прямо сейчас."""
    settings = load_settings()
    return [mode for mode in (STORAGE_LOCAL, STORAGE_DRIVE) if mode_available(mode, settings)]


def resolve_mode(settings: dict = None) -> str:
    """Режим хранилища: local или drive (никогда не auto)."""
    settings = settings if settings is not None else load_settings()
    mode = storage_mode()
    if mode != STORAGE_AUTO:
        return mode
    return STORAGE_DRIVE if mode_available(STORAGE_DRIVE, settings) else STORAGE_LOCAL


def database_path() -> Path:
    """Путь к локальному файлу базы."""
    return user_data_dir() / DATABASE_FILE_NAME


def open_database(mode: str, settings: dict = None) -> Storage:
    """Создаёт хранилище выбранного режима."""
    settings = settings if settings is not None else load_settings()

    if mode == STORAGE_DRIVE:
        return DriveStorage(settings=settings, file_id=drive_file_id())

    if mode == STORAGE_LOCAL:
        return LocalStorage(database_path())

    raise ValueError(f'Неизвестный режим хранилища: {mode!r}')
