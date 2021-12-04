#!/usr/bin/bash
# in file `run`
virtualEnvironmentName=virtual_env

if [ "$1" == "install" ]; then
  printf "\nInstalling...\n"
  python -m venv $virtualEnvironmentName
  source ./$virtualEnvironmentName/Scripts/activate
  python -m pip --quiet install --upgrade pip
  python run_handler.py "$1"
elif [ "$1" == "test" ]; then
  printf "\nTesting...\n"
  source ./$virtualEnvironmentName/Scripts/activate
  python run_handler.py "$1"
else
  source ./$virtualEnvironmentName/Scripts/activate
  python run_handler.py "$1"
fi

deactivate
exec $SHELL