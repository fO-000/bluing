#!/usr/bin/env bash

sudo -E env "PATH=$PATH" ./setup.py clean
sudo -E env "PATH=$PATH" ./setup.py check
sudo -E env "PATH=$PATH" ./setup.py sdist bdist_wheel
twine upload dist/*
