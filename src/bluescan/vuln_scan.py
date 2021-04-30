#!/usr/bin/env python3

from . import BlueScanner
import os
from pathlib import Path
import subprocess


class VulnScanner(BlueScanner):
    test_poc = str(Path(os.path.abspath(__file__)).parent/'poc/CVE-2017-0785/CVE-2017-0785.py')
    
    def __init__(self, iface):
        super().__init__(iface=iface)
        self.load_poc_paths()

    def scan(self, addr, addr_type):
        subprocess.run([self.test_poc, 'BD_ADDR='+addr])

        for poc_path in self.poc_paths:
            subprocess.run([poc_path, 'BD_ADDR='+addr])

    def load_poc_paths(self):
        self.poc_paths = []
