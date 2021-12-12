import re, logging, sys # pragma: no cover
from LogWrapper import LogWrapper # pragma: no cover

class CalcHandler(LogWrapper):
    """
    Parent class for the individual classes that handle interacting with APIs # pragma: no cover
    for different websites and calculating respective scores.
    """
    url = ""
    repo_directory = ""
    user=""


    # @LogWrapper.log_init_decorator
    def __init__(self, _url):
        super().__init__()
        self.set_logger(__name__)
        self.url = _url
        self.repo_directory = self.get_repo_directory(_url)
        self.user = str.split(self.repo_directory, '/')[0]

    def get_repo_directory(self, url_in):
        pattern = r'.*.com\/'       #select up to .com/
        user_and_repo = re.sub(pattern, '', url_in) #replace that string above with ''
        if user_and_repo == url_in:     #when re.sub() is unable to find the pattern, it returns the original string, therefore we can see if it was successful by checking here
            user_and_repo = 'UNABLE TO PARSE FOR REPO' #if unsuccessful, rename to unable to parse, will change this most likely to '-1' or something similar
        return(user_and_repo)
