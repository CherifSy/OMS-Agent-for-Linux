import os
import subprocess

from tsg_info        import tsg_info
from .tsg_checkos    import check_os
from .tsg_checkoms   import check_oms
from .tsg_checkfiles import check_filesystem
from .tsg_checkpkgs  import check_packages

# backwards compatible input() function for Python 2 vs 3
try:
    input = raw_input
except NameError:
    pass



# get installation error codes
def get_install_err_codes():
    install_err_codes = dict()
    with open("install/files/Troubleshooting.md", 'r') as ts_doc:
        section = None
        for line in ts_doc:
            line = line.rstrip('\n')
            if (line == ''):
                continue
            if (line.startswith('##')):
                section = line[3:]
                continue
            if (section == 'Installation Error Codes'):
                parsed_line = list(map(lambda x : x.strip(' '), line.split('|')))[1:-1]
                if (parsed_line[0] in ['Error Code', '---']):
                    continue
                install_err_codes[parsed_line[0]] = parsed_line[1]
                continue
            if (section == 'Onboarding Error Codes'):
                break
    return install_err_codes

# ask if user has seen installation error code
def ask_install_error_codes():
    answer = input("Do you have an installation error code? (y/n): ")
    # TODO: add smth about where / how to see if user encountered error code in installation
    while (answer.lower() not in ['y','yes','n','no']):
        print("Unclear input. Please type either 'y'/'yes' or 'n'/'no' to proceed.")
        answer = input("Do you have an installation error code? (y/n): ")
    if (answer.lower() in ['y','yes']):
        install_err_codes = get_install_err_codes()
        err_code = input("Please input the error code: ")
        while (err_code not in list(install_err_codes.keys())):
            if (err_code == 'none'):
                break
            print("Unclear input. Please enter an error code (either an integer "\
                  "or 'NOT_DEFINED') to get the error message, or type 'none' to "\
                  "continue with the troubleshooter.")
            err_code = input("Please input the error code: ")
        if (err_code != 'none'):
            print("Error {0}: {1}".format(err_code, install_err_codes[err_code]))
            answer1 = input("Would you like to continue with the troubleshooter? (y/n): ")
            while (answer1.lower() not in ['y','yes','n','no']):
                print("Unclear input. Please type either 'y'/'yes' or 'n'/'no' to proceed.")
                answer1 = input("Would you like to continue with the troubleshooter? (y/n): ")
            if (answer1.lower() in ['n','no']):
                print("Exiting troubleshooter...")
                return False
    print("Continuing on with troubleshooter...")
    return True



# check which installer the machine is using
def check_pkg_manager():
    is_dpkg = subprocess.Popen(['which', 'dpkg'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)\
                .communicate()[0].decode('utf8')
    if (is_dpkg != ''):
        tsg_info['INSTALLER'] = 'dpkg'
        return True
    is_rpm = subprocess.Popen(['which', 'rpm'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)\
                .communicate()[0].decode('utf8')
    if (is_rpm != ''):
        tsg_info['INSTALLER'] = 'rpm'
        return True
    print("Error: this system does not have a supported package manager. Please install "\
          "'dpkg' or 'rpm' and run this troubleshooter again.")
    return False



# check space in MB for each main directory
def check_space():
    success = True
    dirnames = ["/etc", "/opt", "/var"]
    for dirname in dirnames:
        space = os.statvfs(dirname)
        free_space = space.f_bavail * space.f_frsize / 1024 / 1024
        if (free_space < 500):
            print("Error: directory {0} doesn't have enough space to install OMS. "\
                  "Please free up some space and try installing again.".format(dirname))
            success = False
    return success



# ask user if they want to reinstall OMS Agent
def ask_reinstall():
    answer = input("Would you like to uninstall and reinstall OMS Agent to see if "\
                   "that fixes the issue you're having? (y/n): ")
    while (answer.lower() not in ['y','yes','n','no']):
        print("Unclear input. Please type either 'y'/'yes' or 'n'/'no' to proceed.")
        answer = input("Would you like to uninstall and reinstall OMS Agent to see if "\
                   "that fixes the issue you're having? (y/n): ")
    if (answer.lower() in ['y','yes']):
        print("Please run the command `sudo sh ./omsagent-*.universal.x64.sh --purge` to "\
              "uninstall, and `sudo sh ./omsagent-*.universal.x64.sh --install` to reinstall.")
        return False
    elif (answer.lower() in ['n','no']):
        print("Continuing on with troubleshooter...")
        return True



# check certificate
def check_cert():
    crt_path = "/etc/opt/microsoft/omsagent/certs/oms.crt"
    try:
        crt_info = subprocess.Popen(['openssl', 'x509', '-in', crt_path, '-text', '-noout'], stdout=subprocess.PIPE, \
                    stderr=subprocess.STDOUT).communicate()[0].decode('utf8')
        if (crt_info.startswith("Certificate:\n")):
            return True
        print("Error: Certificate is invalid, please check {0} for the issue.".format(crt_path))
        return False
    except IOError as e:
        if (e.errno == errno.EACCES):
            # permissions error, needs to be run as sudo
            print("Error: could not access file {0} due to inadequate permissions. "\
                  "Please run the troubleshooter as root in order to allow access "\
                  "to figure out the issue with OMS Agent.".format(crt_path))
            return False
        else:
            print("Error: could not access file {0}".format(crt_path))
            raise
        return False

# check RSA private key
def check_key():
    key_path = "/etc/opt/microsoft/omsagent/certs/oms.key"
    try:
        key_info = subprocess.Popen(['openssl', 'rsa', '-in', key_path, '-check'], stdout=subprocess.PIPE, \
                    stderr=subprocess.STDOUT).communicate()[0].decode('utf8')
        if ("RSA key ok\n" in key_info):
            return True
        print("Error: RSA key is invalid, plese check {0} for the issue.".format(key_path))
        return False
    except IOError as e:
        if (e.errno == errno.EACCES):
            # permissions error, needs to be run as sudo
            print("Error: could not access file {0} due to inadequate permissions. "\
                  "Please run the troubleshooter as root in order to allow access "\
                  "to figure out the issue with OMS Agent.".format(key_path))
            return False
        else:
            print("Error: could not access file {0}".format(key_path))
            raise
        return False




# check all packages are installed
def check_installation(err_codes=True):
    success = True

    if (err_codes):
        if (not ask_install_error_codes()):
            return False

    # check OS
    print("Checking if running a supported OS version...")
    if (not check_os()):
        return False
    
    # check space available
    print("Checking if enough disk space is available...")
    if (not check_space()):
        return False

    # check package manager
    print("Checking if machine has a supported package manager...")
    if (not check_pkg_manager()):
        return False
    
    # check packages are installed
    print("Checking packages installed correctly...")
    if (not check_packages()):
        if (ask_reinstall()):
            success = False
        else:
            return False

    # check OMS version
    print("Checking if running a supported version of OMS...")
    if (not check_oms()):
        if (ask_reinstall()):
            success = False
        else:
            return False

    # check all files
    print("Checking all files installed correctly (may take some time)...")
    if (not check_filesystem()):
        if (ask_reinstall()):
            success = False
        else:
            return False

    # check certs
    print("Checking certificate and RSA key are correct...")
    if (not check_cert()):
        if (ask_reinstall()):
            success = False
        else:
            return False
    if (not check_key()):
        if (ask_reinstall()):
            success = False
        else:
            return False
    
    if (success):
        print("Couldn't find any errors in the install process.")
        return True
    else:
        print("One or more errors found in the install process. Please go through "\
            "the error messages above to help find the issue.")

    