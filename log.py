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

def get_file_name():
    stack = traceback.extract_stack()
    return stack[-3][2]
    
def info(log_str):
    if GetLogger():
        GetLogger().info("[%s] %s" % (get_file_name(), log_str))

def error(log_str):
    if GetLogger():
        GetLogger().error("[%s] %s" % (get_file_name(), log_str))
        
def debug(log_str):
    if GetLogger():
        GetLogger().debug("[%s] %s" % (get_file_name(), log_str))

def warning(log_str):
    if GetLogger():
        GetLogger().warning("[%s] %s" % (get_file_name(), log_str))

def warn(log_str):
    if GetLogger():
        GetLogger().warning("[%s] %s" % (get_file_name(), log_str))

def critical(log_str):
    if GetLogger():
        GetLogger().critical("[%s] %s" % (get_file_name(), log_str))
        
def exception(log_str):
    if GetLogger():
        GetLogger().exception("[%s] %s" % (get_file_name(), log_str))



        
        
        
        
        
        
        
        
        
        
        
        