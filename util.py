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
    ret = process.returncode # (len(stderr_data) == 0) # 
    out_str_list = []
    
    # 根据返回值输出日志提示
    if ret:
        # 输出错误信息到日志
        out_str_list = get_cmd_output(stderr_data)
        if sys.version_info.major >= 3:
            log.error(out_str_list, False)
        else:
            log.error(out_str_list.encode("gbk"), False)
        log.error("Exe Cmd -> '{}' failed with return code {}".format(cmd, process.returncode))
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
        # 不存在则connect
        if Adb.__current_connect not in cmd_res:
            cmd = "adb connect " + Adb.__current_connect
            ret, ret_strs = execute_cmd_with_stdout(cmd)
            if not ret:
                return False
            cmd_res = "".join(ret_strs)
            if cmd_res.startswith("cannot connect to"):
                log.error("connect " + Adb.__current_connect + " fail")
                return False

        '''
        if [ ! -d /data/local/tmp ] then mkdir -p /data/local/tmp fi
        '''
        # 确保 /data/local/tmp 目录存在
        if not Adb.check_dir("/data/local/tmp"):
            log.info("---------------------------------")
            Adb.mkdir("/data/local/tmp")
        return True
    
    # 获取包装过的adb命令
    @staticmethod
    def getcmd(cmd):
        connect_str = "-s " + Adb.__current_connect if "" != Adb.__current_connect else ""
        cmd_str = "adb " + connect_str + " " + cmd
        log.info("adb cmd:%s" % cmd_str)
        return cmd_str
    
    # 获取包装过的shell命令
    @staticmethod
    def getshell(cmd):
        connect_str = " -s " + Adb.__current_connect if "" != Adb.__current_connect else ""
        cmd_str = "shell"
        if cmd != "":
            cmd_str = Adb.__shell_start + cmd + Adb.__shell_end
        cmd_str = "adb " + connect_str + " " + cmd_str
        return cmd_str


def getcmd(cmd):
    return Adb.getcmd(cmd)

def getshell(cmd):
    return Adb.getshell(cmd)

# 判断目录或者文件是否存在
def check_exist(file):
    cmd = Adb.getshell("ls " + file)
    ret, ret_strs = execute_cmd_with_stdout(cmd)
    if not ret:
        return False
    if "No such file or directory" not in ret_strs:
        return True
    return False

def check_dir(file):
    cmd = Adb.getshell("file " + file)
    ret, ret_strs = execute_cmd_with_stdout(cmd)
    if not ret:
        return False
    if (file + ": directory") == ret_strs.strip():
        return True
    return False

def check_file(file):
    cmd = Adb.getshell("file " + file)
    ret, ret_strs = execute_cmd_with_stdout(cmd)
    if not ret:
        return False
    if (file + ": directory") == ret_strs.strip():
        return True
    return False

# 创建目录
def mkdir(dir):
    cmd = Adb.getshell("mkdir -p " + dir)
    ret, ret_strs = execute_cmd_with_stdout(cmd)
    if not ret:
        return False
    return True

# 辅助函数，用于获取对应进程的进程id
def get_process_id(process_name):
    # 获取进程id
    shell_cmd = Adb.getshell("ps | grep %s" % process_name)
    ret, res_str = execute_cmd_with_stdout(shell_cmd)
    if not ret:
        return ""
    if process_name not in res_str:
        shell_cmd = Adb.getshell("ps -A | grep %s" % process_name)
        ret, res_str = execute_cmd_with_stdout(shell_cmd)
        if not ret:
            return ""
    if process_name not in res_str:
        return ""
    res_str_list = res_str.split("\n")
    pi_list = []
    for res_str in res_str_list:
        # 优先模糊查找
        process_line = [r.strip() for r in res_str.split(" ") if r.strip() != ""]
        if 0 == len(process_line): continue
        # if process_name in process_line:
        #     pi_list.append(process_line)
        #     continue
        if process_line[-1].endswith(process_name):
            pi_list.append(process_line)
            continue
        if process_line[-1].startswith(process_name):
            pi_list.append(process_line)
            continue

    # 如果找到多个，则精准查找
    if len(pi_list) != 1:
        tmp_list = []
        for pi in pi_list:
            if pi[-1] == process_name:
                tmp_list.append(pi)
        if len(tmp_list) != 0:
            pi_list = tmp_list

    # 判断是否找到多个进程
    if len(pi_list) != 1:
        log.warn("process_info size %d" % len(pi_list))
        for pi in pi_list:
            log.info("---- " + str(pi))
        return ""
    # 返回找到的pid
    return pi_list[0][1]

