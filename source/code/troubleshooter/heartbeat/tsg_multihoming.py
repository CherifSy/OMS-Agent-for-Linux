# INSPIRED BY update_mgmt_health_check.py

import os

from tsg_errors import tsg_error_info

def check_multihoming():
    directories = []
    potential_workspaces = []

    for (dirpath, dirnames, filenames) in os.walk("/var/opt/microsoft/omsagent"):
        directories.extend(dirnames)
        break # Get the top level of directories

    for directory in directories:
        if len(directory) >= 32:
            potential_workspaces.append(directory)

    workspace_id_list = ', '.join(potential_workspaces)
    if len(potential_workspaces) > 1:
        tsg_error_info.append((workspace_id_list))
        return 126

    return 0
        