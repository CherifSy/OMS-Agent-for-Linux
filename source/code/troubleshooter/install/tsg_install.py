import os
import subprocess

from tsg_info        import update_pkg_manager
from tsg_errors      import tsg_error_info, get_input, print_errors
from .tsg_checkos    import check_os
from .tsg_checkoms   import check_oms
from .tsg_checkfiles import check_filesystem
from .tsg_checkpkgs  import check_packages



# get installation error codes
def get_install_err_codes():
    install_err_codes = {0 : "No errors found"}
    with open("files/Troubleshooting.md", 'r') as ts_doc:
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
    print("Installation error codes can be found by going through the command output in \n"\
          "the terminal to find a line that matches:")
    print("\n    Shell bundle exiting with code <err>\n")
    answer = get_input("Do you have an installation error code? (y/n)",\
                       (lambda x : x in ['y','yes','n','no']),\
                       "Please type either 'y'/'yes' or 'n'/'no' to proceed.")
    if (answer.lower() in ['y','yes']):
        install_err_codes = get_install_err_codes()
        poss_ans = lambda x : x in (list(install_err_codes.keys()) + ['none'])
        err_code = get_input("Please input the error code", poss_ans,\
                             "Please enter an error code (either an integer or 'NOT_DEFINED') \n"\
                                "to get the error message, or type 'none' to continue with "\
                                "the troubleshooter.")
        if (err_code != 'none'):
            print("\nError {0}: {1}\n".format(err_code, install_err_codes[err_code]))
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



# check space in MB for each main directory
def check_space():
    success = 0
    dirnames = ["/etc", "/opt", "/var"]
    for dirname in dirnames:
        space = os.statvfs(dirname)
        free_space = space.f_bavail * space.f_frsize / 1024 / 1024
        if (free_space < 500):
            tsg_error_info.append((dirname, free_space))
            success = 106
    return success



# check certificate
def check_cert():
    crt_path = "/etc/opt/microsoft/omsagent/certs/oms.crt"
    try:
        crt_info = subprocess.check_output(['openssl','x509','-in',crt_path,'-text','-noout'],\
                        universal_newlines=True, stderr=subprocess.STDOUT)
        if (crt_info.startswith("Certificate:\n")):
            return 0
        tsg_error_info.append((crt_path,))
        return 116
    except e:
        if (e == subprocess.CalledProcessError):
            err_msg = "Can't open {0} for reading, (\b+)".format(crt_path)
            match_err = re.match(err_msg, (e.split('\n'))[0])
            if (match_err != None):
                err = (match_err.groups())[0]
                # openssl permissions error
                if (err == "Permission denied"):
                    tsg_error_info.append((crt_path,))
                    return 100
                # openssl file existence error
                elif (err == "No such file or directory"):
                    tsg_error_info.append(("file", crt_path))
                    return 114
                # openssl some other error
                else:
                    tsg_error_info.append((crt_path, err))
                    return 123
            # catch-all in case of fluke error
            else:
                tsg_error_info.append((crt_path, e.output))
                return 123
        else:
            tsg_error_info.append((crt_path,))
            return 116



# check RSA private key
def check_key():
    key_path = "/etc/opt/microsoft/omsagent/certs/oms.key"
    key_info = subprocess.check_output(['openssl','rsa','-in',key_path,'-check'],\
                    universal_newlines=True, stderr=subprocess.STDOUT)
    # check if successful
    if ("RSA key ok\n" in key_info):
        return 0
    # check if file access error
    err_msg = "Can't open {0} for reading, (\b+)".format(key_path)
    match_err = re.match(err_msg, (key_info.split('\n'))[0])
    if (match_err != None):
        err = (match_err.groups())[0]
        # openssl permissions error
        if (err == "Permission denied"):
            tsg_error_info.append((key_path,))
            return 100
        # openssl file existence error
        elif (err == "No such file or directory"):
            tsg_error_info.append(("file", key_path))
            return 114
        # openssl some other error
        else:
            tsg_error_info.append((key_path, err))
            return 123
    # key error
    tsg_error_info.append((key_path,))
    return 117




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

    