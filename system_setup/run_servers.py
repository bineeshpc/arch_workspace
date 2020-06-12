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


code_server_cmd = """/home/bineesh/.local/bin/code-server \
--auth none &"""

jupyter_server_cmd = """/home/bineesh/anaconda3/bin/jupyter notebook \
--config=/home/bineesh/.jupyter/jupyter_notebook_config.py \
--no-browser \
--notebook-dir=/home/bineesh/agile/workspace &"""


t1 = threading.Thread(target=run_as_user, args=("bineesh", code_server_cmd))
t2 = threading.Thread(target=run_as_user, args=("bineesh", jupyter_server_cmd))

t1.start()
t2.start()
