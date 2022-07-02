"""
CONVERT PDF
Converts a plan from pdf to png, keep transparency.

Requires:
    ghostscript
    imagemagick

Author: Pablo Pizarro R. @ ppizarror.com
"""

# Library imports
import json
import subprocess
import time
from tkinter.filedialog import askopenfilename
import traceback
from tkinter import *
from tkinter import font
from resources.utils import *
from resources.vframe import VerticalScrolledFrame
from settings import SettingsDialog
import os

_actualpath = str(os.path.abspath(os.path.dirname(__file__))).replace('\\', '/')

# noinspection PyBroadException
try:
    import winsound

    WSOUND_MODULE = True
except:
    WSOUND_MODULE = False

# Constants
VERSION = '2.0.0'


# noinspection PyUnusedLocal,PyBroadException,PyTypeChecker
class App(object):
    """
    Main Application
    """

    def __init__(self):
        """
        Constructor.
        """

        def _about():
            """
            Print about on console.
            :return:
            """
            self._print(self._lang['ABOUT_APPTITLE'].format(VERSION))
            self._print(self._lang['ABOUT_AUTHOR'] + '\n')

        def _kill():
            """
            Destroy the application.
            :return:
            """
            self._root.destroy()
            exit()

        def _scroll_console(event):
            """
            Scroll console.
            :param event: Event
            :return: None
            """
            if 0 < event.x < 420 and 38 < event.y < 150:
                if is_windows():
                    if -1 * (event.delta / 100) < 0:
                        move = -1
                    else:
                        move = 2
                elif is_osx():
                    if -1 * event.delta < 0:
                        move = -2
                    else:
                        move = 2
                else:
                    if -1 * (event.delta / 100) < 0:
                        move = -1
                    else:
                        move = 2
                if len(self._console) < 5 and move < 0:
                    return
                self._info_slider.canv.yview_scroll(move, 'units')

        self._root = Tk()
        self._root.protocol('WM_DELETE_WINDOW', _kill)
        self._root.tk.call('tk', 'scaling', 1.35)

        # Load configuration
        with open(os.path.join(_actualpath, 'resources/config.json')) as json_data:
            d = json.load(json_data)
            self._config = d
        self._config['ROOT'] = str(os.path.abspath(os.path.dirname(__file__))).replace(
            '\\', '/') + '/'
        with open(os.path.join(_actualpath, self._config['LANG']), encoding='utf8') as json_data:
            d = json.load(json_data)
            self._lang = d

        # Conversion settings
        self._conversion = {
            'DENSITY': 1300,
            'MAXWIDTH': 9600,
            'ANGLE': -90
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
        self._root.title(self._config['APP']['TITLE'])
        self._root.iconbitmap(os.path.join(_actualpath, self._config['APP']['ICON']['TITLE']))
        fonts = [font.Font(family='Courier', size=8),
                 font.Font(family='Verdana', size=6),
                 font.Font(family='Times', size=10),
                 font.Font(family='Times', size=10, weight=font.BOLD),
                 font.Font(family='Verdana', size=6, weight=font.BOLD),
                 font.Font(family='Verdana', size=10),
                 font.Font(family='Verdana', size=7)]

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
        self._mainlabel = Label(f1, textvariable=self._mainlabelstr, foreground='#555', width=35,
                                anchor='w')
        self._mainlabel.pack(side=LEFT, padx=3)

        # Convert
        upimg = PhotoImage(file=os.path.join(_actualpath, self._config['APP']['ICON']['UPLOADBUTTON']))
        self._convertbutton = Button(f1, image=upimg, relief=GROOVE, height=20,
                                     width=20, border=0, state='disabled', command=self.upload)
        self._convertbutton.image = upimg
        self._convertbutton.pack(side=RIGHT, padx=2, anchor=E)

        # Request configs
        self._configurebutton = Button(f1, text=self._lang['SETTINGS'],
                                       state='disabled', relief=GROOVE,
                                       command=self.request_settings)
        self._configurebutton.pack(side=RIGHT, padx=5, anchor=E)

        # Console
        self._info_slider = VerticalScrolledFrame(f2)
        self._info_slider.canv.config(bg='#000000')
        self._info_slider.pack(pady=2, anchor=NE, fill=BOTH, padx=1)
        self._info = Label(self._info_slider.interior, text='', justify=LEFT, anchor=NW,
                           bg='black', fg='white',
                           wraplength=self._config['APP']['WIDTH'],
                           font=fonts[0], relief=FLAT, border=2,
                           cursor='arrow')
        self._info.pack(anchor=NW, fill=BOTH)
        self._info_slider.scroller.pack_forget()
        self._console = []
        self._cnextnl = False
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

    def _clearstatus(self):
        """
        Clear a loaded status.
        :return: None
        """
        self._convertbutton.configure(state='disabled', cursor='arrow')
        self._configurebutton.configure(state='disabled', cursor='arrow')
        self._mainlabelstr.set('')
        self._loadedfile = {}
        self._generationok = False
        self._lastloadedfile = ''

    def _clearconsole(self, scrolldir=1):
        """
        Clear the console.
        :param scrolldir: Scroll direction
        :return:
        """

        # noinspection PyShadowingNames,PyUnusedLocal
        def _slide(*args):
            """
            Move scroll.
            :return: None
            """
            self._info_slider.canv.yview_scroll(1000 * scrolldir, 'units')

        self._console = []
        self._info.config(text='')
        self._root.after(10, _slide)

    def _errorsound(self):
        """
        Create an error sound.
        :return: None
        """
        if self._config['APP']['SOUNDS'] and WSOUND_MODULE:
            winsound.MessageBeep(1)

    def load_file(self):
        """
        Load a file pdf to convert to png.
        :return: None
        """
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

        # Check if filename is not empty
        if filename == '':
            self._print(self._lang['LOAD_CANCELLED'])
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
        self._configurebutton.configure(state='normal', cursor='hand2')
        if self._config['AUTO_START']:
            self._root.after(50, self.request_settings)

    def _print(self, msg, hour=False, end=None, scrolldir=1):
        """
        Print a message on console.
        :param msg: Message
        :param hour: Hour
        :param scrolldir: Scroll direction
        :return: None
        """

        def _consoled(c):
            """
            Generates string with hour of message.
            :param c: List
            :return: Text
            """
            text = ''
            for i in c:
                text = text + i + '\n'
            return text

        def _get_hour():
            """
            Return system hour.
            :return: String
            """
            return time.ctime(time.time())[11:19]

        def _slide(*args):
            """
            Scroll the console.
            :return: None
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
            self._root.after(50, _slide)
        except:
            self._clearconsole()

    def request_settings(self):
        """
        Request settings of conversion.
        :return:
        """
        self._print(self._lang['REQUESTING_SETTINGS'], end='', hour=True)
        settings = SettingsDialog(
            [self._lang, os.path.join(_actualpath, 'resources/settings.ico'), 'basic_settings', [315, 160],
             self._conversion])
        settings.w.mainloop(1)
        if settings.sent:
            self._print(self._lang['PROCESS_OK'], hour=True)
            self._conversion['DENSITY'] = int(settings.values[0])
            self._conversion['MAXWIDTH'] = int(settings.values[1])
            # noinspection PyTypeChecker,PyTypedDict
            self._conversion['ANGLE'] = float(settings.values[2])
        else:
            self._print(self._lang['PROCESS_CANCEL'], hour=True)

    def run(self):
        """
        Run the app.
        :return: None
        """
        self._root.mainloop()

    def save_last_session(self):
        """
        Save last opened folder to file.
        :return:
        """
        if self._config['SAVE_LAST_SESSION']:
            with open(os.path.join(_actualpath, self._config['LAST_SESSION_FILE']), 'w') as outfile:
                session = {
                    'LAST_FOLDER': self._lastfolder,
                    'LAST_LOADED_FILE': self._lastloadedfile
                }
                json.dump(session, outfile)

    def upload(self):
        """
        Convert the image.
        :return:
        """

        def _callback():
            try:
                t = time.time()
                with open(os.devnull, 'w') as FNULL:
                    with Cd(self._lastfolder):

                        current_image = '__convert__.png'  # Remove if exist
                        if os.path.isfile(current_image):
                            os.remove(current_image)
                        final_image = self._lastloadedfile.split('.')
                        final_image.pop()
                        final_image.append('png')
                        final_image = '.'.join(final_image)

                        # Convert from pdf to png
                        self._print(self._lang['CONVERSION_CONV'].format(self._conversion['DENSITY']), hour=True)
                        time.sleep(0.5)
                        subprocess.call(['magick', '-density', str(self._conversion['DENSITY']), self._lastloadedfile,
                                         '__convert__.png'], shell=True)

                        if self._conversion['ANGLE'] != 0:
                            self._print(self._lang['CONVERSION_ANGLE'].format(self._conversion['ANGLE']), hour=True)
                            subprocess.call(
                                ['magick', current_image, '-rotate', '{0}'.format(self._conversion['ANGLE']),
                                 '__2convert__.png'], shell=True)
                            os.remove(current_image)
                            current_image = '__2convert__.png'

                        # Check width/height and calculate factor
                        self._print(self._lang['CONVERSION_WIDTH'], hour=True)
                        wh = subprocess.check_output(['magick', 'identify', '-format', '%w %h', current_image])
                        wh = wh.decode('utf-8')
                        width = int(wh.split(' ')[0])
                        height = int(wh.split(' ')[1])

                        # Get the maximum factor
                        max_factor = max(1.0 * width / self._conversion['MAXWIDTH'],
                                         1.0 * height / self._conversion['MAXWIDTH'])
                        if max_factor > 1:
                            resizefactor = 100.0 / max_factor
                            self._print(self._lang['CONVERSION_RESIZE'].format(round(resizefactor, 2)), hour=True)
                            time.sleep(0.5)
                            subprocess.call(
                                ['magick', current_image, '-resize', '{0}%'.format(resizefactor), '-filter', 'Point',
                                 '__3convert__.png'], shell=True)
                            os.remove(current_image)
                            current_image = '__3convert__.png'

                        # Rename image
                        if os.path.isfile(final_image):
                            os.remove(final_image)  # Remove last instance of image

                        os.rename(current_image, final_image)
                        self._print(self._lang['CONVERSION_FINISHED'], hour=True)

                self.save_last_session()
                self._clearstatus()
                self._loadbutton.configure(state='active', cursor='arrow')
                self._root.configure(cursor='arrow')
            except Exception as e:
                self._root.configure(cursor='arrow')
                self._errorsound()
                self._print(self._lang['PROCESS_ERROR'])
                self._print(str(e))
                self._print(traceback.format_exc())

        self._root.configure(cursor='wait')
        self._convertbutton.configure(state='disabled', cursor='arrow')
        self._loadbutton.configure(state='disabled', cursor='arrow')
        self._print(self._lang['PROCESS_STARTED'], hour=True)
        self._root.after(500, _callback)


if __name__ == '__main__':
    App().run()
