#!/usr/bin/env python3

import os
import shutil
from pathlib import Path
from setuptools.command.install import install
from distutils.command.clean import clean
from setuptools import setup, find_packages


BLUESCAN_PATH = os.path.abspath(Path(__file__).parent)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class MyInstall(install):
    def run(self):
        super().run()
        print('[INFO] install bluescan_prompt.bash')
        shutil.copy(
            'src/bluescan/bluescan_prompt.bash', '/etc/bash_completion.d'
        )


class MyClean(clean):
    def run(self):
        super().run()
        dirs = [
            os.path.join(BLUESCAN_PATH, 'build'),
            os.path.join(BLUESCAN_PATH, 'dist'),
            os.path.join(BLUESCAN_PATH, 'src', 'bluescan.egg-info'),
            os.path.join(BLUESCAN_PATH, 'src', 'bluescan', '__pycache__')
        ]

        for d in dirs:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    setup(
        name='bluescan',
        version='0.0.4',
        packages=find_packages('src'),
        package_dir={'':'src'},
        entry_points={
            'console_scripts': [
                'bluescan=bluescan.__main__:main'
            ]
        },
        package_data={

        },
        #scripts=['src/bluescan/bluescan.py'],

        install_requires=[
            'pybluez>=0.22', 'bluepy>=1.3.0', 'docopt>=0.6.2', 
            'termcolor>=1.1.0'
        ],

        # metadata to display on PyPI
        author="fO_000",
        author_email="fO_000@protonmail.com",
        description='A Bluetooth device scanner, support both BR and LE!',
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
