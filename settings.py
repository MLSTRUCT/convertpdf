# coding=utf-8
"""
SETTINGS

Author: Pablo Pizarro R. @ ppizarror.com
"""

# Import libraries
import os
from tkinter import *


def is_linux():
    if os.name == 'posix':
        return True
    return False


def is_osx():
    if os.name == 'darwin':
        return True
    return False


def is_windows():
    if os.name == 'nt':
        return True
    return False


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


# Constants
if is_windows():
    DEFAULT_FONT_TITLE = 'Arial', 10
elif is_osx():
    DEFAULT_FONT_TITLE = 'Arial', 15
elif is_linux():
    DEFAULT_FONT_TITLE = 'Arial', 9
else:
    DEFAULT_FONT_TITLE = 'Arial', 10
COMMENT_COLOR = '#666666'


def del_matrix(matrix):
    a = len(matrix)
    if a > 0:
        for k in range(a):
            matrix.pop(0)


class SettingsDialog(object):
    """
    Settings dialogs.
    """

    def __init__(self, properties):
        self.lang = properties[0]
        title = self.lang['SETTINGS_TITLE']
        icon = properties[1]
        type_object = properties[2]
        size = properties[3]
        inputs = properties[4]
        self.w = Tk()
        self.w.protocol('WM_DELETE_WINDOW', self.kill)
        self.values = []
        if size[0] != 0 and size[1] != 0:
            self.w.minsize(width=size[0], height=size[1])
            self.w.geometry(
                '%dx%d+%d+%d' % (size[0], size[1], (self.w.winfo_screenwidth(
                ) - size[0]) / 2, (self.w.winfo_screenheight() - size[1]) / 2))
        self.w.resizable(width=False, height=False)
        self.w.focus_force()
        self.w.title(title)
        # noinspection PyBroadException
        try:
            self.w.iconbitmap(icon)
        except:
            pass
        self.sent = False
        Label(self.w, text="", height=1).pack()

        if type_object == 'basic_settings':
            # Density
            f = Frame(self.w, border=3)
            f.pack()
            Label(f, text=self.lang['SETTINGS_DENSITY'], width=23, anchor=E).pack(side=LEFT)
            self.density = Entry(f, relief=GROOVE, width=24)
            self.density.insert(END, inputs['DENSITY'])
            self.density.pack(side=LEFT, padx=5)
            self.density.focus_force()

            # Max width
            f = Frame(self.w, border=3)
            f.pack()
            Label(f, text=self.lang['SETTINGS_MAX_WIDTH'], width=23, anchor=E).pack(side=LEFT)
            self.maxwidth = Entry(f, relief=GROOVE, width=24)
            self.maxwidth.insert(END, inputs['MAXWIDTH'])
            self.maxwidth.pack(side=LEFT, padx=5)

            # Angle
            f = Frame(self.w, border=3)
            f.pack()
            Label(f, text=self.lang['SETTINGS_ANGLE'], width=23, anchor=E).pack(side=LEFT)
            self.angle = Entry(f, relief=GROOVE, width=24)
            self.angle.insert(END, inputs['ANGLE'])
            self.angle.pack(side=LEFT, padx=5)

            Label(self.w, text="", height=1).pack()
            Button(self.w, text=self.lang['SAVE_SETTINGS'], relief=GROOVE, command=self.send).pack()
            self.w.bind("<Escape>", self.destroy)

    def send(self):
        """
        Send the configs back to the app, then store them.
        :return:
        """
        del_matrix(self.values)
        a = self.density.get().strip()
        b = self.maxwidth.get().strip()
        c = self.angle.get().strip()
        if is_number(a) and is_number(b) and is_number(c):
            self.values.append(a)
            self.values.append(b)
            self.values.append(c)
            self.sent = True
            self.destroy()

    # noinspection PyUnusedLocal
    def destroy(self, e=None):
        """
        Destroy window via event, sends data.

        :param e: Evento
        :return: void
        """
        self.w.destroy()

    def kill(self):
        """
        Destroy the window without sending data.

        :return: void
        """
        self.sent = False
        self.w.destroy()
