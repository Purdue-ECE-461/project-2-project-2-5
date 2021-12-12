# from _typeshed import NoneType
import json # pragma: no cover
import re # pragma: no cover
import logging # pragma: no cover
import LogWrapper # pragma: no cover
import os # pragma: no cover
import sys # pragma: no cover
import stat # pragma: no cover
import git # pragma: no cover

from git.exc import GitCommandError # pragma: no cover
from CalcHandler import CalcHandler # pragma: no cover
from github import Github # pragma: no cover
from collections import defaultdict # pragma: no cover
from git import Repo as gitRepo # pragma: no cover
import glob # pragma: no cover
import shutil # pragma: no cover
import datetime # pragma: no cover
import requests # pragma: no cover
import math # pragma: no cover
from typing import Any # pragma: no cover


class CalcHandlerGit(CalcHandler):

    """
    Handles interactions with the Github API and performs calculations
    to return scores for each metric. Inherits from CalcHandler and overrides
    functions as needed.
    """


    def __init__(self, url):
        # try:
        super().__init__(url)
        self.set_logger(__name__)
        self.token = os.environ.get('GITHUB_TOKEN')
        self.api_request_header = {'Authorization': 'token %s' % self.token}
        self.api_data = self.__api_http_get_general_repo_data()
        self.file_ext_list = self.__api_parse_file_exts("file_exts.txt")

        #initialize repo- if either of these fail, stop evaluation of current
        # repository
        self.github_obj = self.__api_get_git_object()
        self.git_repo = self.__api_get_git_repo(self.repo_directory)

        # generate metrics- if these raise an exception, set corresponding
        # metrics to 0
        try:
            self.dir_list, self.file_name_list = self.__api_get_file_contents_recursive()
        except:
            self.dir_list = []
            self.file_name_list = []

        self.license = self.__api_get_licenseID()
        self.contributions_data = self.__api_get_contributions_data()
        self.release_frequency = self.__api_check_release_frequency()
        self.commit_list = self.__api_get_commit_list()

        self.last10_commit_author_count = self.__api_get_last10_commit_author_count()
        self.checkissues = self.__api_check_opened_issues()
        self.last_3_issues = self.__api_get_last3_issues()

    def __sigmoid(self, x, scaling_factor=1):
        return 2 / (1 + math.exp(-1 * scaling_factor * x)) - 1

    def __api_get_git_object(self)->Any:
        """pygithub get git object using token"""
        try:
            gitobject = Github(self.token)
            return gitobject
        except:
            print("get_git_object, bad token given")
            self.log_exception("get_git_object, bad token given")
            self.github_obj = None
            raise

    def __api_get_git_repo(self, repo_directory)->Any:
        "pygithub get object from directory"
        try:
            return self.github_obj.get_repo(repo_directory)
        except:
            print("get_git_repo")
            self.log_exception("get_git_repo")
            raise

    def __api_get_licenseID(self) -> str:
        """pygithub request to get license information"""
        repo_license = ""
        try:
            repo_license = self.git_repo.get_license()
        except:
            print("get_licenseID")
            self.log_exception("get_licenseID")
            return ""
        license_ID = repo_license.license.spdx_id
        return license_ID
            # return None

    # [count, highest, total]
    def __api_get_contributions_data(self)->list:
        """returns a list with the number of contributors,
            max number of contributions and the total number of contributions.
        """
        try:
            contributors = self.git_repo.get_contributors(anon=True)

            highest = contributors[0].contributions # user with the highest number of contributions
            total = 0 # total number of contributions
            count = 0 # number of all contributors

            count = contributors.totalCount
            total = self.__api_get_num_commits()
            #self.get_num_commits()
            return [count, highest, total]
        except:
            print("get_contributions_data")
            self.log_exception("get_contributions_data")

    # should return a list of all the releases
    def __api_check_release_frequency(self)->list:
        """counts the number of releases per year over the past 5 years.
        returns 1 if at least 2 per year, 0 otherwise
        return 0 on failure"""
        try:
            releases = self.git_repo.get_tags() # obtain all tags from the repository
            release_count_per_year = defaultdict(int) # dictionary to store count of releases per year for the last 5 years
            if len(list(releases)) == 0:
                return 0

            for release in releases:
                date = str(release.commit.commit.author.date)
                year = int(date[:4]) # extract the year from the release date

                # if year within the last 5 years update the count for that year
                if year >= 2017:
                    release_count_per_year[year] += 1

            # if any of the years in the last 5 years have a release count less than 2, it returns 0, else it passes and returns 1           
            for year in release_count_per_year:
                if release_count_per_year[year] < 2:
                    return 0
            return 1
        except:
            self.log_exception("check_release_frequency")
            return 0

    #@CalcHandler.log_method_decorator # pragma: no cover
    def __api_get_last10_commit_author_count(self)->int:
        """return the number of authors in the last 10% of commits
        return 0 on failure
        """

        try:
            commits_list = self.git_repo.get_commits()
            num_of_contributors, highest_contributions, commits_count = self.contributions_data
            last10_commits = round(0.1 * commits_count) # number of commits in the last 10%

            authors_in_last10 = [] # stores the authors from the last 10% of commits
            count_curr_commits = 0 # counter for the while loop. Exits when this variable is equal to last 10 commits.

            while count_curr_commits != last10_commits:
                authors_in_last10.append(commits_list[count_curr_commits].author)
                count_curr_commits += 1

            author_count_last10 =  len(set(authors_in_last10)) #removes the duplicates authors and counts the remainder
            return author_count_last10
        except:
            self.log_exception("get_last10_commit_author_count")
            return 0

    #@CalcHandler.log_method_decorator # pragma: no cover
    def __api_check_opened_issues(self)->int:
        """checks if any issues have been opened for the last 100 days
        return 0 on failure
        """
        try:
            date = datetime.datetime.now()
            diff = datetime.timedelta(days = 100)
            date_diff = date - diff
            open_issues_count = self.__api_get_open_issues()
            last100_issues_count = self.git_repo.get_issues(since=date_diff).totalCount # since=date_diff
            #print(open_issues_count, last100_issues_count)

            if open_issues_count - last100_issues_count > 0:
                return 0

            return 1
        except:
            self.log_exception("check_opened_issues")
            return 0

    def __api_parse_file_exts(self, file_ext_list_filename="file_exts.txt") -> None:
        """parses text file (included in directory) with the list of file
         extensions that count as code files"""
        file_ext_list = []
        try:
            with open(file_ext_list_filename) as f_exts:
                for line in f_exts:
                    file_ext_list.append(str.rstrip(line.lower()))
            return file_ext_list
        except:
            self.log_exception("parse_file_exts")


    def __clone_repo(self)->None:
        """use GitPython to clone repository"""
        try:
            if (os.path.isdir(self.user)):
                self.__remove_cloned_repo()
            else:
                gitRepo.clone_from(self.url, self.repo_directory)

        # except GitCommandError:
            # gitRepo.clone_from(self.url, self.repo_directory)
        except:
            self.log_exception("clone_repo")

    def __parse_repo_filenames_as_list(self) -> list:
        """get list of files within the cloned directory"""
        repofiles = glob.glob(self.user+'/**/*', recursive=True)
        return repofiles

    def __filter_list_by_code_files(self, repofiles)->list:
        """return list of files with extensions within the list of code file extensions"""
        f_filtered = []
        for name in repofiles:
            if os.path.splitext(name)[-1].lower() in self.file_ext_list:
                f_filtered.append(name)
        self.code_file_list = f_filtered
        return f_filtered

    #@CalcHandler.log_method_decorator # pragma: no cover
    def code_file_count(self)->int:
        """number of code files in the repository"""
        return len(self.file_name_list)

    #@CalcHandler.log_method_decorator # pragma: no cover
    def get_code_comment_ratio(self)->int:
        """get the ratio between the number of lines of code and the number of
        lines of comment within the repository.
        1. clones repo
        2. get list of code files
        3. parse files to get lines of code, lines of comments
        4. remove local copy of cloned repo
        return 0 on exception
        """
        lines = 0
        comments = 0
        try:
            self.__clone_repo()
            repofiles = self.__parse_repo_filenames_as_list()
            file_list = self.__filter_list_by_code_files(repofiles)
            lines, comments = self.__parse_lines_and_comments(file_list)
            self.__remove_cloned_repo()
        except:
            self.log_exception("get_code_comment_ratio")
            return 0
        self.__remove_cloned_repo()

        if lines == 0:
            return 0
        else:
            return comments / lines



    def __parse_lines_and_comments(self, source_file_list)->tuple:
        """count the number of code lines (lines that aren't blank in code files)
        and the number of lines of comments within the code files"""
        total_linecount = 0
        comment_linecount = 0

        if source_file_list == []: return 0, 0

        for file in source_file_list:
            if os.path.isdir(file):
                continue
            try:
                with open(file) as f:
                    try:
                        linelist = f.readlines()
                        comment, total = self.__count_lines_in_file(linelist)
                        comment_linecount += comment
                        total_linecount += total
                    except:
                        pass
            except:
                self.log_exception(file)
        return total_linecount, comment_linecount

    #@CalcHandler.log_method_decorator # pragma: no cover
    def __count_lines_in_file(self, line_list)->int:
        """count the number of non-empty lines in a single file
        """
        comment_line_count = 0
        in_comment_block = False
        linecount = 0
        for line in line_list:
            stripped_line = line.strip()

            if stripped_line:
                linecount += 1
                if in_comment_block == True:
                    comment_line_count += 1
                    if '*/' in stripped_line:
                        in_comment_block = False
                elif stripped_line[0:2] == '//':
                    comment_line_count += 1
                elif stripped_line[0:2] == '/*':
                    comment_line_count += 1
                    in_comment_block = True

        return comment_line_count, linecount

    def __api_get_file_contents(self, filename)->str:
        """use api to get the contents of a single file
        entire file as a single string
        """
        try:
            contents = self.git_repo.get_contents(filename)
            return contents.decoded_content.decode()
        except:
            return None

    #@CalcHandler.log_method_decorator # pragma: no cover
    def get_readme_score(self)->int:
        """calculate readme score based on existence of keywords in README file.
        on exception, return 0
        """

        readme_text = self.__api_get_file_contents("README.md")

        #just for redundancy, check for readme in lowercase
        if (readme_text == None):
            readme_text = self.__api_get_file_contents("readme.md")

        if readme_text == None:
            return 0

        score = int('install' in readme_text.lower())
        score += int('usage' in readme_text.lower())
        score += int('license' in readme_text.lower())

        return score / 3

    def __api_get_file_contents_recursive(self)->list:
        """use api to create list of directories and file names
        throws exception on failure, return empty list
        """

        contents = None
        dir_list = []
        file_name_list = []

        try:
            contents = self.git_repo.get_contents("")
        except:
            self.log_exception("get_code_line_count")
            raise
        # print(contents)

        if contents != None:
            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    dir_list.append(file_content.name)
                    contents.extend(
                        self.git_repo.get_contents(file_content.path))
                else:
                    file_name_list.append(file_content.name.lower())
        return dir_list, file_name_list

    def __remove_cloned_repo(self)->None:
        """remove the repository that was cloned locally
        """
        if not os.path.isdir(self.user):
            self.info("Remove_cloned_repo: Directory does not exist")
            return
        try:
            shutil.rmtree(self.user, ignore_errors=False, onerror=None)
        except:
            self.log_exception("remove cloned repo")


    #@CalcHandler.log_method_decorator # pragma: no cover
    def __api_get_subscribers(self)->int:
        """pygithub API request for # subscribers
        return 0 on exception"""
        try:
            return self.api_data['subscribers_count']
        except:
            self.log_exception("get_subscribers")
            return 0

    #@CalcHandler.log_method_decorator # pragma: no cover
    def __api_get_releases(self)->Any:
        """pygithub API request for # releases
            need to do it through tags because releases function
            does not give the proper info
            return 0 on exception

            # https://github.com/orbitdb/orbit-db-community-stats/blob/main/stats.py
        """
        try:
            return self.git_repo.get_tags()
        except:
            self.log_exception("get_releases")
            return 0

    #@CalcHandler.log_method_decorator # pragma: no cover
    def __api_get_stargazers(self)->int:
        """pygithub API request for # people who starred repository
        return 0 on exception
        """
        try:
            # return self.git_repo.get_stargazers()
            return self.api_data['stargazers_count']
        except:
            self.log_exception("get_stargazers")
            return 0

    #@CalcHandler.log_method_decorator # pragma: no cover
    def __api_get_network_count(self)->int:
        """pygithub API request for # of forks of the repository
        return 0 on exception
        """
        try:
            # return self.git_repo.get_stargazers()
            return self.api_data['network_count']
        except:
            self.log_exception("get_network_count")
            return 0

    #@CalcHandler.log_method_decorator # pragma: no cover
    def __api_get_num_commits(self)->int:
        """pygithub API request for # commits
        return 0 on exception
        """
        try:
            return self.git_repo.get_commits().totalCount
        except:
            return 0

    #@CalcHandler.log_method_decorator # pragma: no cover
    def __repo_age(self) -> int:
        """pygithub use first repo commit to get repo age
        return 0 on exception
        """
        if (self.commit_list == None):
            return 0
        if (len(self.commit_list) > 0):
            oldest_commit = self.commit_list[-1].commit.author.date
            return ((datetime.datetime.now() - oldest_commit)).days

        else:
            return 0

    def __api_get_commit_list(self)->list:
        """pygithub get list of all commits
        return empty list on exception
        """
        try:
            if self.git_repo.get_commits().totalCount > 0:
                return [x for x in self.git_repo.get_commits()]
            else:
                #self.logger.error("Empty commit list")
                return []
        except:
            self.log_exception("get_commit_list")

    def __api_http_request(self, url)->Any:
        """request info from github API directly
        return json object
        """
        try:
            return requests.get(url, headers=self.api_request_header).json()
        except json.JSONDecodeError:
            # print("BAD")
            self.log_exception("request_from_github_api")
            return None

    #@CalcHandler.log_method_decorator # pragma: no cover
    def __api_http_get_closed_issues(self)->Any:
        """github API, get number of closed issues
        return 0 on exception

        https://stackoverflow.com/questions/17622439/how-to-use-github-api-token-in-python-for-requesting
        """

        url = 'https://api.github.com/search/issues?q=repo:' + \
            self.repo_directory+'+type:issue+state:closed'
        try:
            data = self.__api_http_request(url)
            return data['total_count']
        except:
            self.log_exception("get_closed_issues")
            return 0

    def __api_http_get_general_repo_data(self)->Any:
        """use github API directly to get general repo info
        https://stackoverflow.com/questions/17622439/how-to-use-github-api-token-in-python-for-requesting
        """

        url = 'https://api.github.com/repos/' + self.repo_directory
        return self.__api_http_request(url)

    #@CalcHandler.log_method_decorator # pragma: no cover
    def __api_get_open_issues(self)->int:
        """pygithub API request to get # open issues
        return 0 on exception
        """
        try:
            return self.git_repo.get_issues().totalCount
        except:
            self.log_exception("get_open_issues")
            return 0

    #@CalcHandler.log_method_decorator # pragma: no cover
    def get_issue_ratio(self)->int:
        """calculate ratio of open issues to total issues
        formula set up so it will return 0 on failure
        """
        open_issues = self.__api_get_open_issues()
        closed_issues = self.__api_http_get_closed_issues()
        return 1 - (1 + open_issues) / (open_issues + closed_issues + 1)

    def get_test_existence(self)-> bool:
        """check for existence of a test directory or file
        return true if it exists and false otherwise
        """

        list_of_test_dirs = [fname for fname in self.dir_list if 'test' in fname]
        list_of_test_files = [fname for fname in self.file_name_list if 'test' in fname]
        return (list_of_test_dirs != []) or (list_of_test_files != [])

    #@CalcHandler.log_method_decorator # pragma: no cover
    def get_reliability(self)->int:
        """Reliability is based on 5 factors:
            1. age
            2. num people that starred the repo
            3. num subscribers
            4. num releases
            5. num forks of the repository

            age is a scaling factor, other factors averaged together
        """

        #age will be 1/2 at 80 days old
        age_factor = self.__sigmoid(self.__repo_age(), 5/365)

        stars_baseline = 100
        subs_baseline = 100
        releases_baseline = 5
        network_baseline = 5

        stars_count = min(self.__api_get_stargazers() / stars_baseline, 1)
        subs_count = min(self.__api_get_subscribers() / subs_baseline, 1)
        network_count = min(self.__api_get_network_count() / network_baseline, 1)
        releases_count = min(self.__api_get_releases().totalCount / releases_baseline, 1)

        return age_factor * (\
            0.25 * stars_count + \
            0.25 * subs_count + \
            0.25 * network_count + \
            0.25 * releases_count )

    def __api_get_last3_issues(self)->list:
        """pygithub API request for last 3 issues
        return 0 on exception
        """

        try:
            #self.git_repo.get_issues(state='closed')[:3] #Retrieves the last three issues as type Issue
            break_check = 0
            last_issues = []
            for issues in self.git_repo.get_issues(state='closed'):
                last_issues.append(issues)
                break_check += 1
                if break_check >= 3:
                    break
            return last_issues
        except:
            self.log_exception("get_last3_issues")
            return 0

    