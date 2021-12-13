# ECE 46100 Fall 2021 Team 4, Project 1
project-1-project-1-4 created by GitHub Classroom

This project provides a method to evaluate the trustworthiness of modules hosted on GitHub.
In order to use this tool, first clone the repository and change your current working directory to the root of the cloned repository.
There are three different commands that are accepted.
First, the dependencies must be installed to a virtual environment. To do this, run the command "./run install" on the command line interface. This will install all needed dependencies within a virtual environment.

After all dependencies are installed, you can then begin evaluating the trustworthiness of a set of modules. To do this, run the command "./run URL_FILE", where URL_FILE is the absolute location of a file consisting of an ASCII-encoded newline-delimited set of URLs. Acceptable URL's include GitHub repository URL's and NPMJS package URL's.

You may test the correctness of the tool by running "./run test" which will run a test suite of pre-determined URL's and test cases. At the conclusion of the test, the tool will print out how many test cases passed and how much code was covered.

This tool was developed as part of ECE 46100 Fall 2021 at Purdue University by Mohammed Fashola, Owen Prince, and Ryan Villarreal.
