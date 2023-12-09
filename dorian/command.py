import os
import subprocess


def run_command(cmd: str):
    cmd = f"""set -e; {cmd}"""
    return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
