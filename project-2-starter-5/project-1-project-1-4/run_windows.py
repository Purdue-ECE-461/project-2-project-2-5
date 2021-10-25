import sys
from subprocess import call

rc = call(["run_bash_windows.sh",sys.argv[1]], shell=True) #uncomment this line for Windows OS, comment one above
sys.exit(0)
