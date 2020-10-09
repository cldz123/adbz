#--*-- coding:utf-8 --*--
import logging
import os
import sys
import traceback
import time
import threading

# 单例模式
class MyLogger(object):
    _instance_lock = threading.Lock()
    _instance_init = False

    def __init__(self):
        if MyLogger._instance_init == False:
            self.logger = None
            self.file_handler = None
            self.console_handler = None
            MyLogger._instance_init = True

    def __new__(cls, *args, **kwargs):
        if not hasattr(MyLogger, "_instance"):
            with MyLogger._instance_lock:
                if not hasattr(MyLogger, "_instance"):
                    MyLogger._instance = object.__new__(cls, *args, **kwargs)
        return MyLogger._instance

    @classmethod
    def instance(cls, *args, **kwargs):
        return MyLogger(*args, **kwargs)

    def init(self, logger_name = "info"):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level = logging.INFO)
        #先删除日志文件
        # if os.path.exists(logger_name):
        #     os.remove(logger_name)
        if logger_name is None:
            logger_name = "info"
        if "" == logger_name:
            logger_name = "info"
        # cur_time_str = time.strftime("%Y-%m-%d_%H.%M.%S", time.localtime())
        cur_time_str = time.strftime("%Y-%m-%d", time.localtime())
        logger_name = logger_name + "_" + cur_time_str + ".log"

        self.file_handler = logging.FileHandler(logger_name)
        self.file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_handler)
         
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.INFO)
        self.logger.addHandler(self.console_handler)
    
    def uninit(self):
        if self.logger is not None:
            self.logger.removeHandler(self.file_handler)
            self.logger.removeHandler(self.console_handler)
            self.logger = None

    def GetMyLogger(self):
        return self.logger

def GetLogger():
    logger = MyLogger.instance()
    return logger.GetMyLogger()


def get_stack_info():
    stack_list = traceback.extract_stack()
    cur_stack = stack_list[-4]

    res = ""
    if sys.version > '3':
        # res = res + cur_stack.filename + " "
        res = res + cur_stack.name + " "
        res = res + "%03d" % cur_stack.lineno
        # res = res + cur_stack.line + " "
    else:
        # res = res + cur_stack[0] + " "
        res = res + cur_stack[2] + " "
        res = res + "%03d" % cur_stack[1]
        # res = res + cur_stack[3]+ " "
    return res

def GetLoggedStringList(log_str, file_name):
    stack_info = ""
    if file_name:
        stack_info = "[%s] " % get_stack_info()
    if type(log_str) == type([]):
        log_str = "\n".join(log_str)
    if type(log_str) == type(""):
        log_str_list = log_str.strip().split("\n")
        return [("%s%s" % (stack_info, log.strip())) for log in log_str_list]
    return ""

def info(log_str, file_name = True):
    if GetLogger():
        log_list = GetLoggedStringList(log_str, file_name)
        for log in log_list:
            GetLogger().info(log)

def error(log_str, file_name = True):
    if GetLogger():
        log_list = GetLoggedStringList(log_str, file_name)
        for log in log_list:
            GetLogger().error(log)
        
def debug(log_str, file_name = True):
    if GetLogger():
        log_list = GetLoggedStringList(log_str, file_name)
        for log in log_list:
            GetLogger().debug(log)

def warning(log_str, file_name = True):
    if GetLogger():
        log_list = GetLoggedStringList(log_str, file_name)
        for log in log_list:
            GetLogger().warning(log)

def warn(log_str, file_name = True):
    if GetLogger():
        log_list = GetLoggedStringList(log_str, file_name)
        for log in log_list:
            GetLogger().warning(log)

def critical(log_str, file_name = True):
    if GetLogger():
        log_list = GetLoggedStringList(log_str, file_name)
        for log in log_list:
            GetLogger().critical(log)
   
def exception(log_str, file_name = True):
    if GetLogger():
        log_list = GetLoggedStringList(log_str, file_name)
        for log in log_list:
            GetLogger().exception(log)
