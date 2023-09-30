"""
UTILS

Author: Pablo Pizarro R. @ ppizarror.com
"""

__all__ = ['Cd', 'get_local_path']

import os
from pathlib import Path

# Constants
CREATE_NO_WINDOW = 0x08000000


class Cd(object):
    """
    Context manager for changing the current working directory.
    """

    def __init__(self, new_path):
        self.newPath = os.path.expanduser(new_path)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def get_user_path() -> str:
    """
    :return: Returns the user path
    """
    return os.path.expanduser('~')


def get_local_path() -> str:
    """
    :return: Returns the app local path
    """
    appdata = os.getenv('LOCALAPPDATA')
    if appdata is None:
        appdata = os.path.join(get_user_path(), 'Applications')

    path = os.path.join(appdata, 'MLSTRUCT.convertpdf')
    return make_path_if_not_exists(path)


def make_path_if_not_exists(path: str) -> str:
    """
    Create the path if not exists.

    :param path: Path
    :return: Path
    """
    if not os.path.isdir(path):
        Path(path).mkdir(parents=True, exist_ok=True)
    return path
