# INSPIRED BY verify_e2e.py


def check_e2e():
    # get machine's hostname
    hostname = subprocess.Popen(['hostname'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)\
                .communicate()[0].decode('utf8').rstrip('\n')

    sources = ['Heartbeat', 'Syslog', 'Perf', 'ApacheAccess_CL', 'MySQL_CL', 'Custom_Log_CL']

    successes = []
    failures = []

    print("Please go to https://ms.portal.azure.com and navigate to your workspace. "\
          "Once there, please navigate to the 'Logs' blade, and input the queries "\
          "that will be printed below. If the query was successful, then you should "\
          "see one result; if not, then there will be no results.")
    print("WARNING: not all of these will necessarily have information! Specifically, "\
          "ApacheAccess_CL, MySQL_CL, or Custom_Log_CL will have no results if you "\
          "don't use Apache, MySQL, or Custom Logs, respectively. You can always skip "\
          "certain queries if you don't want to test them by typing 's' or 'skip'.")
    # ask if user wants to skip entire query section
    skip_all = input("Do you want to skip this entire section (all queries)? (y/n): ")
    while (skip_all.lower() not in ['y','yes','n','no']):
        print("Unclear input. Please type either 'y'/'yes' or 'n'/'no' to proceed.")
        skip_all = input("Do you want to skip this entire section (all queries)? (y/n): ")

    if (skip_all.lower() in ['n','no']):
        for source in sources:
            query = "{0} | where Computer == '{1}' | take 1".format(source, hostname)
            print("Please run this query:")
            print(query)

            # ask if query was successful
            q_result = input("Was the query successful? (y/n/skip): ")
            while (q_result.lower() not in ['y','yes','n','no','s','skip']):
                print("Unclear input. Please type either 'y'/'yes' or 'n'/'no' to proceed, "\
                      "or 's'/'skip' to skip the {0} query.".format(source))
                q_result = input("Was the query successful? (y/n/skip): ")

            # skip current query
            if (q_result.lower() in ['s','skip']):
                print("Skipping {0} query...".format(source))
                continue

            # query was successful
            elif (q_result.lower() in ['y','yes']):
                successes.append(source)
                print("Continuing to next query...")

            # query wasn't successful
            elif (q_result.lower() in ['n','no']):
                failures.append(source)
                # ask to quit troubleshooter completely
                quit_tsg = input("Do you want to continue with the troubleshooter?")
                while (quit_tsg.lower() not in ['y','yes','n','no']):
                    print("Unclear input. Please type either 'y'/'yes' or 'n'/'no' to proceed.")
                    quit_tsg = input("Do you want to continue with the troubleshooter?")
                # quit troubleshooter
                if (quit_tsg.lower() in ['n','no']):
                    print("Exiting troubleshooter...")
                    return False
                # ask to quit this section
                elif (quit_tsg.lower() in ['y','yes']):
                    quit_section = input("Do you want to continue with this section?")
                    while (quit_section.lower() not in ['y','yes','n','no']):
                        print("Unclear input. Please type either 'y'/'yes' or 'n'/'no' to proceed.")
                        quit_section = input("Do you want to continue with this section?")
                    # quit section
                    if (quit_section.lower() in ['n','no']):
                        print("Continuing on with troubleshooter...")
                        break
                    # continue queries
                    elif (quit_section.lower() in ['y','yes']):
                        print("Continuing to next query...")
                        continue
            
        # summarize query section
        success_qs = successes.join(', ') if (len(successes) > 0) else 'none'
        failed_qs  = failures.join(', ')  if (len(failures) > 0)  else 'none'
        print("Successful queries: {0}".format(success_qs))
        print("Failed queries: {0}".format(failed_qs))
        
        if (len(failures) > 0):
            # ask to quit troubleshooter completely
            quit_tsg = input("Do you want to continue with the troubleshooter?")
            while (quit_tsg.lower() not in ['y','yes','n','no']):
                print("Unclear input. Please type either 'y'/'yes' or 'n'/'no' to proceed.")
                quit_tsg = input("Do you want to continue with the troubleshooter?")
            # quit troubleshooter
            if (quit_tsg.lower() in ['n','no']):
                print("Exiting troubleshooter...")
                return False

    # skipping entire section
    elif (skip_all.lower() in ['n','no']):
        print("Continuing on with troubleshooter...")

    return True
                    
