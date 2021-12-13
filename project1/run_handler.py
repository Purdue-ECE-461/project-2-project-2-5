import sys, subprocess
from Dependencies import download_dependencies
import logging, os, argparse
from logging.handlers import TimedRotatingFileHandler
from Repo import Repo
from CLIHandler import CLIHandler
from CalcHandler import CalcHandler
from CalcHandlerGit import CalcHandlerGit
from dotenv import load_dotenv
from test_coverage import *
load_dotenv()

def runHandler(input_path):
    # input_path = "https://github.com/expressjs/express" #handle directory path here
    
    #if the input given is not an absolute path. Absolute path definition varies by OS, see https://www.computerhope.com/issues/ch001708.htm
    # if not os.path.isabs(input_path):   
    #     print('!Unable to interpret arguments given!\n|Acceptable Inputs|\n\"install\" to install dependencies\n\"test\" to test coverage and validate performance\nOr, you may enter an absolute path to a file containing line-delimited URLs\n')
    #     sys.exit(1)

    #print("Manual addition.!")    

    cli = CLIHandler(input_path)  #create CLIHandler object with command line input
    #cli = CLIHandler("~/461/project-1-project-1-4/test_url_list.txt") 
    cli.calc()  #make the calculations on all repo objects extracted from the above call
    # cli.print_to_console()    #print out the output
    return cli.getScores()
    
if __name__ == "__main__":

    print(runHandler(sys.argv[1]))
    sys.exit(0)