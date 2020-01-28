import os
import subprocess
import time

from tsg_errors import get_input



def check_top_files(top_files):
    for (fsize,fpath) in top_files:
        fnew = subprocess.check_output(['du',fpath], universal_newlines=True)
        fsize_new = (fnew.split())[0]
        fsize_diff = fsize_new - fsize
        # check who opened



def scan_top_files(num_files, tto):
    with open(os.devnull, 'w') as devnull:
        find_cmd = subprocess.Popen(['find','/','-type','f','-exec','du','-S','\{\}','+'],\
                        stdout=subprocess.PIPE, stderr=devnull)
        sort_cmd = subprocess.Popen(['sort','-rh'], stdin=find_cmd.stdout,\
                        stdout=subprocess.PIPE, stderr=devnull)
        files = subprocess.check_output(['head','-n',num_files], stdin=sort_cmd.stdout,\
                        universal_newlines=True, stderr=devnull)
        # [(size1, file1), (size2, file2), ...]
        it = iter(files.split())
        top_files = zip(it,it)
    # check every second
    for sec in range(tto):
        check_top_files(top_files)
        time.sleep(1)

        

def check_disk_space():
    print("--------------------------------------------------------------------------------")
    print("") # something about going to check largest files

    def check_int(i):
        try:
            return (int(i) > 0)
        except ValueError:
            return (i == '')

    num_files_in = get_input("How many files do you want to check? (Default is top 20 files)",\
                          check_int,\
                          "Please either type a positive integer, or just hit enter to go\n"\
                            "with the default value.")
    num_files = 20 if (num_files_in == '') else int(num_files_in)
    tto_in = get_input("How many seconds do you want to observe the files? (Default is 60sec)",\
                    check_int,\
                    "Please either type a positive integer, or just hit enter to go\nwith "\
                        "the default value.")
    tto = 60 if (tto_in == '') else int(tto_in)

