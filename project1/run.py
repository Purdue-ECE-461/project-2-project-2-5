import sys
from subprocess import call, run, DEVNULL

output = run(["chmod", "+x", "run_bash_ecngrid.sh"], stdout=DEVNULL, stderr=DEVNULL) #This line is needed for Linux to give permissions
rc = call(["run_bash_ecngrid.sh",sys.argv[1]])     #uncomment this line for Unix/Linux OS, comment one below
sys.exit(0)
