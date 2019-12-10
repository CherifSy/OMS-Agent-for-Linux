# INSPIRED BY verify_e2e.py

import subprocess

from tsg_errors import tsg_error_info, get_input

def check_e2e():
    success = 0

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
                            ['y','yes','n','no'],\
                            "Please type either 'y'/'yes' or 'n'/'no' to proceed.")

    if (no_skip_all.lower() in ['y','yes']):
        for source in sources:
            query = "{0} | where Computer == '{1}' | take 1".format(source, hostname)
            print("--------------------------------------------------------------------------------")
            print(" Please run this query:")
            print("\n    {0}\n".format(query))

            # ask if query was successful
            q_result = get_input("Was the query successful? (y/n/skip)",\
                                 ['y','yes','n','no','s','skip'],\
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

            # query wasn't successful
            elif (q_result.lower() in ['n','no']):
                failures.append(source)
                # ask to quit troubleshooter completely
                quit_tsg = get_input("Do you want to continue with the troubleshooter? (y/n)",\
                                     ['y','yes','n','no'],
                                     "Please type either 'y'/'yes' or 'n'/'no' to proceed.")
                # quit troubleshooter
                if (quit_tsg.lower() in ['n','no']):
                    print("Exiting troubleshooter...")
                    print("================================================================================")
                    return 1
                # ask to quit this section
                elif (quit_tsg.lower() in ['y','yes']):
                    quit_section = get_input("Do you want to continue with this section? (y/n)",\
                                             ['y','yes','n','no'],\
                                             "Please type either 'y'/'yes' or 'n'/'no' to proceed.")
                    # quit section
                    if (quit_section.lower() in ['n','no']):
                        break
                    # continue queries
                    elif (quit_section.lower() in ['y','yes']):
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
            success = 128
            # ask to quit troubleshooter completely
            quit_tsg = get_input("Do you want to continue with the troubleshooter? (y/n)",\
                                 ['y','yes','n','no'],\
                                 "Please type either 'y'/'yes' or 'n'/'no' to proceed.")
            # quit troubleshooter
            if (quit_tsg.lower() in ['n','no']):
                print("Exiting troubleshooter...")
                print("================================================================================")
                return 1
    
    print("Continuing on with troubleshooter...")
    print("--------------------------------------------------------------------------------")
    return success
                    
