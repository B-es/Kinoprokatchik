"""Пути и настройки приложения.

Никаких секретов в коде: токены и client_secrets лежат в файлах, которые
создаёт пользователь и которые перечислены в .gitignore.
"""

import os
import sys
from pathlib import Path

import yaml

DRIVE_DIR = Path(__file__).resolve().parent / 'drive'
SETTINGS_PATH = DRIVE_DIR / 'settings.yaml'
CLIENT_SECRETS_PATH = DRIVE_DIR / 'client_secrets.json'

ENV_FILE_ID = 'KINOPROKATCHIK_DRIVE_FILE_ID'
ENV_DATA_DIR = 'KINOPROKATCHIK_DATA_DIR'
ENV_STORAGE = 'KINOPROKATCHIK_STORAGE'

#: Режимы хранения базы.
STORAGE_AUTO = 'auto'
STORAGE_LOCAL = 'local'
STORAGE_DRIVE = 'drive'
STORAGE_MODES = (STORAGE_AUTO, STORAGE_LOCAL, STORAGE_DRIVE)

_DEFAULT_SETTINGS = (
    'save_credentials: true\n'
    "oauth_scope: ['https://www.googleapis.com/auth/drive']\n"
    'save_credentials_backend: file\n'
)


def app_dir() -> Path:
    """Корень приложения: папка со скриптами или распакованный бандл Flet."""
    if getattr(sys, 'frozen', False):
        return Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent


def user_data_dir() -> Path:
    """Папка для изменяемых пользовательских файлов (токен OAuth и т.п.)."""
    override = os.environ.get(ENV_DATA_DIR)
    if override:
        directory = Path(override).expanduser()
    elif sys.platform == 'win32':
        base = os.environ.get('LOCALAPPDATA') or os.path.expanduser('~')
        directory = Path(base) / 'Kinoprokatchik'
    elif sys.platform == 'darwin':
        directory = Path.home() / 'Library' / 'Application Support' / 'Kinoprokatchik'
    else:
        base = os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share')
        directory = Path(base) / 'Kinoprokatchik'
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _absolute(value: str) -> str:
    """Приводит путь из settings.yaml к абсолютному, считая относительные от data/drive/."""
    path = Path(value)
    if not path.is_absolute():
        path = DRIVE_DIR / path
    return str(path.resolve()).replace('\\', '/')


def settings_path() -> Path:
    """Путь к settings.yaml (переопределяется переменной окружения)."""
    override = os.environ.get('KINOPROKATCHIK_SETTINGS')
    if override:
        return Path(override).expanduser()
    return SETTINGS_PATH


def load_settings() -> dict:
    """Читает настройки PyDrive2. Если их нет — создаёт файл-заготовку."""
    path = settings_path()
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_DEFAULT_SETTINGS, encoding='utf-8')

    settings = yaml.safe_load(path.read_text(encoding='utf-8')) or {}

    if settings.get('client_config_file'):
        settings['client_config_file'] = _absolute(settings['client_config_file'])
    elif CLIENT_SECRETS_PATH.exists():
        settings['client_config_file'] = str(
            CLIENT_SECRETS_PATH.resolve()
        ).replace('\\', '/')

    if settings.get('save_credentials_file'):
        settings['save_credentials_file'] = _absolute(settings['save_credentials_file'])
    else:
        stored = user_data_dir() / 'credentials.json'
        settings['save_credentials_file'] = str(stored).replace('\\', '/')

    return settings


def drive_file_id() -> str:
    """ID файла-базы на Google Drive. Переопределяется переменной окружения."""
    return os.environ.get(ENV_FILE_ID) or str(load_settings().get('drive_file_id') or '')


def has_client_secrets() -> bool:
    """Есть ли OAuth-клиент Google (без него Drive недоступен)."""
    return CLIENT_SECRETS_PATH.exists()


def storage_mode() -> str:
    """Выбранный режим хранилища. Переопределяется переменной окружения."""
    raw = os.environ.get(ENV_STORAGE) or load_settings().get('storage') or STORAGE_AUTO
    mode = str(raw).strip().lower()
    return mode if mode in STORAGE_MODES else STORAGE_AUTO


def check_settings() -> str:
    """Возвращает текст ошибки для первого экрана или пустую строку, если всё готово."""
    # Импорт здесь, чтобы не было цикла: data/storage.py сам читает config.
    from data.storage import STORAGE_DRIVE, resolve_mode

    if resolve_mode() == STORAGE_DRIVE:
        if not CLIENT_SECRETS_PATH.exists():
            return (
                'Выбрано хранение в Google Drive, но не найден client_secrets.json.\n\n'
                'Положите файл по пути:\n'
                f'{CLIENT_SECRETS_PATH}\n\n'
                'Инструкция — в README.md, раздел «Настройка доступа к Google Drive».'
            )

        if not drive_file_id():
            return (
                'Не задан ID файла базы данных на Google Drive.\n\n'
                f'Укажите drive_file_id в {settings_path()}\n'
                f'или задайте переменную окружения {ENV_FILE_ID}.'
            )

        return ''

    # Режим local: проверяем, что папку данных вообще можно создать и записать.
    try:
        directory = user_data_dir()
        probe = directory / '.write-check'
        probe.write_text('', encoding='utf-8')
        probe.unlink()
    except OSError as error:
        return (
            'Не удалось получить доступ к папке данных.\n\n'
            f'{user_data_dir()}\n\n'
            f'Ошибка: {error}'
        )

    return ''


if __name__ == '__main__':
    app_dir()
    print('settings :', settings_path())
    print('secrets  :', CLIENT_SECRETS_PATH)
    print('data dir :', user_data_dir())
    print('storage  :', storage_mode())
    print('file id  :', drive_file_id() or '(не задан)')
    print('check    :', check_settings() or 'ok')
