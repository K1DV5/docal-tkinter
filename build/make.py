from subprocess import run
from glob import glob
from os import walk, path, sep as pathsep, makedirs
from shutil import copy, move, rmtree, make_archive
import pkg_resources
import zipfile as zf
import re
from pkg_resources import resource_filename

VERSION = pkg_resources.get_distribution('docal').version
NAME = 'docal'
DIR = 'docal_tkinter.dist'
INSTALLER_TEMPLATE = 'installer-script.nsi'
ASSETS_DIR = path.join(DIR, 'assets')
ICON = '../docal.ico'

# template file for word
WORD_TEMPL = resource_filename('docal', 'handlers/template.docx')

def build():
    args = ['python', '-m', 'nuitka',
            '--standalone',
            '--plugin-enable=tk-inter',
            '--windows-icon=' + path.abspath(ICON),
            '--windows-disable-console',
            # '--experimental=use_pefile',
            # '--experimental=use_pefile_recurse',
            '--windows-dependency-tool=pefile',
            '--recurse-all',
            '../docal_tkinter']
    # args = [
    #     'pyinstaller',
    #     '../docal_tkinter',
    #     '-n', NAME,
    #     '--windowed',
    #     '--icon', ICON
    # ]
    if run(args).returncode != 0:
        print('error')
        exit(1)
    move(path.join(DIR, 'docal_tkinter.exe'), path.join(DIR, NAME + '.exe'))
    copy(ICON, path.join(DIR, path.basename(ICON)))
    template_dir = path.join(DIR, 'docal', 'handlers')
    print(makedirs(template_dir))
    copy(WORD_TEMPL, path.join(template_dir, path.basename(WORD_TEMPL)))
    # unnecessary regional things
    rmtree(path.join(DIR, 'tcl', 'encoding'))
    rmtree(path.join(DIR, 'tcl', 'http1.0'))
    rmtree(path.join(DIR, 'tcl', 'tzdata'))
    rmtree(path.join(DIR, 'tcl', 'opt0.4'))
    rmtree(path.join(DIR, 'tcl', 'msgs'))
    rmtree(path.join(DIR, 'tk', 'msgs'))
    rmtree(path.join(DIR, 'tk', 'images'))
    print('Compiled')

def create_installer():
    '''update the version and the files in the installer'''

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
    file = path.relpath(INSTALLER_TEMPLATE)
    with open(file, encoding='utf-8') as nsi:
        template = nsi.read()
    # Update the version
    installer = template.replace('$[VERSION]', VERSION).replace('$[DIR]', DIR)
    commands = '\n'.join(file_commands + dir_commands)
    installer = installer.replace('$[UNINSTALL_DELETES]', commands)
    installer_file = 'installer.nsi'
    with open(installer_file, 'w', encoding='utf-8') as nsi:
        nsi.write(installer)
    run(['D:\\DevPrograms\\NSIS\\makensis.exe', installer_file])
    print('Installer built')


def build_zip():
    file_paths = []
    for root, dirs, files in walk(DIR):
        file_paths += [path.join(root, f) for f in files]

    # make_archive(path.abspath(f'{NAME}-{VERSION}-portable'), 'zip', DIR, DIR)
    with zf.ZipFile(f'{NAME}-{VERSION}-portable.zip', 'w', compression=zf.ZIP_DEFLATED) as package:
        for file in file_paths:
            package.write(file, file.replace(DIR, NAME))
    print('Portable archive built')

# TASKS:
# -----------
build()
build_zip()
create_installer()
