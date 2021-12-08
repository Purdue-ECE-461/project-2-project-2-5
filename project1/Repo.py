from os import close # pragma: no cover
from LogWrapper import LogWrapper # pragma: no cover
import re, logging # pragma: no cover
from CalcHandlerGit import CalcHandlerGit # pragma: no cover
from CalcHandlerNpmjs import CalcHandlerNpmjs # pragma: no cover

"""
Class that represents a github repository. Takes a directory to the repo
and calculates metrics on that repository.
"""
class Repo(LogWrapper):
    def __init__(self, _url):
        super().__init__()
        #self.set_logger(__name__)
        if 'github.com' in _url.lower():   #If a Github URL is passed in do this
            self.is_good_URL = True
            self.url = _url
            self.net_score = -1
            self.rampup_score = -1
            self.correctness_score = -1
            self.license_score = -1
            self.bus_factor_score = -1
            self.maint_score = -1
            self.dependenciesScore = -1
            try:
                self.calc_handler = CalcHandlerGit(_url)
            except:
                self.is_good_URL = False
                self.log_exception("Could not instantiate CalcHandlerGit object with url: " + _url)


        elif 'npmjs.com' in _url.lower():   #If a NPM URL is passed in do this
            self.is_good_URL = True
            self.url = _url
            self.net_score = -1
            self.rampup_score = -1
            self.correctness_score = -1
            self.license_score = -1
            self.bus_factor_score = -1
            self.maint_score = -1
            self.dependenciesScore = -1
            try:
                self.calc_handler = CalcHandlerNpmjs(_url)
            except:
                self.is_good_URL = False
                self.log_exception("Could not instantiate CalcHandlerNpmjs object with url: " + _url + " Could be due to nonexistent package, or no Github Repository linked.")


        else:       #Else, a non-compatible URL was fed
            self.is_good_URL = False
            #self.logger.error(f"ERROR!\n{_url}\nIS NOT AN ACCEPTABLE INPUT. ONLY GITHUB.COM AND NPMJS.COM URL'S ARE CURRENTLY SUPPORTED. THE SCORE FOR THIS URL WILL NOT BE CALCULATED.\n")
            self.url = _url
            self.net_score = -1
            self.rampup_score = -1
            self.correctness_score = -1
            self.license_score = -1
            self.bus_factor_score = -1
            self.maint_score = -1
            self.dependenciesScore = -1
            #self.calc_handler = CalcHandlerGit(self.repo_directory)

    """
    print in the following format:
    NET_SCORE RAMP_UP_SCORE CORRECTNESS_SCORE BUS_FACTOR_SCORE RESPONSIVE_MAINTAINER_SCORE LICENSE_SCORE"
    """
    def __str__(self):
        return    "{:.2f}".format(self.net_score) + ' ' \
                + "{:.2f}".format(self.rampup_score) + ' ' \
                + "{:.2f}".format(self.correctness_score) + ' ' \
                + "{:.2f}".format(self.bus_factor_score) + ' ' \
                + "{:.2f}".format(self.maint_score) + ' ' \
                + "{:.2f}".format(self.license_score) + ' '\
                + "{:.2f}".format(self.dependenciesScore) 
                # add funciton call.!
                

    #calculate each score
    def do_calc(self)->None:
        """perform all calculations"""
        self.correctness_score = self.calc_correctness_score() #owen - Done
        self.license_score = self.calc_license_score() #ryan - Done
        self.rampup_score = self.calc_rampup_score() #owen - Done
        self.bus_factor_score = self.calc_bus_factor_score() #Mohammed -Done
        self.maint_score = self.calc_maint_score() #Mohammed, Ryan - Done
        self.dependenciesScore = self.getNumDependencies(self.repo_directory)
        self.net_score = self.calc_net_score() #Done

    #@LogWrapper.log_method_decorator # pragma: no cover
    def calc_correctness_score(self):
        """correctness metric:
        1. issue to comment ratio (30%)
        2. existence of test framework (20%)
        3. reliability score (50%) - this is a combination of
            age, stars, subscribers, releases, # repository forks
         """
        score = .3 * self.calc_handler.get_issue_ratio() + \
                .5 * self.calc_handler.get_test_existence() + \
                .2 * self.calc_handler.get_reliability()
        return score

    #@LogWrapper.log_method_decorator # pragma: no cover
    def calc_bus_factor_score(self):
        """bus_factor metric
        return 0 on exception
        """
        if self.calc_handler.contributions_data == None:
            return 0
        contributor_count, highest_contributions, total_contributions = self.calc_handler.contributions_data

        #EQN 1
        EQN1 = 1 - (1 / contributor_count)
        #Make exception for divide by 0

        #EQN2
        num_authors_last10 = self.calc_handler.last10_commit_author_count
        EQN2 = num_authors_last10 / contributor_count

        #EQN 3
        EQN3 = 1 - (highest_contributions / total_contributions)

        score = (EQN1 + EQN2 + EQN3) / 3
        return score


    #@LogWrapper.log_method_decorator # pragma: no cover
    def calc_license_score(self):
        """license score metric
        return 0 on exception
        """
        #print(self.url)
        #print(self.calc_handler.license)

        acceptable_license = set(['CC-PDDC','AML','Apache-2.0','BSD-3-Clause','GPL-2.0-only', 'GPL-2.0-or-later', 'GPL-3.0-only', 'GPL-3.0-or-later', 'GPL-2.0', 'GPL-2.0+', 'GPL-2.0-with-autoconf-exception', 'GPL-2.0-with-bison-exception', 'GPL-2.0-with-classpath-exception', 'GPL-2.0-with-font-exception', 'GPL-2.0-with-GCC-exception', 'GPL-3.0', 'GPL-3.0+', 'GPL-3.0-with-autoconf-exception', 'GPL-3.0-with-GCC-exception', 'LGPL-2.0-or-later', 'LGPL-2.1-only', 'LGPL-2.1-or-later', 'LGPL-3.0-only', 'LGPL-3.0-or-later', 'LGPL-2.1', 'LGPL-2.1+', 'LGPL-2.0+', 'LGPL-3.0', 'LGPL-3.0+', 'MIT', 'MIT-0','MIT-Modern-Variant','MIT-open-group','Artistic-2.0', 'ClArtistic', 'Sleepycat', 'BSL-1.0', 'CECILL-2.0','CECILL-2.1', 'BSD-3-Clause-Clear', 'eCos-2.0', 'ECL-2.0', 'EFL-2.0', 'EUDatagrid', 'BSD-2-Clause-FreeBSD', 'FreeBSD-DOC', 'FTL', 'HPND', 'iMatix', 'Imlib2', 'IJG', 'Intel', 'NCSA', 'OLDAP-2.7', 'PSF-2.0', 'Python-2.0', 'Ruby', 'SGI-B-2.0', 'SMLNJ', 'StandardML-NJ', 'Unicode-DFS-2015', 'Unicode-DFS-2016', 'UPL-1.0', 'Unlicense', 'Vim', 'W3C', 'W3C-19980720', 'W3C-20150513', 'WTFPL', 'wxWindows', 'X11', 'XFree86-1.1', 'Zlib', 'zlib-acknowledgement', 'ZPL-2.0', 'ZPL-2.1'])  #This maybe should be defined elsewhere for performance, probably in the calculate function
        if self.calc_handler.license in acceptable_license:
            return 1
        else:
            return 0


    #@LogWrapper.log_method_decorator # pragma: no cover
    def calc_rampup_score(self):
        """ramp up score metric
        return 0 on exception
        """
        readme_score = self.calc_handler.get_readme_score()
        comment_ratio_score = self.calc_handler.get_code_comment_ratio()

        # looking for 10% comments in code
        return .4 * readme_score   + \
                .6 * min(1, (comment_ratio_score) / 0.1)

    #@LogWrapper.log_method_decorator # pragma: no cover
    def calc_maint_score(self):
        """maintenance score metric
        return 0 on exception
        """
        if self.calc_handler.contributions_data == None:
            return 0
        contributor_count, highest_contributions, total_contributions = self.calc_handler.contributions_data

        #EQN 1
        EQN1 = self.calc_handler.release_frequency

        #EQN 2
        EQN2 = self.calc_handler.checkissues

        #EQN 3
        if contributor_count < 10:
            EQN3 = (1 / 10) * contributor_count
        else:
            EQN3 = 1

        #EQN 4
        EQN4 = 1 #Default 1, set to 0 if any issue open longer than 7 days
        for issue in self.calc_handler.last_3_issues:
            open_date = issue.created_at
            close_date = issue.closed_at
            difference = close_date - open_date
            if difference.days > 7:
                EQN4 = 0
                break #dont waste time iterating through the rest
            #debugging below
            #print(f"FOR: {self.url} Opened at: {open_date} Closed at: {close_date} difference: {difference} difference(days): {difference.days} SCORE: {EQN2}")
            
        score = (EQN1 + EQN2 + EQN3 + EQN4) / 4

        return score

    #@LogWrapper.log_method_decorator # pragma: no cover
    def calc_net_score(self):
        """weighted average of all scores """

        score = self.license_score * (\
            0.4  * self.maint_score       + \
            0.16 * self.bus_factor_score  + \
            0.16 * self.correctness_score + \
            0.1  * self.rampup_score + \
            0.18 * self.dependenciesScope)
        return score

    def getNumDependencies(repo) : #repo should be in the form of "expressjs/express"
        score = 1
        url = 'https://github.com/{}/network/dependencies'.format(repo)

        print("GET " + url)
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")

        data = [
            "{}/{}".format(
                t.find('a', {"data-repository-hovercards-enabled":""}).text,
                t.find('a', {"data-hovercard-type":"repository"}).text
            )
            for t in soup.findAll("div", {"class": "Box-row"})
        ]
        
        score = score / len(data)
        return (score)

