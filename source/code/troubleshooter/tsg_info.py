import errno
import subprocess

from tsg_errors import tsg_error_info, print_errors

tsg_info = dict()

def tsginfo_lookup(key):
    try:
        val = tsg_info[key]
    except KeyError:
        updated_tsginfo = update_tsginfo_all()
        if (updated_tsginfo != 0):
            print_errors(updated_tsginfo, reinstall=False)
            return None
        val = tsg_info[key]
    if (val == ''):
        return None
    return val

# All functions that update tsg_info

# CPU Bits
def get_os_bits():
    cpu_info = subprocess.Popen('lscpu', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)\
                .communicate()[0].decode('utf-8')
    cpu_opmodes = (cpu_info.split('\n'))[1]
    cpu_bits = cpu_opmodes[-6:]
    tsg_info['CPU_BITS'] = cpu_bits
    return cpu_bits

# OS Info
def update_os_version():
    os_path = '/etc/os-release'
    try:
        with open(os_path, 'r') as os_file:
            for line in os_file:
                line = line.replace('"', '')
                info = line.split('=')
                tsg_info['OS_' + (info[0])] = (info[1]).rstrip('\n')
        return 0
    except IOError as e:
        if (e.errno == errno.EACCES):
            tsg_error_info.append((os_path,))
            return 100
        elif (e.errno == errno.ENOENT):
            tsg_error_info.append(('file', os_path))
            return 113
        else:
            raise

# Package Manager
def update_pkg_manager():
    is_dpkg = subprocess.Popen(['which', 'dpkg'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)\
                .communicate()[0].decode('utf8')
    if (is_dpkg != ''):
        tsg_info['PKG_MANAGER'] = 'dpkg'
        return 0
    is_rpm = subprocess.Popen(['which', 'rpm'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)\
                .communicate()[0].decode('utf8')
    if (is_rpm != ''):
        tsg_info['PKG_MANAGER'] = 'rpm'
        return 0
    # neither
    return 106

# Package Info
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

# omsadmin.conf
def update_omsadmin():
    conf_path = "/etc/opt/microsoft/omsagent/conf/omsadmin.conf"
    try:
        with open(conf_path, 'r') as conf_file:
            for line in conf_file:
                parsed_line = (line.rstrip('\n')).split('=')
                tsg_info[parsed_line[0]] = '='.join(parsed_line[1:])
        return 0
    except IOError as e:
        if (e.errno == errno.EACCES):
            tsg_error_info.append((conf_path,))
            return 100
        elif (e.errno == errno.ENOENT):
            tsg_error_info.append(('file', os_path))
            return 113
        else:
            raise



# update all
def update_tsginfo_all():
    # cpu_bits
    bits = get_os_bits()
    if (bits not in ['32-bit', '64-bit']):
        return 102
    # os info
    os = update_os_version()
    if (os != 0):
        return os
    # package manager
    pkg = update_pkg_manager()
    if (pkg != 0):
        return pkg
    # dpkg packages
    if (tsg_info['PKG_MANAGER'] == 'dpkg'):
        if (get_dpkg_pkg_version('omsconfig') == None):
            return 107
        if (get_dpkg_pkg_version('omi') == None):
            return 108
        if (get_dpkg_pkg_version('scx') == None):
            return 109
        if (get_dpkg_pkg_version('omsagent') == None):
            return 110
    # rpm packages
    elif (tsg_info['PKG_MANAGER'] == 'rpm'):
        if (get_rpm_pkg_version('omsconfig') == None):
            return 107
        if (get_rpm_pkg_version('omi') == None):
            return 108
        if (get_rpm_pkg_version('scx') == None):
            return 109
        if (get_rpm_pkg_version('omsagent') == None):
            return 110
    # omsadmin info
    omsadmin = update_omsadmin()
    if (omsadmin != 0):
        return omsadmin
    # all successful
    return 0