import os
import re
import subprocess

from .tsg_install_info import install_info
from .tsg_checkoms     import comp_versions_ge



# get files/directories/links from data files

def get_data(f, variables, files, links, dirs):
    curr_section = None
    with open(f, 'r') as data_file:
        for line in data_file:
            line = line.rstrip('\n')
            # skip comments
            cstart = line.find('#')
            if (cstart != -1):
                line = line[:cstart]

            # skip empty lines
            if (line == ''):
                continue            

            # new section
            if (line.startswith('%')):
                curr_section = line[1:]
                continue

            # line contains variable, needs to be replaced with content
            while ('${{' in line):
                vstart = line.index('${{')
                vend = line.index('}}') + 2
                l = line[vstart:vend]
                v = line[vstart+3:vend-2]
                if (v in list(variables.keys())):
                    line = line.replace(l, variables[v])
                else:
                    break

            # variable line
            if (curr_section == "Variables"):
                # parsed_line: [variable name, content]
                parsed_line = (line.replace(' ','')).split(':')
                variables[parsed_line[0]] = (parsed_line[1]).strip("'")
                continue

            # dependencies line
            elif (curr_section == "Dependencies"):
                pass
                # go through dependencies, make sure that currently running the version that works with it

            # file line
            elif (curr_section == "Files"):
                # parsed_line: [filepath, install filepath, permissions, user, group]
                parsed_line = (line.replace(' ','')).split(';')
                files[parsed_line[0]] = parsed_line[2:5]
                continue

            # link line
            elif (curr_section == "Links"):
                # parsed_line: [filepath, install filepath, permissions, user, group]
                parsed_line = (line.replace(' ','')).split(';')
                links[parsed_line[0]] = parsed_line[2:5] + [parsed_line[1]]
                continue

            # directory line
            elif (curr_section == "Directories"):
                # parsed_line: [filepath, permissions, user, group]
                parsed_line = (line.replace(' ','')).split(';')
                dirs[parsed_line[0]] = parsed_line[1:4]
                continue

            # installation code
            else:
                # check for changes in owners or permissions
                if (line.startswith('chmod ')):
                    # parsed_line: ['chmod', (recursive,) new permissions, filepath]
                    parsed_line = line.split()
                    path = parsed_line[-1]
                    # skip over anything with undefined variables
                    if (not path.startswith('/')):
                        continue
                    new_perms = parsed_line[-2]
                    if (parsed_line[1] == '-R'):
                        # recursively apply new perms
                        for f in (files.keys()):
                            if (f.startswith(path)):
                                files[f][0] = new_perms
                        for l in (links.keys()):
                            if (l.startswith(path)):
                                links[l][0] = new_perms
                        for d in (dirs.keys()):
                            if (d.startswith(path)):
                                dirs[d][0]  = new_perms
                    else: # not recursive
                        if path in files:
                            files[path][0] = new_perms
                        elif path in links:
                            links[path][0] = new_perms
                        elif path in dirs:
                            dirs[path][0]  = new_perms




# Convert between octal permission and symbolic permission
def perm_oct_to_symb(p):
    binstr = ''
    for i in range(3):
        binstr += format(int(p[i]), '03b')
    symbstr = 'rwxrwxrwx'
    result = ''
    for j in range(9):
        if (binstr[j] == '0'):
            result += '-'
        else:
            result += symbstr[j]
    return result

def perm_symb_to_oct(p):
    binstr = ''
    for i in range(9):
        if (p[i] == '-'):
            binstr += '0'
        else:
            binstr += '1'
    result = ''
    for j in range(0,9,3):
        result += str(int(binstr[j:j+3], 2))
    return result



# Check permissions are correct for each file
# info: [permissions, user, group]
def check_permissions(f, perm_info, corr_info, typ):
    success = True
    # check user
    perm_user = perm_info[1]
    corr_user = corr_info[1]
    if ((perm_user != corr_user) and (perm_user != 'omsagent')):
        print("Error: {0} {1} has user {2} instead of user "\
              "{3}.".format(typ, f, perm_user, corr_user))
        success = False
    
    # check group
    perm_group = perm_info[2]
    corr_group = corr_info[2]
    if ((perm_group != corr_group) and (perm_group != 'omiusers')):
        print("Error: {0} {1} has group {2} instead of group "\
              "{3}.".format(typ, f, perm_group, corr_group))
        success = False
    
    # check permissions
    perms = (perm_info[0])[1:]
    corr_perms = perm_oct_to_symb(corr_info[0])
    if (perms != corr_perms):
        print("Error: {0} {1} has permissions {2} instead of permissions "\
              "{3}.".format(typ, f, perms, corr_perms))
        success = False
    return success



# CHECK WORKSPACE ID STUFF / FILES TO MAKE SURE THEY HAVE CORR PERMS OF OMSAGENT AND OMIUSERS
    


# Check directories exist

