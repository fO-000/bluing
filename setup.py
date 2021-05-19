#!/usr/bin/env python3

import sys
import os
import shutil
import logging
from pathlib import Path
from setuptools.command.install import install
from distutils.command.clean import clean
from setuptools import setup, find_packages

from pyclui import Logger

logger = Logger(__name__, logging.INFO)

PROJECT_ROOT = os.path.abspath(Path(__file__).parent)
PROJECT_NAME = 'bluescan'

sys.path.insert(0, PROJECT_ROOT+'/src')
from bluescan import VERSION


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class MyInstall(install):
    def run(self):
        super().run()
        # logger.info('install bluescan_prompt.bash')
        # shutil.copy(
        #     'src/bluescan/bluescan_prompt.bash', '/etc/bash_completion.d'
        # )


class MyClean(clean):
    def run(self):
        super().run()
        dirs = [
            os.path.join(PROJECT_ROOT, 'build', 'bdist.linux-x86_64'), # 不直接删除 build 目录，因为 yotta 也会使用该目录。
            os.path.join(PROJECT_ROOT, 'build', 'lib'),
            os.path.join(PROJECT_ROOT, 'dist'),
            os.path.join(PROJECT_ROOT, 'src', PROJECT_NAME+'.egg-info'),
            os.path.join(PROJECT_ROOT, 'src', PROJECT_NAME, '__pycache__')
        ]

        for d in dirs:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    setup(
        name=PROJECT_NAME,
        version=VERSION,
        license="GPLv3+",
        packages=find_packages('src'), # include all packages under src
        package_dir={'':'src'}, # tell distutils packages are under src
        entry_points={
            'console_scripts': [
                'bluescan=bluescan.__main__:main'
            ]
        },
        package_data={
            "bluescan": ["res/*.txt"]
        },
        #scripts=['src/bluescan/bluescan.py'],

        install_requires=[
            'bthci>=0.0.19', 'btatt>=0.0.2', 'btgatt>=0.0.2', 'btsmp>=0.0.2', 
            'pyclui>=0.0.8', 'scapy>=2.4.5', 'docopt>=0.6.2', 'pybluez>=0.23', 
            'bluepy>=1.3.0', 'pyserial>=3.5', 'dbus-python>=1.2.16', 'PyGObject>=3.40.1',
        ],
        python_requires='>=3.9',

        # metadata to display on PyPI
        author="fO_000",
        author_email="fO_000@protonmail.com",
        description='A powerful Bluetooth scanner',
        long_description=read('README.md'),
        long_description_content_type='text/markdown',
        url='https://github.com/fO-000/'+PROJECT_NAME,
        # project_urls={
        #     "Bug Tracker": "None",
        #     "Documentation": "None",
        #     "Source Code": "None",
        # },

        cmdclass={
            'install': MyInstall,
            'clean': MyClean
        },

        classifiers=[
            'Environment :: Console',
            "Intended Audience :: Developers",
            "Intended Audience :: Information Technology",
            "Intended Audience :: Science/Research",
            "Intended Audience :: System Administrators",
            "Intended Audience :: Telecommunications Industry",
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Programming Language :: Python :: 3.9',
            'Topic :: Security',
            'Topic :: System :: Networking',
        ]
    )
