#! /bin/sh

if [ -d ".env" ];
then
    echo "Enabling virtual env"
else
    echo "No Virtual env. Please run setup.sh first"
    exit N
fi

# Activate virtual env
. .venv/Scripts/Activate.ps1

export ENV=development
python main.py
deactivate