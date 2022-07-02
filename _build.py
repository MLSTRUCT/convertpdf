"""
CONVERT PDF

BUILD
"""

import os
import struct
import sys

assert len(sys.argv) == 2, 'Argument is required, usage: build.py pyinstaller'
mode = sys.argv[1].strip()
python = 'python3' if not sys.platform == 'win32' else 'python'
sys_arch = struct.calcsize('P') * 8

if mode == 'pyinstaller':
    # Check upx
    upx = ''
    if sys.platform == 'win32' and sys_arch == 64:
        upx = '--upx-dir specs/upx_64'
    pyinstaller = f'{python} -m PyInstaller' if sys.platform == 'win32' else 'pyinstaller'

    os.system(f'{pyinstaller} specs/ConvertPDF.spec --noconfirm {upx}')
