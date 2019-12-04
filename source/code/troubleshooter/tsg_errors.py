import copy
import subprocess

# error info edited when error occurs
tsg_error_info = []



# dictionary correlating error codes to error messages
tsg_error_codes = {
    1   : "User requested to exit troubleshooter.",
    101 : "Please go through the output above to find the errors caught by the troubleshooter.",
    102 : "Couldn't get if CPU is 32-bit or 64-bit.",
    103 : "This version of {0} ({1}) is not supported. For {2} machines, please download {3}.",
    104 : "{0} is not supported.",
    105 : "There isn't enough space in directory {0} to install OMS - there needs to be at least 500MB free, "\
          "but {0} has {1}MB free. Please free up some space and try installing again.",
    106 : "This system does not have a supported package manager. Please install 'dpkg' or 'rpm' "\
          "and run this troubleshooter again.",
    107 : "OMSConfig isn't installed correctly.",
    108 : "OMI isn't installed correctly.",
    109 : "SCX isn't installed correctly.",
    110 : "OMS isn't installed correctly.",
    111 : "You are currently running OMS Version {0}. This troubleshooter only "\
          "supports versions 1.11 and newer. Please head to the Github link below "\
          "and click on 'Download Latest OMS Agent for Linux ({1})' in order to update "\
          "to the newest version:\n"\
          "https://github.com/microsoft/OMS-Agent-for-Linux\n"\
          "And follow the instructions given here:\n"\
          "https://github.com/microsoft/OMS-Agent-for-Linux/blob/master/docs"\
          "/OMS-Agent-for-Linux.md#upgrade-from-a-previous-release .",
    112 : "Couldn't get most current released version of OMS.",
    113 : "{0} {1} doesn't exist.",
    114 : "{0} {1} has {2} {3} instead of {2} {4}.",
    115 : "Certificate is invalid, please check {0} for the issue.",
    116 : "RSA key is invalid, please check {0} for the issue.",
    117 : "File {0} is empty.",
    118 : "Couldn't get {0}. Please check {1} for the issue.",
    119 : "Machine couldn't connect to {0}",
    120 : "The agent is configured to report to a different workspace - the GUID "\
          "given is {0}, while the workspace is {1}.",
    121 : "The agent isn't running / will not start.",
    122 : "Couldn't access file {0} due to the following reason: {1}.",
    123 : "At {0} {1} the agent logged this error: {2}. Please check out {3} for "\
          "more information.",
    124 : "At {0} {1} the agent logged this warning: {2}. Please check out {3} for "\
          "more information.",
    125 : "Heartbeats are failing to send data to the workspace.",
    126 : "Machine registered with more than one log analytics workspace. List of "\
          "workspaces: {0}",
    127 : "Machine is not connected to the internet."

}  # TODO: keep up to date with error codes onenote


# ask user if they want to reinstall OMS Agent
def ask_reinstall():
    answer = input(" Would you like to uninstall and reinstall OMS Agent to see if that fixes the \n"\
                   "issue you're having? (y/n): ")
    while (answer.lower() not in ['y','yes','n','no']):
        print(" Unclear input. Please type either 'y'/'yes' or 'n'/'no' to proceed.")
        answer = input(" Would you like to uninstall and reinstall OMS Agent to see if "\
                       "that fixes the \nissue you're having? (y/n): ")

    if (answer.lower() in ['y','yes']):
        print(" Please run the command:")
        print("    sudo sh ./omsagent-*.universal.x64.sh --purge")
        print(" to uninstall, and then run the command:")
        print("    sudo sh ./omsagent-*.universal.x64.sh --install")
        print(" to reinstall.")
        return 1

    elif (answer.lower() in ['n','no']):
        print(" Continuing on with troubleshooter...")
        return 101

def ask_restart_oms():
    answer = input(" Would you like to restart OMS Agent? (y/n): ")
    while (answer.lower() not in ['y','yes','n','no']):
        print(" Unclear input. Please type either 'y'/'yes' or 'n'/'no' to proceed.")
        answer = input(" Would you like to restart OMS Agent? (y/n): ")

    if (answer.lower() in ['y','yes']):
        print(" Restarting OMS Agent...")
        subprocess.Popen(['/opt/microsoft/omsagent/bin/service_control', 'restart'])
        return 0

    elif (answer.lower() in ['n','no']):
        print(" Continuing on with troubleshooter...")
        return 101


def print_errors(err_code, reinstall=True, restart_oms=False):
    err_string = tsg_error_codes[err_code]
    # no formatting
    if (tsg_error_info == []):
        print("ERROR: {0}".format(err_string))
    # needs input
    else:
        while (len(tsg_error_info) > 0):
            tup = tsg_error_info.pop(0)
            temp_err_string = err_string.format(*tup)
            print("ERROR: {0}".format(temp_err_string))

    if (restart_oms):
        return ask_restart_oms()
    elif (reinstall):
        return ask_reinstall()
    else:
        return 101