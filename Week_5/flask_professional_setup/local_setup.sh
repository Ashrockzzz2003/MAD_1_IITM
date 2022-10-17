#! /bin/sh

if [ -d ".venv" ];
then
    echo ".venv folder exists. Installing using pip"
else
    echo "creating .venv and install using pip"
    python -m venv .venv
fi

# Activate virtual env
. .venv/Scripts/Activate.ps1

# Upgrade the PIP
pip install --upgrade pip
pip install -r requirements.txt

# Work done. so deactivate the virtual env
deactivate