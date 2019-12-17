import re
import subprocess

from tsg_info             import tsginfo_lookup
from tsg_errors           import tsg_error_info, print_errors
from install.tsg_checkoms import get_oms_version
from install.tsg_install  import check_installation
from connect.tsg_connect  import check_connection
from .tsg_multihoming     import check_multihoming
from .tsg_log_hb          import check_log_heartbeat

sc_path = '/opt/microsoft/omsagent/bin/service_control'



def check_omsagent_running(workspace):
    # check if OMS is running through service control
    if (subprocess.call([sc_path, 'is-running']) == 1):
        return 0

    # check if OMS is running through 'ps'
    processes = subprocess.check_output(['ps', '-ef'], universal_newlines=True).split('\n')
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
            return 121

        # OMS currently running and delivering to the correct workspace
        return 0

    # none of the processes running are OMS
    return 122

def start_omsagent(workspace):
    try:
        subprocess.call([sc_path, 'enable'])
        subprocess.call([sc_path, 'start'])
        return check_omsagent_running(workspace)
    except subprocess.CalledProcessError:
        tsg_error_info.append(('executable shell script', sc_path))
        return 114



def check_heartbeat(prev_success=0):
    print("CHECKING HEARTBEAT / HEALTH...")

    success = prev_success

    # TODO: run `sh /opt/microsoft/omsagent/bin/omsadmin.sh -l` to check if onboarded and running

    # check if installed correctly
    print("Checking if installed correctly...")
    if (get_oms_version() == None):
        print_errors(111)
        print("Running the installation part of the troubleshooter in order to find the issue...")
        print("================================================================================")
        return check_installation(err_codes=False, prev_success=101)

    # get workspace ID
    workspace = tsginfo_lookup('WORKSPACE_ID')
    if (workspace == None):
        omsadmin_path = "/etc/opt/microsoft/omsagent/conf/omsadmin.conf"
        tsg_error_info.append(('Workspace ID', omsadmin_path))
        print_errors(119)
        print("Running the connection part of the troubleshooter in order to find the issue...")
        print("================================================================================")
        return check_connection(err_codes=False, prev_success=101)
    
    # check if running multi-homing
    print("Checking if omsagent is trying to run multihoming...")
    checked_multihoming = check_multihoming(workspace)
    if (checked_multihoming != 0):
        return print_errors(checked_multihoming)

    # check if other agents are sending heartbeats
    # TODO

    # check if omsagent is running
    print("Checking if omsagent is running...")
    checked_omsagent_running = check_omsagent_running(workspace)
    if (checked_omsagent_running == 122):
        # try starting omsagent
        # TODO: find better way of doing this, check to see if agent is stopped / grab results
        print("Agent curently not running. Attempting to start omsagent...")
        checked_omsagent_running = start_omsagent(workspace)
    if (checked_omsagent_running != 0):
        print_errors(checked_omsagent_running)
        return print_errors(checked_omsagent_running)

    # check if omsagent.log finds any heartbeat errors
    print("Checking for errors in omsagent.log...")
    checked_log_hb = check_log_heartbeat(workspace)
    if (checked_log_hb != 0):
        # connection issue
        if (checked_log_hb == 126):
            print_errors(checked_log_hb)
            print("Running the connection part of the troubleshooter in order to find the issue...")
            print("================================================================================")
            return check_connection(err_codes=False, prev_success=101)
        # other issue
        else:
            return print_errors(checked_log_hb)
    
    return success

