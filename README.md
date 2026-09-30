# Кинопрокатчик

Десктопное приложение (Flet) для учёта фильмов и сериалов: что смотрим, что
посмотрели, сколько на это ушло времени. База хранится одним JSON-файлом в
Google Drive, поэтому данные доступны с любого компьютера.

## Возможности

1. Сохраняет кино
2. Удаляет кино
3. Автоматически рассчитывает время просмотра
4. Помечает, просмотрено ли
5. Учитывает количество сезонов
6. Учитывает время серии
7. Синхронизирует базу с облаком
8. Три цветовые темы (серая, красная, светлая)

## Стек

- Python 3.10–3.12
- [Flet](https://flet.dev) 1.0.3 — UI на Flutter
- [PyDrive2](https://pypi.org/project/PyDrive2/) — Google Drive
- `dataclasses-json`, `PyYAML`

## Структура проекта

```
main.py                      точка входа: ft.run(main), проверка настроек
pyproject.toml               зависимости + настройки сборки flet
UI/Window.py                 окно: шапка, закрытие с сохранением, загрузка
UI/Body.py                   две вкладки: «Смотрим» и «Посмотрели»
UI/ListBlock.py              список слева, карточка/форма справа
UI/List.py                   строки списка
UI/Input.py                  форма добавления и изменения
UI/ButtonMenu.py             панель кнопок
UI/ExitDialog.py             диалог выхода
UI/Info.py                   карточка фильма (Markdown)
UI/Theme.py                  темы и меню выбора темы
UI/Export.py                 реэкспорт всех частей интерфейса
data/Kino.py                 модели и логика списка
data/DataController.py       связка UI ↔ база (сеть — в отдельном потоке)
data/config.py               пути и настройки, чтение settings.yaml
data/drive/drive.py          клиент Google Drive
data/drive/settings.yaml     настройки PyDrive2 (без секретов)
assets/                      иконки
```

## Установка для разработки

```powershell
git clone https://github.com/B-es/Kinoprokatchik.git
cd Kinoprokatchik
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Настройка доступа к Google Drive

Секретов в репозитории нет и быть не должно. Ключ доступа каждый заводит сам —
это несколько минут в Google Cloud Console.

1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/).
2. Включите **Google Drive API** (APIs & Services → Library).
3. Настройте **OAuth consent screen** (тип *External*, добавьте себя в Test users).
4. Создайте ключ: Credentials → Create credentials → **OAuth client ID** →
   тип приложения **Desktop app**.
5. Скачайте JSON и положите его рядом с приложением как
   `data/drive/client_secrets.json` (шаблон структуры —
   `client_secrets.example.json` в корне репозитория). Файла в репозитории нет
   специально: он в `.gitignore`.
6. Создайте на Google Drive пустой текстовый файл, скопируйте его ID из ссылки
   (`https://drive.google.com/file/d/<ID>/view`) и впишите в
   `data/drive/settings.yaml` → `drive_file_id`.

При первом запуске откроется браузер — войдите в аккаунт и разрешите доступ.
Токен сохранится в пользовательскую папку и в репозиторий не попадёт:

- Windows: `%LOCALAPPDATA%\Kinoprokatchik\credentials.json`
- Linux: `~/.local/share/Kinoprokatchik/credentials.json`
- macOS: `~/Library/Application Support/Kinoprokatchik/credentials.json`

### Переменные окружения

| Переменная | Назначение |
|---|---|
| `KINOPROKATCHIK_DRIVE_FILE_ID` | переопределяет `drive_file_id` из `settings.yaml` |
| `KINOPROKATCHIK_DATA_DIR` | папка для `credentials.json` и прочих изменяемых файлов |
| `KINOPROKATCHIK_SETTINGS` | путь к своему `settings.yaml` вместо `data/drive/settings.yaml` |

## Запуск

```powershell
python main.py
```

Быстрый запуск через Flet с hot-reload:

```powershell
flet run main.py
```

## Особенности Flet 1.0.3

Проект переписан на актуальный API Flet. Если будете что-то дописывать,
учитывайте отличия от 0.2x — они неочевидные:

- Запуск только через `ft.run(main)` (или `ft.run_async`). `ft.app()`,
  `ft.app_async()` и параметр `target` удалены.
- **Позиционные аргументы у контролов запрещены**: базовые классы объявлены
  `@dataclass(kw_only=True)`, поэтому `ft.Text("привет")` упадёт. Правильно:
  `ft.Text(value="привет")`.
- Обработчики-корутины (`async def`) приложение ожидает (`await`), синхронные
  вызываются как есть. Синхронный код исполняется в том же цикле событий, что и
  UI, поэтому всё сетевое и блокирующее идёт через `asyncio.to_thread`
  (см. `data/DataController.py`).
- `page.window_*` больше нет — только `page.window.*`
  (`page.window.width`, `page.window.prevent_close`, `await page.window.center()`,
  `await page.window.destroy()`).
- Событие закрытия окна разбирается по типу: `e.type == ft.WindowEventType.CLOSE`
  (раньше сравнивали `e.data == "close"`).
- `page.dialog` и `page.overlay` удалены: `page.show_dialog(...)` /
  `page.pop_dialog()`.
- `ft.Tabs` теперь только контейнер: `ft.Tabs(length=..., content=ft.Column(...))`
  с `ft.TabBar(tabs=[...])` и `ft.TabBarView(controls=[...])`.
- `ft.ElevatedButton` удалён → `ft.Button`. Иконки и цвета:
  `ft.Icons.НАЗВАНИЕ` / `ft.Colors.НАЗВАНИЕ` (строчные варианты удалены).
- У `ft.Text` вместо `text_theme` используется `theme_style`, у `ft.Theme` нет
  `text_theme` — шрифт задаётся `font_family`, цвета через `ft.ColorScheme`.
- `.update()` у контрола, которого ещё нет на странице, бросает `RuntimeError`,
  — в коде такие вызовы обёрнуты в `_safe_update()`.

## Сборка

### Windows (нативно, через Flet)

Нужен Flutter SDK: `flet build` скачает подходящую версию в `$HOME\flutter`,
если её нет в `PATH`. Параметры сборки (имя, артефакт, исключения) описаны в
`pyproject.toml`, поэтому команда короткая:

```powershell
pip install flet
flet build windows --yes
```

Готовый бандл — в `build\windows\` (`.exe` плюс служебные папки с Python,
зависимостями и ассетами).

Полный вариант той же команды, если нужно переопределить метаданные:

```powershell
flet build windows --project kinoprokatchik --product "Кинопрокатчик" --yes
```

Полезные флаги: `--verbose` (подробный лог), `--no-rich-output` (обычный текст,
нужен в CI), `--python-version 3.12` (зафиксировать версию Python в бандле),
`--output <папка>` (куда положить результат).

### Иконка

`flet build` генерирует иконки и сплэши из `assets/icon.png`. Файл должен быть
**не меньше 1024×1024** PNG с прозрачностью, иначе сборка падает на генерации
иконок. В репозитории лежит увеличенная до 1024×1024 копия старой иконки —
перед релизом замените её исходником в высоком разрешении.

### Через GitHub Actions

Workflow `.github/workflows/build-windows.yml` собирает Windows-бандл и
прикладывает его артефактом к запуску. Секреты для сборки не нужны:
`client_secrets.json` пользователь кладёт рядом с `.exe` сам.

## Лицензия

Учебный проект, распространяется как есть.
