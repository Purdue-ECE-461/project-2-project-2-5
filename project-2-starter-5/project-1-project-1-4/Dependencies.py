import subprocess
import sys

def download_dependencies():
    """
    This function will download and install all specified dependencies required to run the rest of the project code.
        Inputs: none
        Returns: void
        
    """
    #all the required libraries
    required = ["PyGithub", "regex", "pypi", "coverage", "pytest", "pylint", "python-dotenv", "GitPython", "beautifulsoup4", "glob2", "html5lib"] 
    num_installed = 0 # number of libraries that were succesfully installed
    unsuccessful = [] # list of all the libraries that failed to install

    for library in required:
        output = subprocess.run(["pip", "install", library], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # install the libraries 

        #check if successfull. if it is, increment the number installed. Else, append to the unsuccessful list.
        if output.returncode == 1:
            unsuccessful.append(library)
        else:
            num_installed += 1

    print("\n{} Dependencies Installed...\n".format(num_installed)) #Output to console

    #check if any installation failed and inform the user
    if unsuccessful:
        print("Could not install the following libraries: {}\n".format(unsuccessful))

    pass