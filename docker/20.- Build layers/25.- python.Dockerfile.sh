#!/bin/bash
set -e


# Upgrade system
PACKAGES=()
PACKAGES+=(d2dcn)
PACKAGES+=(wheel)
PACKAGES+=(setuptools)
PACKAGES+=(twine)

# Install all
pip3 install ${PACKAGES[@]}
