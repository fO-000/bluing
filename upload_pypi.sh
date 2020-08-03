#!/usr/bin/env bash

./setup.py clean
./setup.py check
./setup.py sdist bdist_wheel
twine upload dist/*
