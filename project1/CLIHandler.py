from LogWrapper import LogWrapper
from Repo import Repo
import re
import logging, sys



class CLIHandler(LogWrapper):

    """
    This class handles whatever is passed onto the command line except "install" and "test" which are reserved
    Input: Command Line Argument from user
    Return: CLIHandler object which contains URL's and Repo Objects

    """
    url_list = []
    repo_list = []
    command_line_arg = ""

    #@LogWrapper.log_init_decorator
    def __init__(self, _command_line_arg):
        super().__init__()
        self.set_logger(__name__)
        
        self.command_line_arg = _command_line_arg
        try:
            self.url_list, self.repo_list = self.parse_arg(_command_line_arg)
        except:
            self.logger.error("Error in parsing argument.")

    def parse_arg(self, command_line_arg):
        """
        This function parses the file at the given absolute file path.
        Inputs: Absolute file path
        Returns: 
        urls[], a list of URL's read from the input file
        repo_objects[], a list of Repo objects created using the subsequent URL

        """
        urls = []   #contains raw URLS in the order given in the file, newline delimitted
        repo_objects = []   #contains GH directory to repo in the order given in the file

        # try:
        #     URL_file = open(command_line_arg, 'r')  #open file at directory given in argv[1], exit if bad file path
        # except:
        #     self.logger.error("Unable to open file at specified absolute path!")
        #     print("Unable to open file at specified absolute path!")
        #     sys.exit(1)
        
        # for line_input in URL_file.read().splitlines():  #read in each URL which is on its own line
        #     urls.append(line_input) #append the raw URL to the url list            
        #     curr_repo = Repo(line_input)    #create a repo object for the URL given
        #     repo_objects.append(curr_repo)  #append either successful directory grab, or unsuccessful message for each URL in the input file
        urls.append(command_line_arg)
        curr_repo = Repo(command_line_arg)
        repo_objects.append(curr_repo)

        # URL_file.close()    #make sure to close that up
        return urls, repo_objects
        
    def calc(self):
        """
        This function initiates the calculations for all Repo objects in repo_list
        Inputs: Self
        Returns: void
        
        """
        for repository in self.repo_list:
            if repository.is_good_URL == True:  #if the URL is a Github or NPMJS url, else dont calculate on it
                repository.do_calc()

    def sort_by_netscore(self): #This name should be changed to avoid conflict with built in sort()
        """
        This function sorts the repo_list by highest net_score to lowest net_score
        Inputs: Self
        Returns: void
        
        """
        try:
            self.repo_list.sort(key=lambda score: score.net_score, reverse=True) #This will sort by net_score attribute in reverse
        except:
            self.logger.error("Error in sorting final output")

    def print_to_console(self):
        """
        This function prints all Repo objects in repo_list
        Inputs: Self
        Returns: void
        
        """
        self.sort_by_netscore() #First, sort the repo objects by net_score

        print("URL NET_SCORE RAMP_UP_SCORE CORRECTNESS_SCORE BUS_FACTOR_SCORE RESPONSIVE_MAINTAINER_SCORE LICENSE_SCORE") #Output header
        for repository in self.repo_list: #For all the repo objects
            print(repository.url, repository)
        sys.exit(0)
        
    

