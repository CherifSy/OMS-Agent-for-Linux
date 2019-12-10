import os
import subprocess

from tsg_errors import get_input



def scan_top_files(num_files, tto):
    with open(os.devnull, 'w') as devnull:
        find_cmd = subprocess.Popen(['find','/','-type','f','-exec','du','-S','\{\}','+'],\
                        stdout=subprocess.PIPE, stderr=devnull)
        sort_cmd = subprocess.Popen(['sort','-r'], stdin=find_cmd.stdout,\
                        stdout=subprocess.PIPE, stderr=devnull)
        files = subprocess.check_output(['head','-n',num_files], stdin=sort_cmd.stdout,\
                        universal_newlines=True)

def check_disk_space():
    print("--------------------------------------------------------------------------------")
    print("") # something about going to check largest files
    num_files = get_input()
    tto = get_input()

