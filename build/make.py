from subprocess import run
from glob import glob
from os import walk, path, sep as pathsep
from shutil import copy, move
import pkg_resources as pr
import zipfile as zf
import re

VERSION = pr.get_distribution('docal').version
NAME = 'docal'
DIR = 'docal_tkinter.dist'
ASSETS_DIR = path.join(DIR, 'assets')
ICON = '../docal.ico'

def build():
    args = ['python', '-m', 'nuitka',
            '--standalone',
            '--plugin-enable=tk-inter',
            '--windows-icon=../docal.ico',
            '--windows-disable-console',
            # '--windows-dependency-tool=pefile',
            '../docal_tkinter']
    if run(args).returncode == 0:
        move(path.join(DIR, 'docal_tkinter.exe'), path.join(DIR, NAME + '.exe'))
        copy(ICON, path.join(DIR, path.basename(ICON)))

def create_installer():
    '''update the version and the files in the installer'''

    installer_name = 'installer-script.nsi'
    file_commands = []
    dir_commands = []
    file_list = glob(path.join(DIR, '**', '*'), recursive=True)
    for p in file_list:
        inst_path = f'$INSTDIR{p[len(DIR):]}'
        if path.isdir(p):
            dir_commands.append(f'  RMDir "{inst_path}"')
        else:
            file_commands.append(f'  Delete "{inst_path}"')
    # this will ensure that deletion will start from the inner most folder
    dir_commands.sort(key=lambda x: x.count(pathsep), reverse=True)
    # with the installer script
    file = path.relpath(installer_name)
    with open(file, encoding='utf-8') as nsi:
        old = nsi.read()
    # Update the version
    new = re.sub(r'(?<=!define DOCAL_VERSION ")[\d.]*?(?=")', VERSION, old)
    commands = '\n'.join(file_commands + dir_commands).replace('\\', r'\\')
    new = re.sub(r'(?ms)(?<=<INSTALLEDFILES>\n).*?(?= *; </INSTALLEDFILES>)', commands, new)
    with open(file, 'w', encoding='utf-8') as nsi:
        nsi.write(new)
    run(['D:\\DevPrograms\\NSIS\\makensis.exe', installer_name])


def build_zip():
    file_paths = []
    for root, dirs, files in walk(DIR):
        file_paths += [path.join(root, f) for f in files]

    with zf.ZipFile(f'{NAME}-{VERSION}-portable.zip', 'w', compression=zf.ZIP_DEFLATED) as package:
        for file in file_paths:
            package.write(file, file.replace(DIR, NAME))

# TASKS:
# -----------
# build()
# copy_assets()
build_zip()
# create_installer()
