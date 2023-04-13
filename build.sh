#!/bin/bash

# simple build script for unix, macos

# create a venv if one does not exist, otherwise activate venv
VENV_NAME="venv"
if [ ! -d "$VENV_NAME" ]; then
    echo "### creating virtual environment"
    python -m venv "$VENV_NAME"
fi

echo "### activating virtual environment"
source "$VENV_NAME/bin/activate"

# install requirements in the venv
echo "### installing requirements"
pip install -r requirements.txt

echo "### building TalkTurbo"
python -m build

echo "uninstalling old versions"
pip uninstall TalkTurbo

echo "#### make ./dist/ if it does not exist"
mkdir dist

echo "### installing build in local environment"
whl_files=("./dist/"*.whl)
if [ ${#whl_files[@]} -eq 0 ]; then
    echo "No wheel files found in ./dist directory!"
else
    latest_whl=$(ls -t ./dist/*.whl | head -n1)
    pip install "$latest_whl"
fi

echo "### all done! happy chatting"