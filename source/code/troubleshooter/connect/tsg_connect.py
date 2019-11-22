from install.tsg_install  import check_installation
from install.tsg_checkoms import get_oms_version

# backwards compatible input() function for Python 2 vs 3
try:
    input = raw_input
except NameError:
    pass



# get onboarding error codes
def get_onboarding_err_codes():
    onboarding_err_codes = dict()
    with open("install/files/Troubleshooting.md", 'r') as ts_doc:
        section = None
        for line in ts_doc:
            line = line.rstrip('\n')
            if (line == ''):
                continue
            if (line.startswith('##')):
                section = line[3:]
                continue
            if (section == 'Onboarding Error Codes'):
                parsed_line = list(map(lambda x : x.strip(' '), line.split('|')))[1:-1]
                if (parsed_line[0] in ['Error Code', '---']):
                    continue
                onboarding_err_codes[parsed_line[0]] = parsed_line[1]
                continue
            if (section=='Onboarding Error Codes' and line.startswith('#')):
                break
    return install_err_codes

# ask if user has seen onboarding error code
def ask_onboarding_error_codes():
    answer = input("Do you have an onboarding error code? (y/n): ")
    # TODO: add smth about where / how to see if user encountered error code in onboarding
    while (answer.lower() not in ['y','yes','n','no']):
        print("Unclear input. Please type either 'y'/'yes' or 'n'/'no' to proceed.")
        answer = input("Do you have an onboarding error code? (y/n): ")
    if (answer.lower() in ['y','yes']):
        onboarding_err_codes = get_onboarding_err_codes()
        err_code = input("Please input the error code: ")
        while (err_code not in list(onboarding_err_codes.keys())):
            if (err_code == 'none'):
                break
            print("Unclear input. Please enter an error code (an integer) to get "\
                  "the error message, or type 'none' to continue with the troubleshooter.")
            err_code = input("Please input the error code: ")
        if (err_code != 'none'):
            print("Error {0}: {1}".format(err_code, onboarding_err_codes[err_code]))
            answer1 = input("Would you like to continue with the troubleshooter? (y/n): ")
            while (answer1.lower() not in ['y','yes','n','no']):
                print("Unclear input. Please type either 'y'/'yes' or 'n'/'no' to proceed.")
                answer1 = input("Would you like to continue with the troubleshooter? (y/n): ")
            if (answer1.lower() in ['n','no']):
                print("Exiting troubleshooter...")
                return False
    print("Continuing on with troubleshooter...")
    return True



# Verify omsadmin.conf exists / not empty
def check_omsadmin():
    omsadmin_path = "opt/microsoft/omsagent/bin/omsadmin.sh"
    try:
        with open(omsadmin_path) as omsadmin_file:
            if (omsadmin_file == ""):
                print("Error: file {0} is empty. Running the installation part of "\
                      "the troubleshooter in order to find the issue...".format(omsadmin_path))
                # TODO: copy contents into it upon asking?
                return False
            return True
    except IOError:
        print("Error: the file {0} doesn't exist. Running the installation part of "\
              "the troubleshooter in order to find the issue...".format(omsadmin_path))
        return False
            


# Ping OMS endpt (verify_e2e.py)
def ping_oms_endpt():
    return True



# Check workspace ID and status
# Verify omsagent is running (ps aux | grep omsagent)



def check_connection():
    success = True

    # check if installed correctly
    print("Checking if installed correctly...")
    if (get_oms_version() == None):
        print("Error: OMS is not installed successfully. Running the installation "\
              "part of the troubleshooter in order to find the issue...")
        return check_installation(err_codes=False)

    # check omsadmin.conf
    if (not check_omsadmin()):
        return check_installation(err_codes=False)

    
