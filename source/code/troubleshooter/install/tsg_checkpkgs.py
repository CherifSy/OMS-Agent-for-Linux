import subprocess

from tsg_info import tsg_info

def get_dpkg_pkg_version(pkg):
    dpkg_info = subprocess.Popen(['dpkg', '-s', pkg], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)\
                    .communicate()[0].decode('utf-8')
    dpkg_lines = dpkg_info.split('\n')
    if ("package '{0}' is not installed".format(pkg) in dpkg_lines[0]):
        # didn't find package
        return None
    for line in dpkg_lines:
        if (line.startswith('Package: ') and not line.endswith(pkg)):
            # wrong package
            return None
        if (line.startswith('Status: ') and not line.endswith('installed')):
            # not properly installed
            return None
        if (line.startswith('Version: ')):
            version = (line.split())[-1]
            tsg_info['{0}_VERSION'.format(pkg.upper())] = version
            return version
    return None

def get_rpm_pkg_version(pkg):
    rpm_info = subprocess.Popen(['rpm', '-qi', pkg], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)\
                .communicate()[0].decode('utf-8')
    if ("package {0} is not installed".format(pkg) in rpm_info):
        # didn't find package
        return None
    rpm_lines = rpm_info.split('\n')
    for line in rpm_lines:
        if (line.startswith('Name') and not line.endswith(pkg)):
            # wrong package
            return None
        if (line.startswith('Version')):
            parsed_line = line.replace(' ','').split(':')  # ['Version', version]
            version = parsed_line[1]
            tsg_info['{0}_VERSION'.format(pkg.upper())] = version
            return version
    return None
            
def get_package_version(pkg):
    # dpkg
    if (tsg_info['INSTALLER'] == 'dpkg'):
        return get_dpkg_pkg_version(pkg)
    # rpm
    elif (tsg_info['INSTALLER'] == 'rpm'):
        return get_rpm_pkg_version(pkg)
    else:
        return None



# get current OMSConfig (DSC) version running on machine
def get_omsconfig_version():
    pkg_version = get_package_version('omsconfig')
    if (pkg_version == None):
        # couldn't find OMSConfig
        print("Error: could not get OMSConfig Version.")
        return None
    return pkg_version



# get current OMI version running on machine
def get_omi_version():
    pkg_version = get_package_version('omi')
    if (pkg_version == None):
        # couldn't find OMI
        print("Error: could not get OMI Version.")
        return None
    return pkg_version



# get current SCX version running on machine
def get_scx_version():
    pkg_version = get_package_version('scx')
    if (pkg_version == None):
        # couldn't find SCX
        print("Error: could not get SCX Version.")
        return None
    return pkg_version



# check to make sure all necessary packages are installed
def check_packages():
    if (get_omsconfig_version() == None):
        return False

    if (get_omi_version() == None):
        return False

    if (get_scx_version() == None):
        return False
    
    return True