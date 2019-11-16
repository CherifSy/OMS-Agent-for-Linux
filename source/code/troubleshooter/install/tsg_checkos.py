from __future__ import print_function

import copy
import os
import subprocess

from .tsg_install_info import install_info



# dictionary to convert pretty name to ID for OS system
name_to_id = {'CentOS':'centos', 'Amazon Linux':'amzn', 'Oracle Linux':'ol', 
              'Red Hat Enterprise Linux Server':'rhel', 'Debian GNU/Linux':'debian', 
              'Ubuntu Linux':'ubuntu', 'SUSE Linux Enterprise Server':'sles'}

# create dictionaries for all supported Operating Systems
supported_32bit = dict()
supported_64bit = dict()

# check if version number
def is_number(s):
  try:
    int(s)
    return True
  except ValueError:
    try:
      float(s)
      return True
    except ValueError:
      return False

# grab all supported OS from README.md
def get_supported_versions():
    current_bits = None
    with open("install/files/README.md") as f:
        for line in f:
            # check if we're in the right section
            if (line == "### 64-bit\n"):
                current_bits = '64-bit'
                continue
            elif (line == "### 32-bit\n"):
                current_bits = '32-bit'
                continue
            elif (line == "\n"):
                current_bits = None
                continue

            # skip over all lines that aren't the right section
            if (current_bits == None):
                continue

            # parse line to get supported versions (get rid of commas)
            parsed_line = [word.rstrip(',') for word in (line.split()[1:])]
            # iterate through name until we reach versions
            name = parsed_line[0]
            i = 1
            while (not is_number(parsed_line[i])):
                name += (' ' + parsed_line[i])
                i += 1
            supp_versions = list(filter(is_number, parsed_line[i:]))

            id_name = name_to_id[name]
            if (current_bits == '64-bit'):
                supported_64bit[id_name] = supp_versions
            elif (current_bits == '32-bit'):
                supported_32bit[id_name] = supp_versions



# get if machine is 32 bit or 64 bit
def get_os_bits():
    cpu_info = subprocess.Popen('lscpu', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)\
                .communicate()[0].decode('utf-8')
    cpu_opmodes = (cpu_info.split('\n'))[1]
    cpu_bits = cpu_opmodes[-6:]
    install_info['CPU_BITS'] = cpu_bits
    return cpu_bits


# put all info from os-release in dictionary for lookup
def get_os_version():
    with open("/etc/os-release", 'r') as os_file:
        for line in os_file:
            line = line.replace('"', '')
            info = line.split('=')
            install_info['OS_' + (info[0])] = (info[1]).rstrip('\n')


# print out warning if running the wrong version of OS system
def print_wrong_version(cpu_bits):
    print("This version of {0} ({1}) is not supported. For {2} machines, please download " \
          "{0} ".format(install_info['OS_NAME'], install_info['OS_PRETTY_NAME'], cpu_bits), \
          end='')
    versions = None
    if (cpu_bits == '32-bit'):
        versions = copy.deepcopy(supported_32bit[install_info['OS_ID']])
    elif (cpu_bits == '64-bit'):
        versions = copy.deepcopy(supported_64bit[install_info['OS_ID']])
    last = versions.pop()
    if (versions == []):
        print("{0}.".format(last))
    else:
        print("{0} or {1}.".format(', '.join(versions), last))
    
    
# check version of OS
def check_os_version(cpu_bits):
    if ((cpu_bits == '32-bit') and (install_info['OS_ID'] in supported_32bit.keys())):
        if (install_info['OS_VERSION_ID'] in supported_32bit[install_info['OS_ID']]):
            return True
        else:
            print_wrong_version(cpu_bits)
            return False
    elif ((cpu_bits == '64-bit') and (install_info['OS_ID'] in supported_64bit.keys())):
        if (install_info['OS_VERSION_ID'] in supported_64bit[install_info['OS_ID']]):
            return True
        else:
            print_wrong_version(cpu_bits)
            return False
    else:
        print("{0} is not supported.".format(install_info['OS_PRETTY_NAME']))
        return False
    



# check if running supported OS/version
def check_os():
    # fill dictionaries with supported versions
    get_supported_versions()

    # 32 bit or 64 bit
    cpu_bits = get_os_bits()
    if (cpu_bits == None or (cpu_bits not in ['32-bit', '64-bit'])):
        print("Error getting if CPU is 32-bit or 64-bit.")
        return False

    # get OS version info
    get_os_version()

    # check OS version
    return check_os_version(cpu_bits)