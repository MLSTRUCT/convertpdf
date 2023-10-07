"""
CONVERT PDF
Converts a plan from pdf to png, keep transparency.

Requires:
    ghostscript
    imagemagick

Author: Pablo Pizarro R. @ppizarror.com
"""

__all__ = ['App']

import ctypes
import json
import math
import subprocess
import time
import tkinter.messagebox
from tkinter.filedialog import askopenfilename
import traceback
from tkinter import *
from tkinter import font
from resources.utils import Cd, get_local_path
from resources.vframe import VerticalScrolledFrame
from settings import SettingsDialog
from typing import List, Dict, Union, Optional
import shutil
import os

_actualpath = str(os.path.abspath(os.path.dirname(__file__))).replace('\\', '/')

# noinspection PyBroadException
try:
    import winsound

    WSOUND_MODULE = True
except:
    WSOUND_MODULE = False

# Constants
VERSION = '2.2'


# noinspection PyUnusedLocal,PyBroadException,PyTypeChecker
class App(object):
    """
    Main Application
    """
    _settings: Optional['SettingsDialog']

    def __init__(self):
        """
        Constructor.
        """

        def _about() -> None:
            """
            Print about on console.
            """
            self._print(self._lang['ABOUT_APPTITLE'].format(VERSION))
            self._print(self._lang['ABOUT_AUTHOR'] + '\n')

        def _kill() -> None:
            """
            Destroy the application.
            """
            self._root.destroy()
            exit()

        def _scroll_console(event) -> None:
            """
            Scroll console.

            :param event: Event
            """
            if 0 < event.x < 420 and 38 < event.y < 150:
                if os.name == 'nt':  # Windows
                    if -1 * (event.delta / 100) < 0:
                        move = -1
                    else:
                        move = 2
                elif os.name == 'darwin':  # OSX
                    if -1 * event.delta < 0:
                        move = -2
                    else:
                        move = 2
                else:
                    if -1 * (event.delta / 100) < 0:
                        move = -1
                    else:
                        move = 2
                print(len(self._console), move)
                if len(self._console) < 5 and move < 0:
                    return
                self._info_slider.canv.yview_scroll(move, 'units')

        # Configure dpi awareness
        if os.name == 'nt':
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                ctypes.windll.user32.SetProcessDPIAware()

        self._root = Tk()
        self._root.protocol('WM_DELETE_WINDOW', _kill)

        # Load configuration
        with open(os.path.join(_actualpath, 'resources/config.json')) as json_data:
            d = json.load(json_data)
            self._config: Dict[str, Union[str, int, Dict[str, Union[str, int]]]] = d
        self._config['ROOT'] = str(os.path.abspath(os.path.dirname(__file__))).replace(
            '\\', '/') + '/'
        with open(os.path.join(_actualpath, self._config['LANG']), encoding='utf8') as json_data:
            d = json.load(json_data)
            self._lang = d

        # Conversion settings
        self._conversion = {
            'MAXWIDTH': 9600,
            'ANGLE': 0
        }

        # Window properties
        size = [self._config['APP']['WIDTH'], self._config['APP']['HEIGHT']]
        self._root.minsize(width=size[0], height=size[1])
        self._root.geometry('%dx%d+%d+%d' % (
            size[0], size[1], (self._root.winfo_screenwidth() - size[0]) / 2,
            (self._root.winfo_screenheight() - size[1]) / 2))
        self._root.resizable(width=False, height=False)
        self._root.focus_force()

        # Window style
        self._root.title(self._config['APP']['TITLE'].format(VERSION))
        self._root.iconbitmap(os.path.join(_actualpath, self._config['APP']['ICON']['TITLE']))

        f1 = Frame(self._root, border=5)
        f1.pack(fill=X)
        f2 = Frame(self._root)
        f2.pack(fill=BOTH)

        # Load file
        self._loadbutton = Button(f1, text=self._lang['LOAD_FILE_BUTTON'], state='normal', relief=GROOVE,
                                  command=self.load_file, cursor='hand2')
        self._loadbutton.pack(side=LEFT, padx=5, anchor=W)

        # Label that shows loaded configuration name
        self._mainlabelstr = StringVar()
        self._mainlabel = Label(f1, textvariable=self._mainlabelstr, foreground='#555', width=35, anchor='w')
        self._mainlabel.pack(side=LEFT, padx=3)

        # Convert
        upimg = PhotoImage(file=os.path.join(_actualpath, self._config['APP']['ICON']['UPLOADBUTTON']))
        self._convertbutton = Button(f1, image=upimg, relief=GROOVE, height=20,
                                     width=20, border=0, state='disabled', command=self.upload)
        self._convertbutton.image = upimg
        self._convertbutton.pack(side=RIGHT, padx=(5, 2), anchor=E)

        # Request configs
        self._configurebutton = Button(f1, text=self._lang['SETTINGS'], relief=GROOVE, command=self.request_settings)
        self._configurebutton.pack(side=RIGHT, padx=5, anchor=E)

        # Console
        self._info_slider = VerticalScrolledFrame(f2)
        self._info_slider.canv.config(bg='#000000')
        self._info_slider.pack(pady=2, anchor=NE, fill=BOTH, padx=1)
        self._info = Label(self._info_slider.interior, text='', justify=LEFT, anchor=NW,
                           bg='black', fg='white', wraplength=self._config['APP']['WIDTH'],
                           font=font.Font(family='Courier', size=9), relief=FLAT, border=2, cursor='arrow')
        self._info.pack(anchor=NW, fill=BOTH)
        self._console = []
        self._cnextnl = False
        self._settings = None  # Opened
        _about()

        # Other variables
        with open(os.path.join(_actualpath, self._config['LAST_SESSION_FILE'])) as json_data:
            lsession = json.load(json_data)
        if lsession['LAST_FOLDER'] != '':
            self._lastfolder = lsession['LAST_FOLDER']
        else:
            self._lastfolder = self._config['ROOT']
        self._loadedfile = {}
        self._lastloadedfile = ''
        self._clearstatus()

        # Events
        self._root.bind('<MouseWheel>', _scroll_console)

    def _clearstatus(self) -> None:
        """
        Clear a loaded status.
        """
        self._convertbutton.configure(state='disabled', cursor='arrow')
        self._mainlabelstr.set('')
        self._loadedfile = {}
        self._generationok = False
        self._lastloadedfile = ''

    def _clearconsole(self, scrolldir: int = 1) -> None:
        """
        Clear the console.

        :param scrolldir: Scroll direction
        """

        # noinspection PyShadowingNames,PyUnusedLocal
        def _slide(*args) -> None:
            """
            Move scroll.
            """
            self._info_slider.canv.yview_scroll(1000 * scrolldir, 'units')

        self._console = []
        self._info.config(text='')
        self._root.after(10, _slide)

    def _errorsound(self) -> None:
        """
        Create an error sound.
        """
        if self._config['APP']['SOUNDS'] and WSOUND_MODULE:
            winsound.MessageBeep(1)

    def load_file(self) -> None:
        """
        Load a file pdf to convert to png.
        """
        if not self._check_settings_closed:
            return
        self._print(self._lang['LOAD_WAITING_USER'], end='', hour=True)
        if self._config['REMEMBER_LAST_FOLDER'] and self._lastfolder != '':
            filename = askopenfilename(
                title=self._lang['LOAD_FILE_PICKWINDOW_TITLE'],
                filetypes=[(self._lang['LOAD_FILE_PDF'], '.pdf')],
                initialdir=self._lastfolder)
        else:
            filename = askopenfilename(
                title=self._lang['LOAD_FILE_PICKWINDOW_TITLE'],
                filetypes=[(self._lang['LOAD_FILE_PDF'], '.pdf')])

        # Check if the filename is not empty
        if filename == '' or 'pdf' not in filename.lower():
            self._print(self._lang['LOAD_CANCELLED'] if filename == '' else self._lang['LOAD_FAILED'])
            self._clearstatus()
            return
        else:
            self._print(self._lang['PROCESS_OK'])

        # Store last folder
        filepath = os.path.split(filename)
        self._lastfolder = filepath[0]
        self._lastloadedfile = filepath[1]

        # Validate file
        self._print(self._lang['START_LOADING'].format(filename), hour=True, end='')
        self._print(self._lang['LOAD_OK'])
        self._convertbutton.configure(state='normal', cursor='hand2')
        if self._config['AUTO_START']:
            self._root.after(50, self.request_settings)

    def _print(self, msg: str, hour: bool = False, end: bool = None, scrolldir: int = 1) -> None:
        """
        Print a message on console.

        :param msg: Message
        :param hour: Hour
        :param scrolldir: Scroll direction
        """

        def _consoled(c: List[str]) -> str:
            """
            Generates string with hour of message.
            :param c: List
            :return: Text
            """
            text = ''
            for i in c:
                text = text + i + '\n'
            return text

        def _get_hour() -> str:
            """
            Return system hour.

            :return: String
            """
            return time.ctime(time.time())[11:19]

        def _slide(*args) -> None:
            """
            Scroll the console.
            """
            self._info_slider.canv.yview_scroll(2000 * scrolldir, 'units')

        try:
            msg = str(msg)
            if hour:
                msg = self._config['CONSOLE']['MSG_FORMAT'].format(_get_hour(), msg)
            if len(self._console) == 0 or self._console[len(self._console) - 1] != msg:
                if self._cnextnl:
                    self._console[len(self._console) - 1] += msg
                else:
                    self._console.append(msg)
                if end == '':
                    self._cnextnl = True
                else:
                    self._cnextnl = False

            if len(self._console) > self._config['CONSOLE']['LIMIT_MESSAGES_CONSOLE']:
                self._console.pop()
            print(msg, end=end)

            self._info.config(text=_consoled(self._console))
            self._root.after(100, _slide)
        except:
            self._clearconsole()

    def request_settings(self) -> None:
        """
        Request settings of conversion.
        """
        if self._settings is not None:
            return self._settings.focus()
        self._print(self._lang['REQUESTING_SETTINGS'], end='', hour=True)
        self._settings = SettingsDialog(
            [self._lang, os.path.join(_actualpath, 'resources/settings.ico'), 'basic_settings', [420, 165],
             self._conversion])
        self._settings.w.mainloop(1)
        if self._settings.sent:
            self._print(self._lang['PROCESS_OK'], hour=True)
            self._conversion['MAXWIDTH'] = int(self._settings.values[0])
            # noinspection PyTypeChecker,PyTypedDict
            self._conversion['ANGLE'] = float(self._settings.values[1])
        else:
            self._print(self._lang['PROCESS_CANCEL'], hour=True)
        self._settings = None

    def run(self) -> None:
        """
        Run the app.
        """
        self._root.mainloop()

    def save_last_session(self) -> None:
        """
        Save last opened folder to file.
        """
        if self._config['SAVE_LAST_SESSION']:
            with open(os.path.join(_actualpath, self._config['LAST_SESSION_FILE']), 'w') as outfile:
                session = {
                    'LAST_FOLDER': self._lastfolder,
                    'LAST_LOADED_FILE': self._lastloadedfile
                }
                json.dump(session, outfile)

    @property
    def _check_settings_closed(self) -> bool:
        """
        Check if the settings window is closed.

        :returns: True if closed
        """
        if self._settings is not None:
            tkinter.messagebox.showerror(self._lang['ERROR'], self._lang['ERROR_CLOSE_SETTINGS'])
            self._settings.focus()
            return False
        return True

    def upload(self) -> None:
        """
        Convert the image.
        """
        if not self._check_settings_closed:
            return

        def _callback():
            try:
                t = time.time()
                with open(os.devnull, 'w') as FNULL:
                    with Cd(self._lastfolder):
                        current_image = os.path.join(get_local_path(), '__convert__.png')  # Remove if exist
                        if os.path.isfile(current_image):
                            os.remove(current_image)

                        # Final name of the conversion
                        final_image = self._lastloadedfile.split('.')
                        final_image.pop()
                        final_image.append('png')
                        final_image = '.'.join(final_image)
                        if os.path.isfile(final_image):
                            raise ValueError(self._lang['CONVERSION_ALREADY_EXISTS'].format(final_image))

                        # First, retrieve the pdf size
                        wh = subprocess.check_output(['magick', 'identify', '-verbose', self._lastloadedfile]).decode('utf-8')
                        wh = wh.split('Print size: ')
                        if len(wh) != 2:
                            raise ValueError('Invalid PDF. Print size not allowed')
                        wh = wh[1].split('\n')[0].strip().split('x')  # Format wxh
                        if len(wh) != 2:
                            raise ValueError('Invalid print size. Requires format wxh')
                        density = math.ceil(abs(self._conversion['MAXWIDTH'] / max(float(wh[0]), float(wh[1]))))

                        # Convert from pdf to png
                        self._print(self._lang['CONVERSION_CONV'].format(density), hour=True)
                        subprocess.call(['magick', '-density', str(density),
                                         self._lastloadedfile, current_image], shell=True)

                        # Apply angle
                        angle = self._conversion['ANGLE']
                        if angle != 0:
                            self._print(self._lang['CONVERSION_ANGLE'].format(angle), hour=True)
                            rotated_image = os.path.join(get_local_path(), '__2convert__.png')
                            subprocess.call(['magick', current_image, '-rotate', angle, rotated_image], shell=True)
                            os.remove(current_image)
                            current_image = rotated_image

                        # Rename image
                        if os.path.isfile(final_image):
                            os.remove(final_image)
                        shutil.move(current_image, final_image)
                        self._print(self._lang['CONVERSION_FINISHED'], hour=True)

                self.save_last_session()
                self._clearstatus()
            except Exception as e:
                self._errorsound()
                self._print(traceback.format_exc())

            self._loadbutton.configure(state='active', cursor='arrow')
            self._root.configure(cursor='arrow')

        self._root.configure(cursor='wait')
        self._convertbutton.configure(state='disabled', cursor='arrow')
        self._loadbutton.configure(state='disabled', cursor='arrow')
        self._print(self._lang['PROCESS_STARTED'], hour=True)
        self._root.after(500, _callback)


if __name__ == '__main__':
    App().run()
