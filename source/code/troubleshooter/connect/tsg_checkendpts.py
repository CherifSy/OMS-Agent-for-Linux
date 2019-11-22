# INSPIRED BY update_mgmt_health_check.py

import socket

from tsg_info             import tsg_info
from install.tsg_checkoms import get_tsginfo_key

# check if is fairfax region
def is_fairfax_region():
    oms_endpt = get_tsginfo_key('OMS_ENDPOINT')
    if (oms_endpt != None):
        return ('.us' in oms_endpt)

# ping specific endpoint
def check_endpt(endpoint):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        response = sock.connect_ex((endpoint, 443))
        return (response == 0)
    except Exception:
        return False

# ping endpoints to check if connected
def check_log_analytics_endpts():
    # get workspace ID
    workspace = get_tsginfo_key('WORKSPACE_ID')
    if (workspace == None):
        omsadmin_path = "/etc/opt/microsoft/omsagent/conf/omsadmin.conf"
        print("Error in getting workspace ID. Please check {0} to make sure the workspace "\
              "ID has been added successfully.")
        return False

    # get log analytics endpoints
    if (is_fairfax_region()):
        log_analytics_endpts = ["usge-jobruntimedata-prod-1.usgovtrafficmanager.net", \
            "usge-agentservice-prod-1.usgovtrafficmanager.net", "*.ods.opinsights.azure.us", \
            "*.oms.opinsights.azure.us"]
    else:
        log_analytics_endpts = ["*.ods.opinsights.azure.com", "*.oms.opinsights.azure.com", \
            "ods.systemcenteradvisor.com"]

    for endpt in log_analytics_endpts:
        # replace '*' with workspace ID
        if ('*' in endpt):
            endpt = endpt.replace('*', workspace)

        # ping endpoint
        if (not check_endpt(endpt)):
            print("Error: endpoint {0} could not connect.".format(endpt))
            return False

    return True