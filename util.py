#--*-- coding:utf-8 --*--
import os
import re
import sys
import shutil
import zipfile
import subprocess
import atexit
import codecs
import glob
import log

def execute_cmd_impl(cmd, work_dir=None, stdout=None): 
    if (work_dir is None) or (os.path.isdir(work_dir) is False):
        work_dir = os.getcwd()
    log.info("Exe Cmd -> '{}'".format(cmd))
    log.info("Work Dir -> '{}'".format(work_dir))
    log.info(cmd, False)
    process = subprocess.Popen(cmd, stdout=stdout, stderr=subprocess.PIPE, shell=True, cwd=work_dir)
    stdout_data, stderr_data = process.communicate()
    ret = process.returncode
    out_str_list = []
    
    # 根据返回值输出日志提示
    if ret != 0:
        # 输出错误信息到日志
        out_str_list = get_cmd_output(stderr_data)
        if sys.version_info.major >= 3:
            log.error(out_str_list, False)
        else:
            log.error(out_str_list.encode("gbk"), False)
        log.error("Exe Cmd -> '{}' failed with return code {}".format(cmd, ret))
    else:
        out_str_list = get_cmd_output(stdout_data)
        if sys.version_info.major >= 3:
            log.info(out_str_list, False)
        else:
            log.info(out_str_list.encode("gbk"), False)
        log.info("Exe Cmd -> '{}' success".format(cmd))
    return ret == 0, out_str_list

def get_cmd_output(data):
    if not data:
        return ""
    try:
        return data.decode("gbk")
    except Exception as _:
        try:
            return data.decode("utf-8")
        except Exception as _:
            return data.decode("GB2312")
    return ""

def execute_cmd(cmd, work_dir=None):
    ret, _ = execute_cmd_impl(cmd, work_dir)
    return ret

def execute_cmd_with_stdout(cmd, work_dir=None):
    ret, out_str_list = execute_cmd_impl(cmd, work_dir, subprocess.PIPE)
    return ret, out_str_list

class Adb:
    # 默认是木木模拟器
    __current_connect = "127.0.0.1:7555"
    __shell_start = "shell \""
    __shell_end = "\""

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
        Adb.__shell_start = "shell \""
        Adb.__shell_end = "\""


    @staticmethod
    def check():
        # 确认指定模拟器是否已经连接
        cmd = "adb devices"
        ret, ret_strs = execute_cmd_with_stdout(cmd)
        if not ret:
            return False
        cmd_res = "".join(ret_strs)
        if Adb.__current_connect not in cmd_res:
            cmd = "adb connect " + Adb.__current_connect
            ret, ret_strs = execute_cmd_with_stdout(cmd)
            if not ret:
                return False
            cmd_res = "".join(ret_strs)
            if cmd_res.startswith("cannot connect to"):
                log.error("connect " + Adb.__current_connect + " fail")
                return False
        return True
        
    @staticmethod
    def getcmd(cmd):
        connect_str = "-s " + Adb.__current_connect if "" != Adb.__current_connect else ""
        cmd_str = "adb " + connect_str + " " + cmd
        log.info("adb cmd:%s" % cmd_str)
        return cmd_str

    @staticmethod
    def getshell(cmd):
        connect_str = " -s " + Adb.__current_connect if "" != Adb.__current_connect else ""
        cmd_str = Adb.__shell_start + cmd + Adb.__shell_end
        cmd_str = "adb " + connect_str + " " + cmd_str
        return cmd_str