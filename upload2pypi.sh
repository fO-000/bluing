#!/usr/bin/env bash

sudo ./setup.py clean
sudo ./setup.py check
sudo ./setup.py sdist bdist_wheel
twine upload dist/*
