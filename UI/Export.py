"""Удобный доступ ко всем частям интерфейса из одного места."""

from UI.Body import Body
from UI.ButtonMenu import ButtonMenu
from UI.Counter import Counter
from UI.ExitDialog import confirm_exit
from UI.Info import InfoPane
from UI.Input import InputForm
from UI.List import KinoList, KinoTile
from UI.ListBlock import ListBlock
from UI.Theme import ThemePick, themes
from UI.Window import start_window

__all__ = [
    'Body',
    'ButtonMenu',
    'Counter',
    'confirm_exit',
    'InfoPane',
    'InputForm',
    'KinoList',
    'KinoTile',
    'ListBlock',
    'ThemePick',
    'themes',
    'start_window',
]
