#!/usr/bin/env python

PKG_NAME = 'android'


from .. import LOG_LEVEL as PARENT_LOG_LEVEL, PKG_ROOT as PARENT_PKG_ROOT

LOG_LEVEL = PARENT_LOG_LEVEL
# PKG_ROOT = Path(__file__).parent


from pathlib import Path

PKG_ROOT = PARENT_PKG_ROOT/'android'


from .__main__ import main

__all__ = ['main']
