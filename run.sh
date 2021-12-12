#!/usr/bin/bash
# in file `run`
# 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
virtualEnvironmentName=virtual_env

if [ "$1" == "install" ]; then
  printf "\nInstalling...\n"
  python3 -m venv $virtualEnvironmentName
  source $virtualEnvironmentName/bin/activate
  python3 -m pip --quiet install --upgrade pip #maybe get rid of or add user
  pip install -r ./requirements.txt
  export GOOGLE_APPLICATION_CREDENTIALS="./project-2-331602-22c5987270e1.json"
  # ./google-cloud-sdk/install.sh
  # ./google-cloud-sdk/bin/gcloud init
  # gcloud init
  # ./google-cloud-sdk/bin/gcloud components install app-engine-python
  # ./google-cloud-sdk/bin/gcloud config set project project-2-331602
  # ./google-cloud-sdk/bin/gcloud compute ssh instance-1
  # ./google-cloud-sdk/bin/gcloud beta billing projects link project-2-331602  --billing-account 0175E5-C52C07-062983
  # ./google-cloud-sdk/bin/gcloud services enable cloudbuild.googleapis.com
  # ./google-cloud-sdk/bin/gcloud config set gcloudignore/enabled true
  # ./google-cloud-sdk/bin/gcloud app create --project=project-2-331602
  # ./google-cloud-sdk/bin/gcloud datastore export gs://main-registry-461-project-2 --async
  python3 project1/run_handler.py "$1"
  
  
  
  # ./google-cloud-sdk/bin/gcloud app deploy

  # ./google-cloud-sdk/bin/gcloud app browse
  
  # python3 main.py
#   python3 run_handler.py "$1"
elif [ "$1" == "test" ]; then
  printf "\nTesting...\n"
  source $virtualEnvironmentName/bin/activate
  pip install Flask
#   python3 run_handler.py "$1"
else
  source $virtualEnvironmentName/bin/activate
  export FLASK_APP=main
  export GOOGLE_APPLICATION_CREDENTIALS="./project-2-331602-22c5987270e1.json"
  flask run
fi

deactivate