# 获取模块信息
def check_module_exist(pid, mname):
    # 获取模块信息 基地址和大小
    shell_cmd = Adb.getshell("cat /proc/%s/maps | grep %s" % (pid, mname))
    ret, res_str = execute_cmd_with_stdout(shell_cmd)
    if not ret:
        return False
    if mname not in res_str:
        log.error("cannot find moudle:%s in process:%s" % (pid, mname))
        return False
    if res_str == "1":
        return False
    return True

# 获取模块信息
def get_module_infos(pid, mname):
    # 获取模块信息 基地址和大小
    shell_cmd = Adb.getshell("cat /proc/%s/maps | grep %s" % (pid, mname))
    ret, res_str = execute_cmd_with_stdout(shell_cmd)
    if not ret:
        return []
    if mname not in res_str:
        log.error("cannot find moudle:%s in process:%s" % (pid, mname))
        return []

    # 解析模块信息，可能存在多模块的情况，需要处理下
    res_str_list = res_str.split("\n")
    module_info_list = []
    last_module_info = []
    base_module_info = []
    def AddToModuleInfoList(bm, lm):
        module_info = []
        module_info.append(bm[0])
        module_info.append(lm[1])
        module_info.append(lm[2])
        module_info_list.append(module_info)

    for res_str in res_str_list:
        module_elem_info = [r.strip() for r in res_str.split(" ") if r.strip() != ""]
        if 5 >= len(module_elem_info):
            continue
        address_list =  module_elem_info[0].split("-")
        if 2 != len(address_list):
            continue
        address_list.append(module_elem_info[5])
        if len(last_module_info) == 0:
            last_module_info = address_list
            base_module_info = address_list
            continue
        if last_module_info[1] == address_list[0]:
            last_module_info = address_list
            continue
        AddToModuleInfoList(base_module_info, last_module_info) 
        base_module_info = address_list
        last_module_info = address_list

    AddToModuleInfoList(base_module_info, last_module_info)
    return module_info_list

# dump 内存
def dump(pid, mem_base, mem_size, cbs, file_name):
    log.info("base:%08x size:%08x name:%s" % (mem_base, mem_size, file_name))
    if (mem_size % cbs):
        log.error("module size %d cbs:%d" % (mem_size, cbs))
        return False
    mem_size = mem_size // cbs
    # dd if=/proc/32909/mem skip=2589069312 count=274432 bs=1 of=/data/local/tmp/1
    shell_cmd = Adb.getshell("dd if=/proc/%s/mem skip=%d count=%d bs=%s of=/data/local/tmp/%s" % (pid, mem_base, mem_size, cbs, file_name))
    ret, res_str = execute_cmd_with_stdout(shell_cmd)
    if not ret:
        return False
    shell_cmd = Adb.getcmd("pull /data/local/tmp/%s %s" % (file_name, file_name))
    ret, res_str = execute_cmd_with_stdout(shell_cmd)
    if not ret:
        return False
    shell_cmd = Adb.getshell("rm -rf /data/local/tmp/%s" % file_name)
    ret, res_str = execute_cmd_with_stdout(shell_cmd)
    if not ret:
        return False
    return True
