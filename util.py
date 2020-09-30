#--*-- coding:utf-8 --*--
import os
import re
import shutil
import zipfile
import subprocess
import atexit
import codecs
import glob
import log

def execute_cmd_impl(cmd, work_dir=None, stdout=None):
    log.info("execute cmd -> '{}'".format(cmd))
    log.info("work_dir -> {}".format( work_dir))
    
    if (work_dir is None) or (os.path.isdir(work_dir) is False):
        work_dir = os.getcwd()
    process = subprocess.Popen(cmd, stdout=stdout, stderr=subprocess.PIPE, shell=True, cwd=work_dir)
    ret = process.wait()
    
    # 输出错误信息到日志
    for line in iter(process.stderr.readline, b""):
        line_strip = line.strip('\r\n')
        if line_strip != '':
            log.error('Command error output -> {}'.format(line_strip))
    
    # 根据返回值输出日志提示
    if ret != 0:
        log.error('Execute command "{}" failed with return code {}'.format(cmd, ret))
    else:
        log.info('Execute command "{}" success'.format(cmd))
    return ret == 0, process.stdout
    
def execute_cmd(cmd, work_dir=None):
    ret, _ = execute_cmd_impl(cmd, work_dir)
    return ret

def execute_cmd_with_stdout(cmd, work_dir=None):
    ret, stdout = execute_cmd_impl(cmd, work_dir, subprocess.PIPE)
    return ret, stdout

class Adb:
    # 默认是木木模拟器
    __current_connect = "127.0.0.1:7555"
    __shell_start = "shell "
    __shell_end = ""

    @staticmethod
    def init_env():
        if "AdbConnect" in os.environ:
            Adb.__current_connect = os.environ["AdbConnect"]
        if "AdbShell" in os.environ:
            Adb.init_adb_shell(os.environ["AdbShell"])

    @staticmethod
    def init_adb_shell(adb_shell):
        if "1" == adb_shell:
            Adb.__shell_start = "shell \"su -c'"
            Adb.__shell_end = "'\""
            return
        if "2" == adb_shell:
            Adb.__shell_start = "shell \"su c"
            Adb.__shell_end = "\""
            return
        Adb.__shell_start = "shell "
        Adb.__shell_end = ""

    @staticmethod
    def check():
        # 确认指定模拟器是否已经连接
        cmd = "adb devices"
        ret, pipe = execute_cmd_with_stdout(cmd)
        if not ret:
            return False
        cmd_res = pipe.readline().decode().rstrip('\r\n')
        if Adb.__current_connect not in cmd_res:
            cmd = "adb connect " + Adb.__current_connect
            ret, pipe = execute_cmd_with_stdout(cmd)
            if not ret:
                return False
            if pipe.readline().startswith("cannot connect to"):
                log.error("connect " + Adb.__current_connect + " fail")
                return False
        return True
        
    @staticmethod
    def getcmd(cmd):
        connect_str = " -s " + Adb.__current_connect if "" != Adb.__current_connect else ""
        cmd_str = "adb " + connect_str + " " + cmd
        log.info("adb cmd:%s" % cmd_str)
        return cmd_str

    @staticmethod
    def getshell(cmd):
        connect_str = " -s " + Adb.__current_connect if "" != Adb.__current_connect else ""
        cmd_str = Adb.__shell_start + cmd + Adb.__shell_end
        cmd_str = "adb " + connect_str + " " + cmd_str
        log.info("adb cmd:%s" % cmd_str)
        return cmd_str