import re
import subprocess
import urllib
import errno

from tsg_info       import tsg_info
from .tsg_checkpkgs import get_package_version

# backwards compatible input() function for Python 2 vs 3
try:
    input = raw_input
except NameError:
    pass

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
        print("Error: could not get OMSAgent Version.")
        return None
    return version



# get most recent OMS version released
def get_curr_oms_version():
    doc_file = urlopen("https://raw.github.com/microsoft/OMS-Agent-for-Linux/master/docs/OMS-Agent-for-Linux.md")
    for line in doc_file.readlines():
        line = line.decode('utf8')
        if line.startswith("omsagent | "):
            parsed_line = line.split(' | ') # [package, version, description]
            tsg_info['UPDATED_OMS_VERSION'] = parsed_line[1]
            return parsed_line[1]
    print("Error trying to get current released version.")
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



def print_old_version(oms_version):
    print("You are currently running OMS Version {0}. This troubleshooter only "\
          "supports versions 1.11 and newer. Please head to the Github link below "\
          "and click on 'Download Latest OMS Agent for Linux ({1})' in order to update "\
          "to the newest version:".format(oms_version, tsg_info['CPU_BITS']))
    print("https://github.com/microsoft/OMS-Agent-for-Linux")
    print("And follow the instructions given here:")
    print("https://github.com/microsoft/OMS-Agent-for-Linux/blob/master/docs"\
            "/OMS-Agent-for-Linux.md#upgrade-from-a-previous-release")

def ask_update_old_version(oms_version, curr_oms_version):
    print("You are currently running OMS Verion {0}. There is a newer version "\
          "available which may fix your issue (version {1}).".format(oms_version, curr_oms_version))
    answer = input("Do you want to update? (y/n): ")
    while (answer.lower() not in ['y','yes','n','no']):
    # unknown input, ask again
        print("Unclear input. Please type either 'y'/'yes' or 'n'/'no' to proceed.")
        answer = input("Do you want to update? (y/n): ")
    # user does want to update
    if (answer.lower() in ['y', 'yes']):
        print("Please head to the Github link below and click on 'Download "\
            "Latest OMS Agent for Linux ({0})' in order to update to the "\
            "newest version:".format(tsg_info['CPU_BITS']))
        print("https://github.com/microsoft/OMS-Agent-for-Linux")
        print("And follow the instructions given here:")
        print("https://github.com/microsoft/OMS-Agent-for-Linux/blob/master/"\
                "docs/OMS-Agent-for-Linux.md#upgrade-from-a-previous-release")
        return False
    # user doesn't want to update
    elif (answer.lower() in ['n', 'no']):
        print("Continuing on with troubleshooter...")
        return True



# update the dictionary with info in omsadmin.conf
def update_tsg_info():
    conf_path = "/etc/opt/microsoft/omsagent/conf/omsadmin.conf"
    try:
        with open(conf_path, 'r') as conf_file:
            for line in conf_file:
                parsed_line = (line.rstrip('\n')).split('=')
                tsg_info[parsed_line[0]] = parsed_line[1]
        return True
    except IOError as e:
        if (e.errno == errno.EACCES):
            print("Error: could not access file {0} due to inadequate permissions. "\
                  "Please run the troubleshooter as root in order to allow access "\
                  "to figure out the issue with OMS Agent.".format(conf_path))
            return False
        else:
            print("Error: could not access file {0}".format(conf_path))
            raise
        return False

# get value from omsadmin.conf information in tsg_info dict
def get_tsginfo_key(k):
    val = None
    try:
        val = tsg_info[k]
    except KeyError:
        if (not update_tsg_info()):
            return None
        val = tsg_info[k]
    if (val == ''):
        return None
    return val



def check_oms():
    oms_version = get_oms_version()
    if (oms_version == None):
        return False

    # check if version is >= 1.11
    if (not comp_versions_ge(oms_version, '1.11')):
        print_old_version(oms_version)
        return False

    # if not most updated version, ask if want to update
    curr_oms_version = get_curr_oms_version()
    if (curr_oms_version == None):
        return False

    if (not comp_versions_ge(oms_version, curr_oms_version)):
        return ask_update_old_version(oms_version, curr_oms_version)

    return update_tsg_info()