import os
import subprocess


def run_command(cmd: str):
    return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    # return_code = os.system(cmd)
    # if return_code != 0:
    #     raise Exception("Setup failed")
