#!/usr/bin/bash
# in file `run`
virtualEnvironmentName=virtual_env

if [ "$1" == "install" ]; then
  printf "\nInstalling...\n"
  python3 -m venv $virtualEnvironmentName
  source $virtualEnvironmentName/bin/activate
  python3 -m pip --quiet install --upgrade pip #maybe get rid of or add user
  python3 run_handler.py "$1"
elif [ "$1" == "test" ]; then
  printf "\nTesting...\n"
  source $virtualEnvironmentName/bin/activate
  python3 run_handler.py "$1"
else
  source $virtualEnvironmentName/bin/activate
  export GITHUB_TOKEN="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" # PASTE TOKEN HERE INSIDE OF QUOTATIONS
  python3 run_handler.py
fi

deactivate
