import copy
import subprocess

# backwards compatible input() function for Python 2 vs 3
try:
    input = raw_input
except NameError:
    pass

# error info edited when error occurs
tsg_error_info = []

# list of all errors called when script ran
err_summary = []



# dictionary correlating error codes to error messages
tsg_error_codes = {
    101 : "Please go through the output above to find the errors caught by the troubleshooter.",
    102 : "Couldn't get if CPU is 32-bit or 64-bit.",
    103 : "This version of {0} ({1}) is not supported. For {2} machines, please download {3}.",
    104 : "{0} is not supported.",
    105 : "Indeterminate Operating System.",
    106 : "There isn't enough space in directory {0} to install OMS - there needs to be at least 500MB free, "\
          "but {0} has {1}MB free. Please free up some space and try installing again.",
    107 : "This system does not have a supported package manager. Please install 'dpkg' or 'rpm' "\
          "and run this troubleshooter again.",
    108 : "OMSConfig isn't installed correctly.",
    109 : "OMI isn't installed correctly.",
    110 : "SCX isn't installed correctly.",
    111 : "OMS isn't installed correctly.",
    112 : "You are currently running OMS Version {0}. This troubleshooter only "\
          "supports versions 1.11 and newer. Please head to the Github link below "\
          "and click on 'Download Latest OMS Agent for Linux ({1})' in order to update "\
          "to the newest version:\n"\
          "\n    https://github.com/microsoft/OMS-Agent-for-Linux\n\n"\
          "And follow the instructions given here:\n"\
          "\n    https://github.com/microsoft/OMS-Agent-for-Linux/blob/master/docs"\
          "/OMS-Agent-for-Linux.md#upgrade-from-a-previous-release\n",
    113 : "Couldn't get most current released version of OMS.",
    114 : "{0} {1} doesn't exist.",
    115 : "{0} {1} has {2} {3} instead of {2} {4}.",
    116 : "Certificate is invalid, please check {0} for the issue.",
    117 : "RSA key is invalid, please check {0} for the issue.",
    118 : "File {0} is empty.",
    119 : "Couldn't get {0}. Please check {1} for the issue.",
    120 : "Machine couldn't connect to {0}",
    121 : "The agent is configured to report to a different workspace - the GUID "\
          "given is {0}, while the workspace is {1}.",
    122 : "The agent isn't running / will not start.",
    123 : "Couldn't access file {0} due to the following reason: {1}.",
    124 : "At {0} {1} the agent logged this error: {2}. Please check out {3} for "\
          "more information.",
    125 : "At {0} {1} the agent logged this warning: {2}. Please check out {3} for "\
          "more information.",
    126 : "Heartbeats are failing to send data to the workspace.",
    127 : "Machine registered with more than one log analytics workspace. List of "\
          "workspaces: {0}",
    128 : "Machine is not connected to the internet.",
    129 : "The following queries failed: {0}.",
    130 : "Syslog collection is set up for workspace {0}, but OMS is set up with "\
          "workspace {1}.",
    131 : "With protocol type {0}, ports need to be preceded by '{1}', but currently "\
          "are preceded by '{2}'. Please see {3} for the issue.",
    131 : "Syslog is set up to bind to port {0}, but is currently sending to port {1}. "\
          "Please see {2} for the issue.",
    132 : "Issue with setting up ports for syslog. Please see {0} and {1} for the issue."

}  # TODO: keep up to date with error codes onenote



# get error codes from Troubleshooting.md
def get_error_codes(err_type):
    err_codes = {0 : "No errors found"}
    section_name = "{0} Error Codes".format(err_type)
    with open("files/Troubleshooting.md", 'r') as ts_doc:
        section = None
        for line in ts_doc:
            line = line.rstrip('\n')
            if (line == ''):
                continue
            if (line.startswith('##')):
                section = line[3:]
                continue
            if (section == section_name):
                parsed_line = list(map(lambda x : x.strip(' '), line.split('|')))[1:-1]
                if (parsed_line[0] in ['Error Code', '---']):
                    continue
                err_codes[parsed_line[0]] = parsed_line[1]
                continue
            if (section==section_name and line.startswith('#')):
                break
    return err_codes

