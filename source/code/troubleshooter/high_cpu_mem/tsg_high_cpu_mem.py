from tsg_errors              import print_errors
from install.tsg_install     import check_installation
from heartbeat.tsg_heartbeat import check_omsagent_running

def check_high_cpu_memory():
    print("CHECKING FOR HIGH CPU / MEMORY USAGE...")

    success = 0

    # check if installed / running correctly
    print("Checking if omsagent installed and running...")
    # check installation
    if (get_oms_version() == None):
        print_errors(110, reinstall=False)
        print("Running the installation part of the troubleshooter in order to find the issue...")
        print("================================================================================")
        return check_installation(err_codes=False)
    # check running
    checked_omsagent_running = check_omsagent_running(workspace)
    if (checked_omsagent_running == 121):
        # try starting omsagent
        print("Agent curently not running. Attempting to start omsagent...")
        subprocess.Popen(['/opt/microsoft/omsagent/bin/service_control', 'start'])
        checked_omsagent_running = check_omsagent_running(workspace)
    if (checked_omsagent_running != 0):