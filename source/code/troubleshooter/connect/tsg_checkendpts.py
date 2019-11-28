# INSPIRED BY update_mgmt_health_check.py

import socket

from tsg_info             import tsg_info
from tsg_errors           import tsg_error_info
from install.tsg_checkoms import get_tsginfo_key

omsadmin_path = "/etc/opt/microsoft/omsagent/conf/omsadmin.conf"

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



# check general internet connectivity
def check_internet_connect():
    if (check_endpt("bing.com") and check_endpt("google.com")):
        return 0
    else:
        return 127



# check agent service endpoint
def check_agent_service_endpt():
    dsc_endpt = get_tsginfo_key('DSC_ENDPOINT')
    if (dsc_endpt == None):
        tsg_error_info.append(('DSC (agent service) endpoint', omsadmin_path))
        return 118
    agent_endpt = dsc_endpt.split('/')[2]

    if (check_endpt(agent_endpt)):
        return 0
    else:
        tsg_error_info.append((agent_endpt,))
        return 119




# check log analytics endpoints
def check_log_analytics_endpts():
    success = 0

    # get workspace ID
    workspace = get_tsginfo_key('WORKSPACE_ID')
    if (workspace == None):
        tsg_error_info.append(('workspace ID', omsadmin_path))
        return 118

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
            tsg_error_info.append((endpt,))
            success = 119

    return success