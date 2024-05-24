from abc import ABC, abstractmethod
import subprocess
import os
import shlex
import logging
import conffile
import argparse

filename = "/tmp/install.log"
print(f"check output in {filename}")
logging.basicConfig(filename=filename,level=logging.DEBUG)
home = os.environ["HOME"]

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


class Arch:
    def __init__(self, name):
        self.name = name
        self.install_cmd = "pacman --noconfirm -S "
        self.configure_cmd = "pacman -Qi "

    def get_install_cmd(self):
        return self.install_cmd

    def get_configure_cmd(self):
        return self.configure_cmd

class Ubuntu:
    def __init__(self, name):
        self.name = name
        self.install_cmd = f"apt-get update && \
        DEBIAN_FRONTEND=noninteractive apt-get --yes --allow-downgrades install "
        self.configure_cmd = "dpkg -s "

    def get_install_cmd(self):
        return self.install_cmd

    def get_configure_cmd(self):
        return self.configure_cmd

class OS:
    def __init__(self, name):
        self.name = name

    def get_os(self):
        if self.name == "arch":
            return Arch(self.name)
        if self.name == "ubuntu":
            return Ubuntu(self.name)


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
    def __init__(self, os):
        self.editors = ["emacs", "vim"]
        self.os = OS(name=os).get_os()
        super().__init__()

    def install(self):
        for editor in self.editors:
            run_as_user("root", f"{self.os.get_install_cmd()} {editor}")

    def configure(self):
        """
        Check whether installed
        """
        for editor in self.editors:
            run(f"{self.os.get_configure_cmd()} {editor}")


class Surfshark(Job):
    def __init__(self, os):
        self.packagename = "surfshark-gui-bin"
        self.os = OS(name=os).get_os()
        super().__init__()

    def install(self):
        run_as_user("root", f"{self.os.get_install_cmd()} {self.packagename}")

    def configure(self):
        """
        Check whether installed
        """
        run(f"{self.os.get_configure_cmd()} {self.packagename}")

class Git(Job):
    def __init__(self):
        super().__init__()

    def install(self):
        run_as_user("root", "pacman --noconfirm -S git")

    def configure(self):
        """
        Configure the global names of git
        """
        run("git config --global user.name \"Bineesh Panangat\"")
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

    def __init__(self, os):
        self.os = OS(name=os).get_os()
        super().__init__()

    def install(self):
        run_as_user("root", f"{self.os.get_install_cmd()} screen")

    def configure(self):
        dir_path = os.path.dirname(os.path.abspath(__file__))
        run(f"cp {dir_path}/screenrc ~/.screenrc")


class Java(Job):

    def __init__(self):
        super().__init__()

    def install(self):
        pass

    def configure(self):
        run("echo 'export JAVA_HOME=/usr/lib/jvm/default/' >> ~/.bashrc")

class Hadoop2(Job):


    def __init__(self, add_conf=True):
        self.install_path = f"{home}/programfiles/hadoop-2.10.0/"
        self.add_conf = add_conf
        super().__init__()


    def install(self):
        if not os.path.exists(self.install_path):
            run("mkdir -p downloads")
            run("cd downloads && wget https://mirrors.estointernet.in/apache/hadoop/common/hadoop-2.10.0/hadoop-2.10.0.tar.gz")
            run("mkdir -p programfiles")
            run("cd programfiles && tar -zxvf ../downloads/hadoop-2.10.0.tar.gz")

    def configure(self):
        self.conf = """export HADOOP_HOME=$HOME/programfiles/hadoop-2.10.0/
export HADOOP_MAPRED_HOME=$HADOOP_HOME
export HADOOP_COMMON_HOME=$HADOOP_HOME
export HADOOP_HDFS_HOME=$HADOOP_HOME
export YARN_HOME=$HADOOP_HOME
export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
export PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin
export HADOOP_INSTALL=$HADOOP_HOME
export HADOOP_CLASSPATH=${JAVA_HOME}/lib/tools.jar
export PATH=${JAVA_HOME}/bin:${PATH}"""
        self.cf = conffile.Conf(self.conf, f"{home}/.bashrc")

        if self.add_conf:
            otherhadoop = Hadoop3(add_conf=False)
            if otherhadoop.cf.is_conf_present():
                otherhadoop.cf.delete()

            if not self.cf.is_conf_present():
                self.cf.add()


