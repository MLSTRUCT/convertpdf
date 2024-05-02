"""
CONVERT PDF

SPECS
Defines spec constructor.
"""

__all__ = [
    'block_cipher',
    'get_analysis',
    'get_bundle',
    'get_collect',
    'get_exe',
    'get_pyz',
    'is_osx',
    'is_win',
    'save_zip'
]

# noinspection PyPep8Naming
from convert import VERSION as ver
from zipfile import ZipFile, ZIP_DEFLATED
import os
import platform
from pathlib import Path

print('Inializing specs')
print(f'Current path: {os.getcwd()}')
print(f'Platform: {platform.system()}')

__actualpath = str(os.path.abspath(os.path.dirname(__file__))).replace('\\', '/')
__actualpath = Path(__actualpath).parent
sep = os.path.sep
is_osx = platform.system() == 'Darwin'
is_win = platform.system() == 'Windows'

# Configure
app_name = 'ConvertPDF'
app_icon = '../resources/appicon.ico'
block_cipher = None

excluded_binaries = []
excluded_binaries_contains = ['api-ms-win-']
excluded_modules = []


def _file_sz(f: str) -> str:
    """
    Computes the file size in KB.
    """
    sz = round(os.path.getsize(f) / 1024, 1)
    return f'{sz} KB'


def _path(p: str, sz: int = 60) -> str:
    """
    Returns a parsed path.
    """
    p = p.replace(sep, '/')
    if len(p) < sz:
        return p
    else:
        return '...' + p[len(p) - sz:len(p)]


def get_analysis(analysis, toc):
    """
    Return the ANALYSIS object.
    """
    # Create datas
    datas = [
        (os.path.join(__actualpath, 'resources\\appicon.ico'), 'resources'),
        (os.path.join(__actualpath, 'resources\\config.json'), 'resources'),
        (os.path.join(__actualpath, 'resources\\convert.png'), 'resources'),
        (os.path.join(__actualpath, 'resources\\lang_en.json'), 'resources'),
        (os.path.join(__actualpath, 'resources\\session.json'), 'resources'),
        (os.path.join(__actualpath, 'resources\\settings.ico'), 'resources'),
    ]

    # Make object
    a = analysis(
        ['../convert.py'],
        binaries=[],
        cipher=block_cipher,
        datas=datas,
        excludes=excluded_modules,
        hiddenimports=['convert'],
        hooksconfig={},
        hookspath=[],
        noarchive=False,
        pathex=['../'],
        runtime_hooks=[],
        win_no_prefer_redirects=False,
        win_private_assemblies=False
    )

    # Update its propeties
    print('Updating binaries')
    new_binaries = []
    for i in a.binaries:
        ex_contains = False
        for j in excluded_binaries_contains:
            if j in i[1]:
                ex_contains = True
                break
        if 'sklearn' in i[0] and i[0] != 'sklearn.__check_build._check_build':
            ex_contains = True
        if ex_contains or i[0] in excluded_binaries:
            print(f'\tRemoved:\t{_path(i[1])} ({_file_sz(i[1])}) <{i[0]}>')
            continue
        new_binaries.append(i)
    print('Program binaries')
    a.binaries = toc(new_binaries)
    for j in a.binaries:
        print(f'\t{j[0]}\n\t\t{_path(j[1])} ({_file_sz(j[1])} KB)')

    # Scripts
    print('Program scripts')
    for j in a.scripts:
        print(f'\t{j[0]}\t{_path(j[1])}')

    # Return the analysis
    return a


def get_bundle(bundle, exe):
    """
    Return a bundle for OSX.
    """
    return bundle(
        exe,
        name=app_name + '.app',
        icon=app_icon,
        bundle_identifier='com.ppizarror',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False
        },
    )


def get_collect(collect, a, exe):
    """
    Return the COLLECT object.
    """
    return collect(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        name=app_name,
        upx_exclude=[],
        upx=True
    )


def get_exe(exe, pyz, a, single: bool):
    """
    Return the EXE object.
    """
    if single:
        return exe(
            pyz,
            a.scripts,
            a.binaries,
            a.zipfiles,
            a.datas,
            [],
            bootloader_ignore_signals=False,
            codesign_identity=None,
            console=False,
            debug=False,
            disable_windowed_traceback=False,
            entitlements_file=None,
            icon=app_icon,
            name=app_name,
            runtime_tmpdir=None,
            strip=False,
            target_arch=None,
            upx_exclude=[],
            upx=True
        )
    else:
        return exe(
            pyz,
            a.scripts,
            [],
            bootloader_ignore_signals=False,
            codesign_identity=None,
            console=True,
            debug=False,
            disable_windowed_traceback=False,
            entitlements_file=None,
            exclude_binaries=True,
            icon=app_icon,
            name=app_name,
            strip=False,
            target_arch=None,
            upx=True
        )


def get_pyz(pyz, a):
    """
    Return the PYZ object.
    """
    return pyz(a.pure, a.zipped_data, cipher=block_cipher)


def save_zip(filename, output, in_folder='dist', out_folder='dist/out_zip'):
    """
    Save a zip file.
    """
    # Removes the old file
    if not os.path.isdir(out_folder):
        os.makedirs(out_folder)
    for k in os.listdir(out_folder):
        if output in k:
            print(f'Removing old zip: {out_folder}/{k}')
            os.remove(f'{out_folder}/{k}')

    filename_full = f'{in_folder}/{filename}'
    output = f'{out_folder}/{output}'
    out_file = f'{output}_v{ver}.zip'
    print(f'Compressing to: {out_file}')
    with ZipFile(out_file, 'w', ZIP_DEFLATED) as zipf:
        if os.path.isdir(filename_full):
            zipdir(filename_full, zipf)
        else:
            zipf.write(filename_full, arcname=filename)


# noinspection PyTypeChecker
def zipdir(path, ziph):
    """
    Zip a folder.
    """
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))
