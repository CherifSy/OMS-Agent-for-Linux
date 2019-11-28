import datetime
import re
import subprocess
import time

from tsg_errors import tsg_error_info

# check log for heartbeats
def check_log_heartbeat(workspace):
    # # wait 3 minutes to be able to check last 3 heartbeats
    # print("Waiting 3 minutes to collect last 3 heartbeats...")
    # time.sleep(180)

    # get tail of logs
    log_path = "/var/opt/microsoft/omsagent/{0}/log/omsagent.log".format(workspace)
    logs = subprocess.Popen(['tail', log_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)\
                                .communicate()[0].decode('utf-8')
    
    # check for errors in tailing log file
    err_msg = "tail: cannot open '{0}' for reading: (\b+)\n".format(log_path)
    match_err = re.match(err_msg, logs)
    if (match_err != None):
        err = (match_err.groups())[0]
        # permissions error
        if (err == "Permission denied"):
            tsg_error_info.append((log_path,))
            return 100
        else:
            tsg_error_info.append((log_path, err))
            return 122

    # parse logs
    log_lines = logs.split('\n')
    parsed_log_lines = []
    for line in log_lines:
        if (line == ''):
            continue
        split_half = line.split(': ')
        parsed_log = split_half[0].split(' ')
        parsed_log.append(': '.join(split_half[1:]))
        # [ date, time, zone, [logtype], log ]
        parsed_log_lines.append(parsed_log)

    # # filter logs to last 3 minutes
    # endtime_str = ' '.join(parsed_log_lines[-1][0:2])
    # endtime = datetime.strptime(endtime_str, '%y-%m-%d %H:%M:%S')
    # starttime = endtime - datetime.timedelta(minutes=3)
    # def in_last_3mins(log):
    #     logtime_str = ' '.join(log[0:2])
    #     logtime = datetime.strptime(logtime_str, '%y-%m-%d %H:%M:%S')
    #     return (logtime > starttime)
    # parsed_log_lines = list(filter(in_last_3mins, parsed_log_lines))

    # filter out errors
    parsed_log_errs = list(filter(lambda x : (x[3]) == '[error]', parsed_log_lines))
    if (len(parsed_log_errs) > 0):
        for log_err in parsed_log_errs:
            tsg_error_info.append((log_path, log_err[0], log_err[1], log_err[4]))
        return 123

    # filter warnings
    parsed_log_warns = list(filter(lambda x : (x[3]) == '[warn]', parsed_log_lines))
    if (len(parsed_log_warns) > 0):
        hb_fail_logs = list(filter(lambda x : 'failed to flush the buffer' in x[4], parsed_log_warns))
        if (len(hb_fail_logs) > 0):
            return 125
        else:
            for log_warn in parsed_log_warns:
                tsg_error_info.append((log_path, log_warn[0], log_warn[1], log_warn[4]))
            return 124

    # logs show no errors or warnings
    return 0