class Hadoop3(Job):


    def __init__(self, add_conf=True):
        self.install_path = f"{home}/programfiles/hadoop-3.2.1/"
        self.add_conf = add_conf
        super().__init__()


    def install(self):
        if not os.path.exists(self.install_path):
            run("mkdir -p downloads")
            run("cd downloads && wget http://mirrors.estointernet.in/apache/hadoop/common/hadoop-3.2.1/hadoop-3.2.1.tar.gz")
            run("mkdir -p programfiles")
            run("cd programfiles && tar -zxvf ../downloads/hadoop-3.2.1.tar.gz")

    def configure(self):
        self.conf = """export HADOOP_HOME=$HOME/programfiles/hadoop-3.2.1/
export HADOOP_MAPRED_HOME=$HADOOP_HOME
export HADOOP_COMMON_HOME=$HADOOP_HOME
export HADOOP_HDFS_HOME=$HADOOP_HOME
export YARN_HOME=$HADOOP_HOME
export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
export PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin
export HADOOP_INSTALL=$HADOOP_HOME
export HADOOP_CLASSPATH=${JAVA_HOME}/lib/tools.jar
export PATH=${JAVA_HOME}/bin:${PATH}"""
        self.cf = conffile.Conf(self.conf, f"{home}/.bashrc")


        if self.add_conf:
            otherhadoop = Hadoop2(add_conf=False)
            if otherhadoop.cf.is_conf_present():
                otherhadoop.cf.delete()

            if not self.cf.is_conf_present():
                self.cf.add()


class Spark2(Job):

    def __init__(self, add_conf=True):
        self.install_path = f"{home}/programfiles/spark-2.4.6-bin-hadoop2.7/"
        self.add_conf = add_conf
        super().__init__()

    def install(self):
        if not os.path.exists(self.install_path):
            url_location = ("https://mirrors.estointernet.in/apache/spark/"
            "spark-2.4.6/spark-2.4.6-bin-hadoop2.7.tgz")
            run("mkdir -p downloads")
            run(f"""cd downloads && wget {url_location}""")
            run("mkdir -p programfiles")
            run(f"cd programfiles && tar -zxvf ../downloads/{url_location.split('/')[-1]}")


    def configure(self):
        self.conf = """export SPARK_DIST_CLASSPATH=$($HOME/programfiles/hadoop-2.10.0/bin/hadoop classpath)
export SPARK_HOME=$HOME/programfiles/spark-2.4.6-bin-hadoop2.7/
export PATH=$SPARK_HOME/bin:$PATH
export PYTHONPATH=$SPARK_HOME/python:$PYTHONPATH
export PYTHONPATH=$SPARK_HOME/python/lib/py4j-0.10.7-src.zip:$PYTHONPATH"""
        self.cf = conffile.Conf(self.conf, f"{home}/.bashrc")

        if self.add_conf:
            other = Spark3(add_conf=False)
            if other.cf.is_conf_present():
                other.cf.delete()

            if not self.cf.is_conf_present():
                self.cf.add()


class Spark3(Job):

    def __init__(self, add_conf=True):
        self.install_path = f"{home}/programfiles/spark-3.0.0-preview2-bin-hadoop3.2/"
        self.add_conf = add_conf
        super().__init__()

    def install(self):
        if not os.path.exists(self.install_path):
            url_location = ("http://apachemirror.wuchna.com/spark/"
            "spark-3.0.0-preview2/spark-3.0.0-preview2-bin-hadoop3.2.tgz")
            run("mkdir -p downloads")
            run(f"""cd downloads && wget {url_location}""")
            run("mkdir -p programfiles")
            run(f"cd programfiles && tar -zxvf ../downloads/{url_location.split('/')[-1]}")


    def configure(self):
        self.conf = """export SPARK_DIST_CLASSPATH=$($HOME/programfiles/hadoop-3.2.1/bin/hadoop classpath)
export SPARK_HOME=$HOME/programfiles/spark-3.0.0-preview2-bin-hadoop3.2/
export PATH=$SPARK_HOME/bin:$PATH
export PYTHONPATH=$SPARK_HOME/python:$PYTHONPATH
export PYTHONPATH=$SPARK_HOME/python/lib/py4j-0.10.8.1-src.zip:$PYTHONPATH"""
        self.cf = conffile.Conf(self.conf, f"{home}/.bashrc")

        if self.add_conf:
            other = Spark2(add_conf=False)
            if other.cf.is_conf_present():
                other.cf.delete()

            if not self.cf.is_conf_present():
                self.cf.add()


def parse_cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument("os", type=str)
    return parser.parse_args()

def main():
    args = parse_cmdline()
    # Dummy()
    Editors(args.os)
    Git()
    # Nvidia()
    Screen(args.os)
    # Surfshark(args.os)
    # Java()
    # Hadoop2()
    # Spark2()
    # Hadoop3()
    # Spark3()



if __name__ == "__main__":
    main()
