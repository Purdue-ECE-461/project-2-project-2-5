# ECE 46100 Fall 2021 Team 5, Project 1
project-2-project-2-5 created by GitHub Classroom

This project is a Flask application that serves as a package registry. It has the ability to upload, update, download, and rate packages that are stored as entities in Google Datastore. 
In order to use this tool, first clone the repository and change your current working directory to the root of the cloned repository.
There are three different commands that are accepted.
First, the dependencies must be installed to a virtual environment. To do this, run the command "bash ./run.sh install" on the command line interface. This will install all needed dependencies within a virtual environment.

After all dependencies are installed, you can then begin evaluating the trustworthiness of a set of modules. To do this, run the command "./run URL_FILE", where URL_FILE is the absolute location of a file consisting of an ASCII-encoded newline-delimited set of URLs. Acceptable URL's include GitHub repository URL's and NPMJS package URL's.

You may test the correctness of the tool by running "./run test" which will run a test suite of pre-determined URL's and test cases. At the conclusion of the test, the tool will print out how many test cases passed and how much code was covered.

Don't forget to do "pip install -t lib -r requirements.txt"

This application was developed as part of ECE 46100 Fall 2021 at Purdue University by Raymond Ngo, Isabelle Akian, and Vraj Parmar
