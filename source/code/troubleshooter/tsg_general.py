import os

from install.tsg_install import check_installation

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
        # TODO: add reasons for the troubleshooter to be run as root
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
        '2': unimplemented,
        '3': unimplemented,
        '4': unimplemented,
        '5': unimplemented,
        '6': unimplemented
    }
    issue = input("Please select an option: ")
    while (issue.lower() not in ['1','2','3','4','5','6','q','quit']):
        print("Unclear input. Please enter an integer corresponding with your "\
                      "issue (1-6) to continue, or 'q' to quit.")
        issue = input("Please select an option: ")
    if (issue.lower() in ['q','quit']):
        print("Exiting the troubleshooter...")
        return
    section = switcher.get(issue, lambda: "Invalid input")
    success = section()

    if (success):
        print("")
        # TODO: add smth about how couldn't find any errors, then collect the logs and give them to user and tell them to make ticket
        return
    else:
        # TODO: mention how errors were found, either try to to fix or smth idk
        return
    

# TODO: remove this after done testing
run_tsg()