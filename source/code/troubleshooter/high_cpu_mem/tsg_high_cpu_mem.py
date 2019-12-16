from tsg_errors              import print_errors
from install.tsg_checkoms    import get_oms_version
from install.tsg_install     import check_installation
from connect.tsg_checkendpts import check_log_analytics_endpts
from connect.tsg_connect     import check_connection
from heartbeat.tsg_heartbeat import start_omsagent, check_omsagent_running, check_heartbeat
from .tsg_checkspace         import check_disk_space

def check_high_cpu_memory(prev_success=0):
    print("CHECKING FOR HIGH CPU / MEMORY USAGE...")

    success = prev_success

    # check if installed / connected / running correctly
    print("Checking if omsagent installed and running...")
    # check installation
    if (get_oms_version() == None):
        print_errors(111)
        print("Running the installation part of the troubleshooter in order to find the issue...")
        print("================================================================================")
        return check_installation(err_codes=False, prev_success=101)

    # check connection
    checked_la_endpts = check_log_analytics_endpts()
    if (checked_la_endpts != 0):
        print_errors(checked_la_endpts)
        print("Running the connection part of the troubleshooter in order to find the issue...")
        print("================================================================================")
        return check_connection(err_codes=False, prev_success=101)

    # check running
    checked_omsagent_running = check_omsagent_running(workspace)
    if (checked_omsagent_running != 0):
        print_errors(checked_omsagent_running)
        print("Running the general health part of the troubleshooter in order to find the issue...")
        print("================================================================================")
        return check_heartbeat(prev_success=101)

    # check disk space
    checked_disk_space = check_disk_space()
    if (checked_disk_space != 0):
        return print_errors(checked_disk_space)

    # check CPU capacity