#!/usr/bin/env python3

from bluescan import BlueScanner
import os
from pathlib import Path
import subprocess

class VulnScanner(BlueScanner):
    test_poc = str(Path(os.path.abspath(__file__)).parent/'poc/CVE-2017-0785.py')

    @classmethod
    def scan(cls, addr, addr_type):
        subprocess.run([cls.test_poc, 'TARGET='+addr])
