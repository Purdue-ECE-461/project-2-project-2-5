import sys, subprocess
from Dependencies import download_dependencies

if __name__ == "__main__":

    #Confirm that only one user input is given
    # if (len(sys.argv) != 2):
    #     print('!Incorrect number of arguments given!\n|Acceptable Inputs|\n\"install\" to install dependencies\n\"test\" to test coverage and validate performance\nOr, you may enter an absolute path to a file containing line-delimited URL\'s\n')
    #     sys.exit(1)
 
    # #Mode 1 - Install
    # if sys.argv[1] == "install":
    #     download_dependencies() #from Dependencies.py
    #     sys.exit(0)

    # #Credits!
    # if sys.argv[1] == "team4":
    #     print("Made with <3 by Mohammed Fashola, Owen Prince, and Ryan Villarreal for ECE46100 Fall 2021")
    #     sys.exit(0)
    
    #Import libraries that were installed from download_dependencies()
    import logging, os, argparse
    from logging.handlers import TimedRotatingFileHandler
    from Repo import Repo
    from CLIHandler import CLIHandler
    from CalcHandler import CalcHandler
    from CalcHandlerGit import CalcHandlerGit
    from dotenv import load_dotenv
    from test_coverage import *
    load_dotenv()   #allows use of environment variables in .env file


    #Mode 2 - Test/Coverage
    # if sys.argv[1] == "test":
    #     test_coverage() #from test_coverage.py

    #Mode 3 - Run given file with URL's
    # else: 
    input_path = "https://github.com/expressjs/express" #handle directory path here
    
    #if the input given is not an absolute path. Absolute path definition varies by OS, see https://www.computerhope.com/issues/ch001708.htm
    # if not os.path.isabs(input_path):   
    #     print('!Unable to interpret arguments given!\n|Acceptable Inputs|\n\"install\" to install dependencies\n\"test\" to test coverage and validate performance\nOr, you may enter an absolute path to a file containing line-delimited URLs\n')
    #     sys.exit(1)

    #print("Manual addition.!")    

    cli = CLIHandler(input_path)  #create CLIHandler object with command line input
    #cli = CLIHandler("~/461/project-1-project-1-4/test_url_list.txt") 
    cli.calc()  #make the calculations on all repo objects extracted from the above call
    cli.print_to_console()    #print out the output
    
    sys.exit(0) #exit properly
