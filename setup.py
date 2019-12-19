#!/usr/bin/env python3

import os
import shutil
from setuptools.command.install import install
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class MyInstall(install):
    def run(self):
        install.run(self)
        print('[INFO] install bluescan_prompt.bash')
        shutil.copy(
            'src/bluescan/bluescan_prompt.bash', '/etc/bash_completion.d'
        )


if __name__ == "__main__":
    setup(
        name='bluescan',
        version='0.0.3',
        packages=find_packages('src'),
        package_dir={'':'src'},
        entry_points={
            'console_scripts': [
                'bluescan=bluescan.bluescan:main'
            ]
        },
        #scripts=['src/bluescan/bluescan.py'],

        install_requires=[
            'pybluez>=0.22', 'bluepy>=1.3.0', 'docopt>=0.6.2', 'termcolor>=1.1.0'
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
            'install': MyInstall
        }
    )
