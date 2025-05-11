import sys
import os
import glob
import shutil
from setuptools import setup, find_packages, Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize

with open('requirements.txt', 'r') as f:
    requires = [line.rstrip() for line in f.readlines()]


def get_version():
    with open('Tetris/__version__.py') as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])


ext_modules = []
nonpyd_files = []

for entry in glob.glob('Tetris/**/*.py', recursive=True):
    if entry.find('__') == 0:
        nonpyd_files.append(entry)
        continue
    items = entry.split(os.path.sep)
    filename = items[-1]
    mname = '.'.join(filename.split('.')[:-1])
    items[-1] = mname
    name = '.'.join(items)
    ext = Extension(name, [entry])
    ext.build_in_temp = True
    ext.cython_c_in_temp = True
    ext.language_level = 3
    ext_modules.append(ext)


class CopyInitPyAfterBuildExt(build_ext):
    # 执行完标准的cythonize之后 复制__开头的文件
    def run(self):
        super(CopyInitPyAfterBuildExt, self).run()
        if self.inplace:
            return
        target_dir = self.build_lib
        for file in nonpyd_files:
            target = os.path.join(target_dir, file)
            print(f'copy {file} to {target}')
            shutil.copyfile(file, target)


name = 'HyperTexas'
description = ''
version = get_version()
author = 'lirc'
author_email = ''
url = ''


setup(name=name,
      version=version,
      description=description,
      install_requires=requires,
      cmdclass={'build_ext': CopyInitPyAfterBuildExt},
      ext_modules=cythonize(ext_modules, build_dir='build', compiler_directives={'language_level': sys.version_info[0]}),
      entry_points={},
      zip_safe=False,
      platforms='any',
      url=url,
      author=author,
      author_email=author_email)
