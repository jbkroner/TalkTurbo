#!/bin/bash

# simple build script for unix, macos

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