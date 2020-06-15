"""
For configuration management
especially bashrc
"""
import tempfile
import os
import shutil


class Conf:
    def __init__(self, conf, filename):
        self.conf = conf
        self.filename = filename

        
    def delete(self):
        filename = self.filename
        conf = self.conf
        conf_lines = conf.split("\n")
        firstline = conf_lines[0]
        lastline = conf_lines[-1]
        flag = False
        lines_retained = []

        with open(filename) as f:
            for line in f:
                line = line.strip("\n")
                if firstline == line or flag:
                    flag = True
                    if lastline == line:
                        flag = False
                else:
                    lines_retained.append(line)

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
            for line in lines_retained:
                tf.write(f"{line}\n")
            tempfilename = tf.name

        shutil.move(filename, f"{filename}.bk")
        shutil.move(tempfilename, filename)


    def add(self):
        filename = self.filename
        conf = self.conf

        with open(filename, "a") as f:
            lines = conf.split("\n")
            for line in lines:
                f.write(f"{line}\n")

    def is_conf_present(self):
        filename = self.filename
        conf = self.conf
        conf_lines = conf.split("\n")
        firstline = conf_lines[0]
        
        with open(filename) as f:
            flag = False
            for line in f:
                line = line.strip("\n")
                if firstline == line:
                    flag = True
                    break
            return flag


if __name__ == '__main__':
    conf = """export SPARK_DIST_CLASSPATH=$($HOME/programfiles/hadoop-3.2.1/bin/hadoop classpath)
export SPARK_HOME=$HOME/programfiles/spark-3.0.0-preview2-bin-hadoop3.2/
export PATH=$SPARK_HOME/bin:$PATH
export PYTHONPATH=$SPARK_HOME/python:$PYTHONPATH
export PYTHONPATH=$SPARK_HOME/python/lib/py4j-0.10.8.1-src.zip:$PYTHONPATH"""

    filename = "/tmp/bashrc"
    home = os.environ["HOME"]
    shutil.copy(f"{home}/.bashrc", filename)
    cf = Conf(conf, filename)
    cf.delete()
    cf.add()