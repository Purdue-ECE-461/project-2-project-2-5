import logging # pragma: no cover
import subprocess # pragma: no cover
import sys # pragma: no cover
from Repo import * # pragma: no cover
from coverage import Coverage # pragma: no cover

"""
Skeleton to test 20 testcases to achieve code coverage

Steps in each function:
    Creates a Repo object in the main based on the URL passed in
    extracts the repo directory
    Creates a Repo object based on the URL and directory by calling the Repo class
    Checks the returned values against our hard coded values
    if all looks right it returns 1
    else it returns 0 and writes the checks that went wrong to our LOG_FILE
"""
class bcolors: # pragma: no cover
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

test_case_num = 0

def check_for_errors(func, repo=None):
    '''Only checks to make sure no exceptions are thrown'''
    global test_case_num #this way it doesn't have to be an argument
    test_case_num += 1
    try:
        if repo==None:
            func()
        else:
            func(repo)
        #print(str(test_case_num) + ': ' + bcolors.OKGREEN + "SUCCESS" + bcolors.ENDC)
        return 1
    except:
        #print(str(test_case_num) + ': ' + bcolors.WARNING + "FAIL" + bcolors.ENDC)
        raise



def test_CalcHandlerNpmjs_functions(URL): # pragma: no cover
    try:
        ch = CalcHandlerNpmjs(URL)

        numpassed = 0
        numpassed += check_for_errors(ch._CalcHandlerGit__repo_age)
        numpassed += check_for_errors(ch._CalcHandlerGit__api_get_stargazers)
        numpassed += check_for_errors(ch._CalcHandlerGit__api_get_subscribers)
        numpassed += check_for_errors(ch._CalcHandlerGit__api_get_network_count)
        numpassed += check_for_errors(ch._CalcHandlerGit__api_get_releases)
        numpassed= check_for_errors(ch._CalcHandlerGit__api_get_commit_list)
        numpassed += check_for_errors(ch._CalcHandlerGit__api_http_get_closed_issues)
        numpassed += check_for_errors(ch.code_file_count)
        numpassed += check_for_errors(ch._CalcHandlerGit__api_get_licenseID)
        numpassed += check_for_errors(ch._CalcHandlerGit__api_check_release_frequency)
        numpassed += check_for_errors(ch._CalcHandlerGit__api_get_contributions_data)
        numpassed += check_for_errors(ch.get_reliability)
        numpassed += check_for_errors(ch.get_issue_ratio)
        numpassed += check_for_errors(ch.get_test_existence)
        numpassed += check_for_errors(ch.get_readme_score)
        numpassed += check_for_errors(ch.get_code_comment_ratio)
    except:
        return 0
    return 1


def test_CalcHandlerGit_functions(URL): # pragma: no cover
    try:
        ch = CalcHandlerGit(URL)

        numpassed = 0
        numpassed += check_for_errors(ch._CalcHandlerGit__repo_age)
        numpassed += check_for_errors(ch._CalcHandlerGit__api_get_stargazers)
        numpassed += check_for_errors(ch._CalcHandlerGit__api_get_subscribers)
        numpassed += check_for_errors(ch._CalcHandlerGit__api_get_network_count)
        numpassed += check_for_errors(ch._CalcHandlerGit__api_get_releases)
        numpassed= check_for_errors(ch._CalcHandlerGit__api_get_commit_list)
        numpassed += check_for_errors(ch._CalcHandlerGit__api_http_get_closed_issues)
        numpassed += check_for_errors(ch.code_file_count)
        numpassed += check_for_errors(ch._CalcHandlerGit__api_get_licenseID)
        numpassed += check_for_errors(ch._CalcHandlerGit__api_check_release_frequency)
        numpassed += check_for_errors(ch._CalcHandlerGit__api_get_contributions_data)
        numpassed += check_for_errors(ch.get_reliability)
        numpassed += check_for_errors(ch.get_issue_ratio)
        numpassed += check_for_errors(ch.get_test_existence)
        numpassed += check_for_errors(ch.get_readme_score)
        numpassed += check_for_errors(ch.get_code_comment_ratio)
    except:
        return 0
    return 1

def test_linecount(URL):
    ch = CalcHandlerGit(URL)
    # with open("jashkenas/underscore/karma.conf.js") as f:
        # linelist = f.readlines()
    repofiles = ch.__parse_repo_filenames_as_list()
    file_list = ch.__filter_list_by_code_files(repofiles)
    ch.__parse_lines_and_comments(file_list)



def create_repo(URL):
    # Extracts the repository and creates the Repo object
    repo_obj = Repo(URL)

    # Make all the score calculations
    if repo_obj.is_good_URL == True:
        repo_obj.do_calc()

    return repo_obj


def test01(repo_obj):
    if repo_obj.net_score >= 0.75:
        return 0
    if repo_obj.rampup_score <= 0.4:
        return 0
    if repo_obj.correctness_score >= 0.6:
        return 0
    if repo_obj.license_score != 1:
        return 0
    if repo_obj.bus_factor_score >= 0.5:
        return 0
    if repo_obj.maint_score >= 0.7:
        return 0
    return 1

def test02(repo_obj): #all -1's
    if repo_obj.net_score != -1:
        return 0
    if repo_obj.rampup_score != -1:
        return 0
    if repo_obj.correctness_score != -1:
        return 0
    if repo_obj.license_score != -1:
        return 0
    if repo_obj.bus_factor_score != -1:
        return 0
    if repo_obj.maint_score != -1:
        return 0
    return 1

