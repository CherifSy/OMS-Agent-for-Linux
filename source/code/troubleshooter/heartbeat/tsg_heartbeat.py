import re
import subprocess

from tsg_info             import tsginfo_lookup
from tsg_errors           import tsg_error_info, print_errors
from install.tsg_checkoms import get_oms_version
from install.tsg_install  import check_installation
from connect.tsg_connect  import check_connection
from .tsg_multihoming     import check_multihoming
from .tsg_log_hb          import check_log_heartbeat

# backwards compatible input() function for Python 2 vs 3
try:
    input = raw_input
except NameError:
    pass



def check_omsagent_running(workspace):
    # check if OMS is running through 'ps'
    processes = subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)\
                                .communicate()[0].decode('utf8').split('\n')
    for process in processes:
        # check if process is OMS
        if (not process.startswith('omsagent')):
            continue

        # [ UID, PID, PPID, C, STIME, TTY, TIME, CMD ]
        process = process.split()
        command = ' '.join(process[7:])

        # try to match command with omsagent command
        regx_cmd = "/opt/microsoft/omsagent/ruby/bin/ruby /opt/microsoft/omsagent/bin/omsagent "\
                   "-d /var/opt/microsoft/omsagent/(\S+)/run/omsagent.pid "\
                   "-o /var/opt/microsoft/omsagent/(\S+)/log/omsagent.log "\
                   "-c /etc/opt/microsoft/omsagent/(\S+)/conf/omsagent.conf "\
                   "--no-supervisor"
        matches = re.match(regx_cmd, command)
        if (matches == None):
            continue

        matches_tup = matches.groups()
        guid = matches_tup[0]
        if (matches_tup.count(guid) != len(matches_tup)):
            continue

        # check if OMS is running with a different workspace
        if (workspace != guid):
            tsg_error_info.append((guid, workspace))
            return 120

        # OMS currently running and delivering to the correct workspace
        return 0

    # none of the processes running are OMS
    return 121



# TODO: ask if user wants to restart OMS - /opt/microsoft/omsagent/bin/service_control restart



def check_heartbeat():
    print("CHECKING HEARTBEAT / HEALTH...")

    success = 0

    # check if installed correctly
    print("Checking if installed correctly...")
    if (get_oms_version() == None):
        print_errors(110, reinstall=False)
        print("Running the installation part of the troubleshooter in order to find the issue...")
        print("================================================================================")
        return check_installation(err_codes=False)

    # get workspace ID
    workspace = tsginfo_lookup('WORKSPACE_ID')
    if (workspace == None):
        omsadmin_path = "/etc/opt/microsoft/omsagent/conf/omsadmin.conf"
        tsg_error_info.append(('Workspace ID', omsadmin_path))
        return print_errors(118, reinstall=False)
    
    # check if running multi-homing
    print("Checking if omsagent is trying to run multihoming...")
    checked_multihoming = check_multihoming()
    if (checked_multihoming != 0):
        return print_errors(checked_multihoming, reinstall=False)

    # check if other agents are sending heartbeats
    # TODO

    # check if omsagent is running
    print("Checking if omsagent is running...")
    checked_omsagent_running = check_omsagent_running(workspace)
    if (checked_omsagent_running == 121):
        # try starting omsagent
        print(" Agent curently not running. Attempting to start omsagent...")
        subprocess.Popen(['/opt/microsoft/omsagent/bin/service_control', 'start'])
        checked_omsagent_running = check_omsagent_running(workspace)
    if (checked_omsagent_running != 0):
        if (print_errors(checked_omsagent_running, restart_oms=True) == 1):
            return 1
        else:
            checked_omsagent_running = check_omsagent_running(workspace)
            if (checked_omsagent_running != 0):
                success = 101


    # check if omsagent.log finds any heartbeat errors
    print("Checking if omsagent.log found any errors...")
    checked_log_hb = check_log_heartbeat(workspace)
    if (checked_log_hb != 0):
        # connection issue
        if (checked_log_hb == 125):
            print_errors(checked_log_hb, reinstall=False)
            print("Running the connection part of the troubleshooter in order to find the issue...")
            print("================================================================================")
            return check_connection(err_codes=False)
        # other issue
        if (print_errors(checked_log_hb) == 1):
            return 1
        else:
            success = 101
    
    return success

