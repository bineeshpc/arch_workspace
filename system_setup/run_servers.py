import subprocess
import os
import shlex
import logging
import threading


logging.basicConfig(filename='/tmp/run_servers.log',level=logging.DEBUG)


def run_as_user(username, command):
    cmd = ("sudo -H -u {user} "
    "bash -c \'{command}\'")
    
    cmd_concrete = cmd.format(user=username,
    command=command)
    logging.debug(cmd_concrete)
    status = subprocess.run(cmd_concrete, shell=True, capture_output=True)
    logging.debug(status)


home = os.environ["HOME"]
code_server_cmd = """/home/bineesh/.local/bin/code-server \
--auth none"""

# invoke with bash -i so that the conf in bashrc
# does not prevent source bashrc from executing
# source bashrc works only on non interactive shells by default

jupyter_server_cmd = f"bash -i /home/bineesh/agile/workspace/arch_workspace/system_setup/run_jupyter.sh"


t1 = threading.Thread(target=run_as_user, args=("bineesh", code_server_cmd))
t2 = threading.Thread(target=run_as_user, args=("bineesh", jupyter_server_cmd))

t1.start()
t2.start()