def test03(repo_obj): #all -1's
    if repo_obj.net_score != -1:
        return 0
    if repo_obj.rampup_score != -1:
        return 0
    if repo_obj.correctness_score != -1:
        return 0
    if repo_obj.license_score != -1:
        return 0
    if repo_obj.bus_factor_score != -1:
        return 0
    if repo_obj.maint_score != -1:
        return 0
    return 1

def test04(repo_obj):  #all -1's
    if repo_obj.net_score != -1:
        return 0
    if repo_obj.rampup_score != -1:
        return 0
    if repo_obj.correctness_score != -1:
        return 0
    if repo_obj.license_score != -1:
        return 0
    if repo_obj.bus_factor_score != -1:
        return 0
    if repo_obj.maint_score != -1:
        return 0
    return 1

def test05(repo_obj):
    if repo_obj.net_score != 0:
        return 0
    if repo_obj.rampup_score != 0:
        return 0
    if repo_obj.correctness_score != 0:
        return 0
    if repo_obj.license_score != 0:
        return 0
    if repo_obj.bus_factor_score != 0:
        return 0
    if repo_obj.maint_score != 0:
        return 0
    return 1

def test06(repo_obj):
    if repo_obj.net_score <= 0.5:
        return 0
    if repo_obj.rampup_score <= 0.5:
        return 0
    if repo_obj.correctness_score <= 0.75:
        return 0
    if repo_obj.license_score != 1:
        return 0
    if repo_obj.bus_factor_score <= 0.25:
        return 0
    if repo_obj.maint_score <= 0.25:
        return 0
    return 1

def test07(repo_obj):
    if repo_obj.net_score <= 0.5:
        return 0
    if repo_obj.rampup_score <= 0.5:
        return 0
    if repo_obj.correctness_score <= 0.75:
        return 0
    if repo_obj.license_score != 1:
        return 0
    if repo_obj.bus_factor_score <= 0.25:
        return 0
    if repo_obj.maint_score <= 0.25:
        return 0
    return 1

def test08(repo_obj):
    if repo_obj.net_score != 0:
        return 0
    if repo_obj.rampup_score <= 0.5:
        return 0
    if repo_obj.correctness_score <= 0.3:
        return 0
    if repo_obj.license_score != 0:
        return 0
    if repo_obj.bus_factor_score <= 0.3:
        return 0
    if repo_obj.maint_score >= 0.8:
        return 0
    return 1


def test_coverage():
    cov = Coverage()
    cov.start()
    Numpassed = 0 # counts the number of tests that passed.
    # test_linecount("https://github.com/jonschlinkert/even")
    if test_CalcHandlerGit_functions('ECE 46100!') == 0:    #should fail        Test 1
        Numpassed += 1
    if test_CalcHandlerGit_functions('https://github.com/ThisIsNot/ARealRepoLOL') == 0:     #Test 2
        Numpassed += 1
    if test_CalcHandlerGit_functions('https://www.linkedin.com/in/davisjam/') == 0:     #Test 3
        Numpassed += 1
    if test_CalcHandlerGit_functions('https://www.npmjs.com/package/ThisIsNotARealPackageLOL') == 0:     #Test 4
        Numpassed += 1
    Numpassed += test_CalcHandlerGit_functions('https://github.com/jonschlinkert/even')        #Test 5
    Numpassed += test_CalcHandlerGit_functions('https://github.com/Owen-Prince/blank_repo')     #Test 6
    Numpassed += test_CalcHandlerGit_functions('https://github.com/comparison-sorting/odd-even-merge-sort')     #Test 7

    if test_CalcHandlerNpmjs_functions('https://www.npmjs.com/package/ThisIsNotARealPackageLOL') == 0:     #Test 8
        Numpassed += 1
    if test_CalcHandlerNpmjs_functions('https://www.npmjs.com/package/ece461test') == 0:     #Test 9
        Numpassed += 1
    Numpassed += test_CalcHandlerNpmjs_functions('https://www.npmjs.com/package/even')  #Test 10
    Numpassed += test_CalcHandlerNpmjs_functions('https://www.npmjs.com/package/fresh')  #Test 11
    Numpassed += test_CalcHandlerNpmjs_functions('https://www.npmjs.com/package/jquery')  #Test 12
    



    Numpassed += test01(create_repo('https://github.com/jonschlinkert/even'))    #Test 13
    Numpassed += test02(create_repo('https://www.linkedin.com/in/davisjam/'))    #Test 14
    Numpassed += test03(create_repo('https://www.npmjs.com/package/ThisIsNotARealPackageLOL'))    #Test 15
    Numpassed += test04(create_repo('https://github.com/ThisIsNot/ARealRepoLOL'))    #Test 16
    Numpassed += test05(create_repo('https://github.com/Owen-Prince/blank_repo'))    #Test 17
    Numpassed += test06(create_repo('https://www.npmjs.com/package/fresh'))    #Test 18
    Numpassed += test07(create_repo('https://www.npmjs.com/package/jquery'))    #Test 19
    Numpassed += test08(create_repo('https://github.com/comparison-sorting/odd-even-merge-sort'))    #Test 20

    cov.stop()
    #percent = cov.report(skip_empty=True, omit=["test_coverage.py", "LogWrapper.py"],show_missing = True, ignore_errors = True, file=sys.stdout)
    percent = round(cov.xml_report(skip_empty=True, omit=["test_coverage.py", "LogWrapper.py"], ignore_errors = True))

    print("Total: ", 20, file = sys.stdout)
    print("Passed: ", Numpassed, file = sys.stdout)
    print("Coverage: ", percent, file = sys.stdout)
    print("{}/20 test cases passed. {}% line coverage achieved".format(Numpassed, percent))
    pass

if __name__ == '__main__':
    test_coverage()