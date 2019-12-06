import re
import urllib

from tsg_info                import tsg_info, update_omsadmin
from tsg_errors              import tsg_error_info, get_input, print_errors
from connect.tsg_checkendpts import check_internet_connect
from .tsg_checkpkgs          import get_package_version

# urlopen() in different packages in Python 2 vs 3
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen



# get current OMS version running on machine
def get_oms_version():
    version = get_package_version('omsagent')
    # couldn't find OMSAgent
    if (version == None):
        return None
    return version



# get most recent OMS version released
def get_curr_oms_version():
    try:
        doc_file = urlopen("https://raw.github.com/microsoft/OMS-Agent-for-Linux/master/docs/OMS-Agent-for-Linux.md")
        for line in doc_file.readlines():
            line = line.decode('utf8')
            if line.startswith("omsagent | "):
                parsed_line = line.split(' | ') # [package, version, description]
                tsg_info['UPDATED_OMS_VERSION'] = parsed_line[1]
                return parsed_line[1]
        return None
    except IOError:
        checked_internet = check_internet_connect()
        if (checked_internet != 0):
            print_errors(checked_internet, reinstall=False)
        else:
            print_errors(119, reinstall=False)
        return None



# compare two versions, see if the first is newer than / the same as the second
def comp_versions_ge(v1, v2):
    # split on '.' and '-'
    v1_split = v1.split('.|-')
    v2_split = v2.split('.|-')
    # get rid of trailing zeroes (e.g. 1.12.0 is the same as 1.12)
    while (v1_split[-1] == '0'):
        v1_split = v1_split[:-1]
    while (v2_split[-1] == '0'):
        v2_split = v2_split[:-1]
    # iterate through version elements
    for (v1_elt, v2_elt) in (zip(v1_split, v2_split)):
        # curr version elements are same
        if (v1_elt == v2_elt):
            continue
        try:
            # parse as integers
            return (int(v1_elt) >= int(v2_elt))
        except:
            # contains wild card characters
            if ((v1_elt in ['x','X','*']) or (v2_elt in ['x','X','*'])):
                return True
            # remove non-numeric characters, try again
            v1_nums = [int(n) for n in re.findall('\d+', v1_elt)]
            v2_nums = [int(n) for n in re.findall('\d+', v2_elt)]
            return all([(i>=j) for i,j in zip(v1_nums, v2_nums)])
    # check if subversion is newer (e.g. 1.11.3 to 1.11)
    return (len(v1_split) >= len(v2_split))



def ask_update_old_version(oms_version, curr_oms_version):
    print("--------------------------------------------------------------------------------")
    print("You are currently running OMS Verion {0}. There is a newer version\n"\
          "available which may fix your issue (version {1}).".format(oms_version, curr_oms_version))
    answer = get_input("Do you want to update? (y/n)", ['y','yes','n','no'],\
                       "Please type either 'y'/'yes' or 'n'/'no' to proceed.")
    # user does want to update
    if (answer.lower() in ['y', 'yes']):
        print("Please head to the Github link below and click on 'Download Latest OMS Agent\n"\
              "for Linux ({0})' in order to update to the newest version:".format(tsg_info['CPU_BITS']))
        print("\n    https://github.com/microsoft/OMS-Agent-for-Linux\n")
        print("And follow the instructions given here:")
        print("\n    https://github.com/microsoft/OMS-Agent-for-Linux/blob/master/docs/"\
                "OMS-Agent-for-Linux.md#upgrade-from-a-previous-release\n")
        return 1
    # user doesn't want to update
    elif (answer.lower() in ['n', 'no']):
        print("Continuing on with troubleshooter...")
        print("--------------------------------------------------------------------------------")
        return 0



def check_oms():
    oms_version = get_oms_version()
    if (oms_version == None):
        return 110

    # check if version is >= 1.11
    if (not comp_versions_ge(oms_version, '1.11')):
        tsg_error_info.append((oms_version, tsg_info['CPU_BITS']))
        return 111

    # if not most updated version, ask if want to update
    curr_oms_version = get_curr_oms_version()
    if (curr_oms_version == None):
        return 112

    if (not comp_versions_ge(oms_version, curr_oms_version)):
        if (ask_update_old_version(oms_version, curr_oms_version) == 1):
            return 1

    return update_omsadmin()