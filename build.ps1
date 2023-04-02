# simple build script for windows
# build the package and install it locally

Write-Output "### building TalkTurbo"
python -m build

Write-Output "uninstalling old versions"
pip uninstall TalkTurbo

Write-Output "### installing build in local enviroment"
$latest_whl = Get-ChildItem -Path .\dist\ -Filter *.whl | Sort-Object LastWriteTime -Descending | Select-Object -First 1
pip install "./dist/$latest_whl"

Write-Output "### all done! happy chatting"