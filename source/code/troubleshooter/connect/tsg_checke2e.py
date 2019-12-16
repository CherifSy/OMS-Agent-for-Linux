# INSPIRED BY verify_e2e.py

import subprocess

from tsg_errors import tsg_error_info, get_input

def check_e2e():
    # get machine's hostname
    hostname = subprocess.check_output(['hostname'], universal_newlines=True).rstrip('\n')

    sources = ['Heartbeat', 'Syslog', 'Perf', 'ApacheAccess_CL', 'MySQL_CL', 'Custom_Log_CL']

    successes = []
    failures = []

    print("--------------------------------------------------------------------------------")
    print(" Please go to https://ms.portal.azure.com and navigate to your workspace.\n"\
          " Once there, please navigate to the 'Logs' blade, and input the queries that\n"\
          " will be printed below. If the query was successful, then you should see one\n"\
          " result; if not, then there will be no results.\n")
    print(" WARNING: not all of these will necessarily have information! Specifically,\n"\
          " ApacheAccess_CL, MySQL_CL, or Custom_Log_CL will have no results if you don't\n"\
          " use Apache, MySQL, or Custom Logs, respectively. You can always skip certain\n"\
          " queries if you don't want to test them by typing 's' or 'skip'.\n")
    # ask if user wants to skip entire query section
    no_skip_all = get_input("Do you want to continue with this section (all queries)? (y/n)",\
                            (lambda x : x in ['y','yes','n','no']),\
                            "Please type either 'y'/'yes' or 'n'/'no' to proceed.")

    if (no_skip_all.lower() in ['y','yes']):
        for source in sources:
            # TODO: fix query to what Henry suggested
            query = "{0} | where Computer == '{1}' | take 1".format(source, hostname)
            print("--------------------------------------------------------------------------------")
            print(" Please run this query:")
            print("\n    {0}\n".format(query))

            # ask if query was successful
            q_result = get_input("Was the query successful? (y/n/skip)",\
                                 (lambda x : x in ['y','yes','n','no','s','skip']),\
                                 "Please type either 'y'/'yes' or 'n'/'no' to proceed,\n"\
                                    "or 's'/'skip' to skip the {0} query.".format(source))

            # skip current query
            if (q_result.lower() in ['s','skip']):
                print(" Skipping {0} query...".format(source))
                continue

            # query was successful
            elif (q_result.lower() in ['y','yes']):
                successes.append(source)
                print(" Continuing to next query...")
                continue

            # query wasn't successful
            elif (q_result.lower() in ['n','no']):
                failures.append(source)
                print(" Continuing to next query...")
                continue
            
        # summarize query section
        success_qs = ', '.join(successes) if (len(successes) > 0) else 'none'
        failed_qs  = ', '.join(failures)  if (len(failures) > 0)  else 'none'
        print("--------------------------------------------------------------------------------")
        print(" Successful queries: {0}".format(success_qs))
        print(" Failed queries: {0}".format(failed_qs))
        
        if (len(failures) > 0):
            tsg_error_info.append((', '.join(failures),))
            return 129
    
    print("Continuing on with troubleshooter...")
    print("--------------------------------------------------------------------------------")
    return 0
                    