# ask user if they encountered error code
def ask_error_codes(err_type, find_err, err_types):
    print("--------------------------------------------------------------------------------")
    print(find_err)
    # ask if user has error code
    answer = get_input("Do you have an {0} error code? (y/n)".format(err_type.lower()),\
                       (lambda x : x in ['y','yes','n','no']),\
                       "Please type either 'y'/'yes' or 'n'/'no' to proceed.")
    if (answer.lower() in ['y','yes']):
        # get dict of all error codes
        err_codes = get_error_codes(err_type)
        # ask user for error code
        poss_ans = lambda x : x.isdigit() or (x in ['NOT_DEFINED', 'none'])
        err_code = get_input("Please input the error code", poss_ans,\
                             "Please enter an error code ({0})\nto get the error message, or "\
                                "type 'none' to continue with the troubleshooter.".format(err_types))
        # did user give integer, but not valid error code
        while (err_code.isdigit() and (not err_code in list(err_codes.keys()))):
            print("{0} is not a valid {1} error code.".format(err_code, err_type.lower()))
            err_code = get_input("Please input the error code", poss_ans,\
                                 "Please enter an error code ({0})\nto get the error message, or type "\
                                    "'none' to continue with the troubleshooter.".format(err_types))
        # print out error, ask to exit
        if (err_code != 'none'):
            print("\nError {0}: {1}\n".format(err_code, err_codes[err_code]))
            answer1 = get_input("Would you like to continue with the troubleshooter? (y/n)",\
                                (lambda x : x in ['y','yes','n','no']),
                                "Please type either 'y'/'yes' or 'n'/'no' to proceed.")
            if (answer1.lower() in ['n','no']):
                print("Exiting troubleshooter...")
                print("================================================================================")
                return 1
    print("Continuing on with troubleshooter...")
    print("--------------------------------------------------------------------------------")
    return 0

# make specific for installation versus onboarding
def ask_install_error_codes():
    find_inst_err = "Installation error codes can be found by going through the command output in \n"\
                    "the terminal after running the `omsagent-*.universal.x64.sh` script to find \n"\
                    "a line that matches:\n"\
                    "\n    Shell bundle exiting with code <err>\n"
    return ask_error_codes('Installation', find_inst_err, "either an integer or 'NOT_DEFINED'")

def ask_onboarding_error_codes():
    find_onbd_err = "Onboarding error codes can be found by running the command:\n"\
                    "\n    echo $?\n\n"\
                    "directly after running the `/opt/microsoft/omsagent/bin/omsadmin.sh` tool."
    return ask_error_codes('Onboarding', find_onbd_err, "an integer")



# for getting inputs from the user
def get_input(question, check_ans, no_fit):
    answer = input(" {0}: ".format(question))
    while (not check_ans(answer.lower())):
        print("Unclear input. {0}".format(no_fit))
        answer = input(" {0}: ".format(question))
    return answer



# ask user if they want to reinstall OMS Agent
def ask_reinstall():
    answer = get_input("Would you like to uninstall and reinstall OMS Agent? (y/n)",\
                       (lambda x : x in ['y','yes','n','no']),\
                       "Please type either 'y'/'yes' or 'n'/'no' to proceed.")
    if (answer.lower() in ['y','yes']):
        print("Please run the command:")
        print("\n    sudo sh ./omsagent-*.universal.x64.sh --purge\n")
        print("to uninstall, and then run the command:")
        print("\n    sudo sh ./omsagent-*.universal.x64.sh --install\n")
        print("to reinstall.")
        return 1

    elif (answer.lower() in ['n','no']):
        print("Continuing on with troubleshooter...")
        print("--------------------------------------------------------------------------------")
        return 101

def ask_restart_oms():
    answer = get_input("Would you like to restart OMS Agent? (y/n)",\
                       (lambda x : x in ['y','yes','n','no']),\
                       "Please type either 'y'/'yes' or 'n'/'no' to proceed.")

    if (answer.lower() in ['y','yes']):
        print("Restarting OMS Agent...")
        sc_path = '/opt/microsoft/omsagent/bin/service_control'
        try:
            subprocess.check_output([sc_path, 'restart'], universal_newlines=True,\
                                    stderr=subprocess.STDOUT)
            return 0
        except subprocess.CalledProcessError:
            tsg_error_info.append(('executable shell script', sc_path))
            return 114

    elif (answer.lower() in ['n','no']):
        print("Continuing on with troubleshooter...")
        print("--------------------------------------------------------------------------------")
        return 101

def ask_continue():
    answer = get_input("Would you like to continue with the troubleshooter? (y/n)",\
                       (lambda x : x in ['y','yes','n','no']),\
                       "Please type either 'y'/'yes' or 'n'/'no' to proceed.")
    if (answer.lower() in ['y','yes']):
        print("Continuing on with troubleshooter...")
        print("--------------------------------------------------------------------------------")
        return 101
    elif (answer.lower() in ['n','no']):
        print("Exiting troubleshooter...")
        print("================================================================================")
        return 1



def print_errors(err_code, reinstall=False, restart_oms=False, continue_tsg=False):
    warning = False
    if (err_code == 1):
        return 1
    if (err_code == 125):
        warning = True

    err_string = tsg_error_codes[err_code]
    # no formatting
    if (tsg_error_info == []):
        err_string = "ERROR: {0}".format(err_string)
        err_summary.append(err_string)
        print(err_string)
    # needs input
    else:
        while (len(tsg_error_info) > 0):
            tup = tsg_error_info.pop(0)
            temp_err_string = err_string.format(*tup)
            if (warning):
                err_string = "WARNING: {0}".format(temp_err_string)
            else:
                err_string = "ERROR: {0}".format(temp_err_string)
            err_summary.append(err_string)
            print(err_string)

    if (warning):
        return 0
        
    if (restart_oms):
        return ask_restart_oms()
    elif (reinstall):
        return ask_reinstall()
    elif (continue_tsg):
        return ask_continue()
    else:
        return 101