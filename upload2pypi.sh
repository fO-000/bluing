#!/usr/bin/env zsh

sudo -E env "PATH=$PATH" ./setup.py clean
sudo -E env "PATH=$PATH" ./setup.py check
sudo -E env "PATH=$PATH" ./setup.py sdist bdist_wheel

if [[ $1 == '--test' ]]; then
    twine upload --repository testpypi dist/*
elif [[ -z $1 ]]; then
    twine upload dist/*
else
    echo 'Unknown option' $1
fi
