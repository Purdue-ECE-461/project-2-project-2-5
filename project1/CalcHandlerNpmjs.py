from CalcHandlerGit import CalcHandlerGit # pragma: no cover
import requests # pragma: no cover
from bs4 import BeautifulSoup # pragma: no cover

class CalcHandlerNpmjs(CalcHandlerGit):
    
    """
    This class handles Npmjs links that are fed in. It scrapes the HTML at the URL to grab the Github URL
    Input: URL string containing the Mpmjs URL
    Return: CalcHandlerNpmjs object which contains a git URL
    Web scraping code provided by: https://www.crummy.com/software/BeautifulSoup/bs4/doc/

    """
    def __init__(self, url):
        #self.set_logger(__name__)
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html5lib')

        git_url = soup.find("a", {"aria-labelledby": "repository"}).get('href') #find the github URL on html5 file
        #self.logger.info("Npmjs url, extracted %s from the npmjs page.", git_url)
        if git_url == None: #if no github URL is on the npmjs site
            print("No Github URL to scrape!")
            raise ValueError
        super().__init__(git_url)
