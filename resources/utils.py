"""
UTILS

Author: Pablo Pizarro R. @ ppizarror.com
"""

# Library imports
import os

# Constants
CREATE_NO_WINDOW = 0x08000000


class Cd(object):
    """Context manager for changing the current working directory."""

    def __init__(self, new_path):
        self.newPath = os.path.expanduser(new_path)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def is_windows():
    """
    Función que retorna True/False si el sistema operativo cliente es Windows o no.

    :return: Boolean
    """
    if os.name == 'nt':
        return True
    return False


def is_linux():
    """
    Función que retorna True/False si el sistema operativo cliente es Linux o no.

    :return: Boolean
    """
    if os.name == 'posix':
        return True
    return False


def is_osx():
    """
    Función que retorna True/False si el sistema operativo cliente es OSX.

    :return: Boolean
    """
    if os.name == 'darwin':
        return True
    return False
