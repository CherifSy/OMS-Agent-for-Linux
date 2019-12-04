import os
import subprocess

from tsg_info        import update_pkg_manager
from tsg_errors      import tsg_error_info, print_errors
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
    install_err_codes = {0 : "No errors found"}
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
    print("--------------------------------------------------------------------------------")
    answer = input(" Do you have an installation error code? (You can find it by going through the\n"\
                   " command output in the terminal to find a line that matches 'Shell bundle\n"\
                   " exiting with code <error code>' (y/n): ")
    while (answer.lower() not in ['y','yes','n','no']):
        print(" Unclear input. Please type either 'y'/'yes' or 'n'/'no' to proceed.")
        answer = input(" Do you have an installation error code? (y/n): ")
    if (answer.lower() in ['y','yes']):
        install_err_codes = get_install_err_codes()
        err_code = input(" Please input the error code: ")
        while (err_code not in list(install_err_codes.keys())):
            if (err_code == 'none'):
                break
            print(" Unclear input. Please enter an error code (either an integer or 'NOT_DEFINED')\n"\
                  " to get the error message, or type 'none' to continue with the troubleshooter.")
            err_code = input(" Please input the error code: ")
        if (err_code != 'none'):
            print(" Error {0}: {1}".format(err_code, install_err_codes[err_code]))
            answer1 = input(" Would you like to continue with the troubleshooter? (y/n): ")
            while (answer1.lower() not in ['y','yes','n','no']):
                print(" Unclear input. Please type either 'y'/'yes' or 'n'/'no' to proceed.")
                answer1 = input(" Would you like to continue with the troubleshooter? (y/n): ")
            if (answer1.lower() in ['n','no']):
                print("Exiting troubleshooter...")
                return 1
    print(" Continuing on with troubleshooter...")
    return 0



# check space in MB for each main directory
def check_space():
    success = 0
    dirnames = ["/etc", "/opt", "/var"]
    for dirname in dirnames:
        space = os.statvfs(dirname)
        free_space = space.f_bavail * space.f_frsize / 1024 / 1024
        if (free_space < 500):
            tsg_error_info.append((dirname, free_space))
            success = 105
    return success



# check certificate
def check_cert():
    crt_path = "/etc/opt/microsoft/omsagent/certs/oms.crt"
    try:
        crt_info = subprocess.Popen(['openssl', 'x509', '-in', crt_path, '-text', '-noout'], stdout=subprocess.PIPE, \
                    stderr=subprocess.STDOUT).communicate()[0].decode('utf8')
        if (crt_info.startswith("Certificate:\n")):
            return 0
        tsg_error_info.append((crt_path,))
        return 115
    except IOError as e:
        if (e.errno == errno.EACCES):
            # permissions error, needs to be run as sudo
            tsg_error_info.append((crt_path,))
            return 100
        else:
            raise

# check RSA private key
def check_key():
    key_path = "/etc/opt/microsoft/omsagent/certs/oms.key"
    try:
        key_info = subprocess.Popen(['openssl', 'rsa', '-in', key_path, '-check'], stdout=subprocess.PIPE, \
                    stderr=subprocess.STDOUT).communicate()[0].decode('utf8')
        if ("RSA key ok\n" in key_info):
            return 0
        tsg_error_info.append((key_path,))
        return 116
    except IOError as e:
        if (e.errno == errno.EACCES):
            # permissions error, needs to be run as sudo
            tsg_error_info.append((key_path,))
            return 100
        else:
            raise




# check all packages are installed
def check_installation(err_codes=True):
    print("CHECKING INSTALLATION...")
    # keep track of if all tests have been successful
    success = 0
    
    if (err_codes):
        if (ask_install_error_codes() == 1):
            return 1

    # check OS
    print("Checking if running a supported OS version...")
    checked_os = check_os()
    if (checked_os != 0):
        return print_errors(checked_os, reinstall=False)
    
    # check space available
    print("Checking if enough disk space is available...")
    checked_space = check_space()
    if (checked_space != 0):
        return print_errors(checked_space, reinstall=False)

    # check package manager
    print("Checking if machine has a supported package manager...")
    checked_pkg_manager = update_pkg_manager()
    if (checked_pkg_manager != 0):
        return print_errors(checked_pkg_manager, reinstall=False)
    
    # check packages are installed
    print("Checking if packages installed correctly...")
    checked_packages = check_packages()
    if (checked_packages != 0):
        if (print_errors(checked_packages) == 1):
            return 1
        else:
            success = 101

    # check OMS version
    print("Checking if running a supported version of OMS...")
    checked_oms = check_oms()
    if (checked_oms != 0):
        if (print_errors(checked_oms) == 1):
            return 1
        else:
            success = 101

    # check all files
    print("Checking if all files installed correctly (may take some time)...")
    checked_files = check_filesystem()
    if (checked_files != 0):
        if (print_errors(checked_files) == 1):
            return 1
        else:
            success = 101

    # check certs
    print("Checking certificate and RSA key are correct...")
    checked_cert = check_cert()
    if (checked_cert != 0):
        if (print_errors(checked_cert) == 1):
            return 1
        else:
            success = 101
    checked_key = check_key()
    if (checked_key != 0):
        if (print_errors(checked_key) == 1):
            return 1
        else:
            success = 101
    
    return success

    