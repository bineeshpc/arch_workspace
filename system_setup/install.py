from abc import ABC, abstractmethod
import subprocess
import os
import shlex
import logging


logging.basicConfig(filename='/tmp/install.log',level=logging.DEBUG)


def completed_process_to_string(completed_process):
    s = []
    
    s.append(completed_process.args)
    s.append(str(completed_process.returncode))
    s.append(completed_process.stdout.decode("utf-8"))
    s.append(completed_process.stderr.decode("utf-8"))

    return "\n".join(s)


def run_as_user(username, command):
    cmd = ("sudo -H -u {user} "
    "bash -c \'{command}\'")

    cmd_concrete = cmd.format(user=username,
    command=command)
    logging.debug(cmd_concrete)
    completed_process = subprocess.run(cmd_concrete, shell=True, capture_output=True)
    logging.debug(completed_process_to_string(completed_process))


def run(command):
    logging.debug(command)
    completed_process = subprocess.run(command, shell=True, capture_output=True)
    logging.debug(completed_process_to_string(completed_process))


class Job(ABC):

    def __init__(self):
        self.install()
        self.configure()
        self.start()

    @abstractmethod
    def install(self):
        pass

    @abstractmethod
    def configure(self):
        pass

    def start(self):
        pass


class Dummy(Job):

    def __init__(self):
        self.filename = "/tmp/dummy"
        super().__init__()

    def install(self):
        run(f"echo 1 > {self.filename}")

    def configure(self):
        run(f"echo configured >> {self.filename}")

    def start(self):
        run(f"cat {self.filename}")


class Editors(Job):
    def __init__(self):
        self.editors = ["emacs", "vim"]
        super().__init__()

    def install(self):
        for editor in self.editors:
            run_as_user("root", f"pacman --noconfirm -S {editor}")

    def configure(self):
        """
        Check whether installed
        """
        for editor in self.editors:
            run(f"pacman -Qi {editor}")


class Git(Job):
    def __init__(self):
        super().__init__()

    def install(self):
        pass

    def configure(self):
        """
        Configure the global names of git
        """
        run("git config --global user.name \"Bineesh Chandrasekharan\"")
        run("git config --global user.email \"bineeshpc@gmail.com\"")


class Ssh(Job):
    def __init__(self):
        super().__init__()

    def install(self):
        run_as_user("root", "pacman --noconfirm -S openssh")

    def configure(self):
        pass

    def start(self):
        run_as_user("root", "systemctl enable sshd.service ")
        run_as_user("root", "systemctl start sshd.service ")


class Codeserver(Job):
    def __init__(self):
        super().__init__()

    def install(self):
        run("curl -fsSL https://code-server.dev/install.sh | sh")
        run("""echo 'export  PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc""")
    
    def configure(self):
        pass


class Nvidia(Job):

    def __init__(self):
        super().__init__()

    def install(self):
        print("""
        Install manually
        Find out linux kernel
        pacman -S nvidia cuda cudnn
        Should chose based on the nvidia driver and
        linux kernel

        lspci -k | grep -A 2 -E "(VGA|3D)"

        01:00.0 3D controller: NVIDIA Corporation GP107M [GeForce GTX 1050 Mobile] (rev a1)
        Subsystem: ASUSTeK Computer Inc. GP107M [GeForce GTX 1050 Mobile]
        Kernel driver in use: nouveau
--
04:00.0 VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Raven Ridge [Radeon Vega Series / Radeon Vega Mobile Series] (rev c4)
        Subsystem: ASUSTeK Computer Inc. Raven Ridge [Radeon Vega Series / Radeon Vega Mobile Series]
        Kernel driver in use: amdgpu

        tensorrt or libnvinfer are optional

        pip install tensorflow-gpu

        """)

    def configure(self):
        pass

    def start(self):
        pass


class Swap(Job):

    def __init__(self):
        super().__init__()

    def install(self):
        run_as_user("root", "fallocate -l 1G /swapfile")
        run_as_user("root", "chmod 600 /swapfile")
        run_as_user("root", "mkswap /swapfile")
        # swap on option
        # edit the file instead of doing swapon
        # sudo nano /etc/fstab
        run_as_user("root", "swapon /swapfile")
        run_as_user("root", "swapon --show")

    def configure(self):
        pass


class Screen(Job):

    def __init__(self):
        super().__init__()

    def install(self):
        run_as_user("root", "pacman --noconfirm -S screen")
        
    def configure(self):
        dir_path = os.path.dirname(os.path.abspath(__file__))
        run(f"cp {dir_path}/screenrc ~/.screenrc")


def main():
    Dummy()
    # Editors()
    # Git()
    # Nvidia()
    # Screen()
    pass


if __name__ == "__main__":
    main()
