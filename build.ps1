# simple build script for windows
# build the package and install it locally

# Check if the virtual environment exists
$venv_path = ".\venv\"
if (-Not (Test-Path $venv_path)) {
    Write-Output "### creating virtual environment"
    python -m venv $venv_path
}

# Activate the virtual environment
Write-Output "### activating virtual environment"
. $venv_path\Scripts\Activate

# Check if requirements are installed
$requirements_file = ".\requirements.txt"
if (Test-Path $requirements_file) {
    Write-Output "### checking installed requirements"
    $installed = pip freeze
    $required = Get-Content $requirements_file
    $missing_requirements = $required | Where-Object { $installed -notcontains $_ }

    if ($missing_requirements) {
        Write-Output "### installing missing requirements"
        pip install -r $requirements_file
    }
    else {
        Write-Output "### all requirements satisfied"
    }
}

Write-Output "### building TalkTurbo"
python -m build --no-isolation

Write-Output "uninstalling old versions"
pip uninstall TalkTurbo

Write-Output "### installing build in local enviroment"
$latest_whl = Get-ChildItem -Path .\dist\ -Filter *.whl | Sort-Object LastWriteTime -Descending | Select-Object -First 1
pip install "./dist/$latest_whl"

Write-Output "### all done! happy chatting"