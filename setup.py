#!/usr/bin/env python3

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


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class MyInstall(install):
    def run(self):
        super().run()
        logger.info('install bluescan_prompt.bash')
        shutil.copy(
            'src/bluescan/bluescan_prompt.bash', '/etc/bash_completion.d'
        )


class MyClean(clean):
    def run(self):
        super().run()
        dirs = [
            os.path.join(PROJECT_ROOT, 'build', 'bdist.linux-x86_64'), # 不直接删除 build 目录，因为 yotta 也会使用该目录。
            os.path.join(PROJECT_ROOT, 'build', 'lib'),
            os.path.join(PROJECT_ROOT, 'dist'),
            os.path.join(PROJECT_ROOT, 'src', 'bluescan.egg-info'),
            os.path.join(PROJECT_ROOT, 'src', 'bluescan', '__pycache__')
        ]

        for d in dirs:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    setup(
        name='bluescan',
        version='0.5.0',
        license = "GPL-3.0",
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
            'btsmp>=0.0.2', 'bthci>=0.0.19', 'pyclui>=0.0.7', 'scapy>=2.4.4', 
            'docopt>=0.6.2', 'pybluez>=0.23', 'bluepy>=1.3.0', 'pyserial>=3.5'
        ],

        # metadata to display on PyPI
        author="fO_000",
        author_email="fO_000@protonmail.com",
        description='A powerful Bluetooth scanner',
        long_description=read('README.md'),
        long_description_content_type='text/markdown',
        url='https://github.com/fO-000/bluescan',
        # project_urls={
        #     "Bug Tracker": "None",
        #     "Documentation": "None",
        #     "Source Code": "None",
        # },

        cmdclass={
            'install': MyInstall,
            'clean': MyClean
        }
    )
