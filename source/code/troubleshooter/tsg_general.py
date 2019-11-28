import os

from tsg_errors              import print_errors
from install.tsg_install     import check_installation
from connect.tsg_connect     import check_connection
from heartbeat.tsg_heartbeat import check_heartbeat

# backwards compatible input() function for Python 2 vs 3
try:
    input = raw_input
except NameError:
    pass

# check to make sure the user is running as root
def check_sudo():
    if (os.geteuid() != 0):
        print("The troubleshooter is not currently being run as root. In order to "\
              "have accurate results, we ask that you run this troubleshooter as root.\n"\
              "The OMS Agent Troubleshooter needs to be run as root for the following reasons:")
        print("  - getting workspace ID and other relevant information to debugging")
        print("  - checking files in folders with strict permissions")
        print("  - checking certifications exist / are correct")
        # TODO: add more reasons as troubleshooter changes
        print("NOTE: it will not add, modify, or delete any files without express permission.")
        print("Please try running the troubleshooter again with 'sudo'. Thank you!")
        return False
    else:
        return True

# TODO: remove function when everything is implemented
def unimplemented():
    print("This part of the troubleshooter is unimplemented yet, please come back later for more updates!")


def run_tsg():
    # check if running as sudo
    if (not check_sudo()):
        return

    print("Welcome to the OMS Agent for Linux Troubleshooter! What is your issue?\n"\
        "1: Installation failure\n"\
        "2: Agent doesn't start, can't connect to Log Analytic Services\n"\
        "3: Agent is unhealthy, heartbeat data is missing\n"\
        "4: Agent has high CPU / memory usage\n"\
        "5: Syslog isn't working\n"\
        "6: Custom logs aren't working\n"\
        "Q: Quit troubleshooter")
    switcher = {
        '1': check_installation,
        '2': check_connection,
        '3': check_heartbeat,
        '4': unimplemented,
        '5': unimplemented,
        '6': unimplemented
    }
    issue = input("Please select an option: ")
    while (issue.lower() not in ['1','2','3','4','5','6','q','quit']):
        print("Unclear input. Please enter an integer corresponding with your "\
                      "issue (1-6) to continue, or 'Q' to quit.")
        issue = input("Please select an option: ")
    if (issue.lower() in ['q','quit']):
        print("Exiting the troubleshooter...")
        return
    section = switcher.get(issue, lambda: "Invalid input")
    success = section()

    if (success == 0):
        print("No errors were found.")
        # TODO: add smth about how couldn't find any errors, then collect the logs and give them to user and tell them to make ticket
        return
    else:
        print_errors(success)
        return
    

# TODO: remove this after done testing
run_tsg()