def get_ll_dir(ll_output, d):
    ll_lines = ll_output.split('\n')
    d_end = os.path.basename(d)
    ll_line = list(filter(lambda x : x.endswith(' ' + d_end), ll_lines))[0]
    return ll_line.split()

def check_dirs(dirs):
    success = True
    missing_dirs = []
    for d in (dirs.keys()):
        if (any(d.startswith(md) for md in missing_dirs)):
            # parent folder doesn't exist, skip checking child folder
            continue
        # check if folder exists
        elif (not os.path.isdir(d)):
            print("Error: directory {0} does not exist.".format(d))
            missing_dirs += d
            success = False
            continue
        # check if permissions are correct
        try:
            # get permissions
            ll_output = subprocess.Popen(['ls', '-l', os.path.join(d, '..')], stdout=subprocess.PIPE, \
                            stderr=subprocess.STDOUT).communicate()[0].decode('utf-8')
            # ll_info: [perms, items, user, group, size, month mod, day mod, time mod, name]
            ll_info = get_ll_dir(ll_output, d)
            perm_info = [ll_info[0]] + ll_info[2:4]
            corr_info = dirs[d]
            if (not check_permissions(d, perm_info, corr_info, "directory")):
                success = False
            continue
        except:
            print("Error with trying to check permissions for directory {0}.".format(d))
            raise
            success = False
            continue
    return success



# Check files exist

def check_files(files):
    success = True
    for f in (files.keys()):
        # check if file exists
        if (not os.path.isfile(f)):
            print("Error: file {0} does not exist.".format(f))
            success = False
            continue
        # check if permissions are correct
        try:
            # get permissions
            ll_output = subprocess.Popen(['ls', '-l', f], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)\
                            .communicate()[0].decode('utf-8')
            # ll_info: [perms, items, user, group, size, month mod, day mod, time mod, name]
            ll_info = ll_output.split()
            perm_info = [ll_info[0]] + ll_info[2:4]
            corr_info = files[f]
            if (not check_permissions(f, perm_info, corr_info, "file")):
                success = False
            continue
        except:
            print("Error with trying to check permissions for file {0}.".format(f))
            raise
            success = False
            continue
    return success

            



# Check links exist

def check_links(links):
    success = True
    for l in (links.keys()):
        # check if link exists
        if (not os.path.islink(l)):
            print("Error: link {0} does not exist.".format(l))
            success = False
            continue
        # check if permissions are correct
        try:
            linked_file = links[l][-1]
            # in case a link points to a link
            while (os.path.islink(linked_file)):
                linked_file = links[linked_file][-1]
            # get permissions
            if (os.path.isdir(linked_file)):
                ll_output = subprocess.Popen(['ls', '-l', os.path.join(linked_file, '..')], \
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode('utf-8')
                ll_info = get_ll_dir(ll_output, linked_file)
            elif (os.path.isfile(linked_file)):
                ll_output = subprocess.Popen(['ls', '-l', linked_file], stdout=subprocess.PIPE, \
                                stderr=subprocess.STDOUT).communicate()[0].decode('utf-8')
                ll_info = ll_output.split()
            # ll_info: [perms, items, user, group, size, month mod, day mod, time mod, name]
            perm_info = [ll_info[0]] + ll_info[2:4]
            corr_info = links[l][:-1]
            if (not check_permissions(l, perm_info, corr_info, "link")):
                success = False
            continue
        except:
            print("Error with trying to check permissions for link {0}.".format(l))
            success = False
            continue
    return success





# Check everything

def check_filesystem():
    success = True

    dfs_path = "install/files/datafiles"  # path to datafiles from troubleshooter/

    datafiles = os.listdir(dfs_path)
    for df in datafiles:
        variables = dict()  # {var name : content}
        files = dict()      # {path : [perms, user, group]}
        links = dict()      # {path : [perms, user, group, linked path]}
        dirs = dict()       # {path : [perms, user, group]}

        # TEMP FIX: add in variables for RUBY_ARCH and RUBY_ARCM
        if (df.endswith("ruby.data")):
            variables['RUBY_ARCH'] = 'x86_64-linux'
            variables['RUBY_ARCM'] = 'x86_64-linux'

        # TEMP FIX: look for specific directory if in linux_rpm.data
        if ((df == "linux_rpm.data") and (not os.path.exists('/usr/sbin/semodule'))):
            continue

        # getting workspace id for protected files
        if (df == "wid_files.data"):
            try:
                variables['WORKSPACE_ID'] = install_info['WORKSPACE_ID']
            except KeyError:
                print("Error: could not access file {0} due to inadequate permissions. "\
                      "Please run the troubleshooter as root in order to allow access "\
                      "to figure out the issue with OMS Agent.".format(conf_path))
                return False

        # populate dictionaries with info from data files
        get_data((os.path.join(dfs_path, df)), variables, files, links, dirs)

        # check directories
        if (not check_dirs(dirs)):
            success = False

        # check files
        if (not check_files(files)):
            success = False

        # check links
        if (not check_links(links)):
            success = False

    # all successful
    return success