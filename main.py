#--*-- coding:utf-8 --*--

import log
import os
import traceback
import atexit
import sys
import datetime
import getopt
import util
from util import Adb
from command import Command

#改变标准输出的默认编码
# sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

exe_state = False

def Exit():
    log.info("---- Start ----")
    # 检查是否异常退出
    global exe_state
    if exe_state is False:
        log.error('Exited abnormally')

    # 整理输出结果
    log.info("---- End ----")

def Usage():
    pass

def Run():
    Adb.init_env()
    Adb.check()

    current_cmd = sys.argv[1].lower()
    current_cmd_arg = " ".join(sys.argv[2:])
    if current_cmd == "help":
        Usage()
        return True
    if current_cmd == "pull":
        return Command.pull(sys.argv[2:])
    if current_cmd == "push":
        return Command.push(sys.argv[2:])
    if current_cmd == "shell":
        return Command.shell(current_cmd_arg)
    if current_cmd == "dump":
        return Command.dump(sys.argv[2:])
    if current_cmd == "module" or current_cmd == "mod":
        return Command.module(sys.argv[2:])
    if current_cmd == "process":
        return Command.process(sys.argv[2:])
    if current_cmd == "inject":
        return Command.inject(sys.argv[2:])
    if current_cmd == "dolua":
        return Command.dolua(sys.argv[2:])
    if current_cmd == "lua":
        return Command.loadlua(sys.argv[2:])
    if current_cmd == "unlua":
        return Command.unloadlua(sys.argv[2:])
    if current_cmd == "uninject":
        return Command.uninject(sys.argv[2:])
    
    log.info("unknown command:%s args:%s" % (current_cmd, current_cmd_arg))
    return False

def Main():
    log.info("---- Start ----")
    # 注册退出时执行的函数
    atexit.register(Exit)
    # 保存开始时间
    start_time = datetime.datetime.now()

    expect_seconds = 0

    # 执行函数
    ret = Run()
    global exe_state
    exe_state = True
    # 计算执行时间
    execution_seconds = (datetime.datetime.now() - start_time).seconds
    # 打印结束信息
    execution_result = 'success'
    if (isinstance(ret, bool) and ret is False) or (not isinstance(ret, bool) and isinstance(ret, int) and ret != 0):
        execution_result = 'failed'

    run_result = ''
    if expect_seconds != 0:
        run_result = 'expect in {} seconds'.format(expect_seconds)
        if execution_seconds > expect_seconds:
            run_result += ', execution TIMEOUT'
            
    log.info('------------ {}, execution takes {} seconds{}'.format(execution_result, execution_seconds, run_result))
    log.info("---- End ----")
    

if __name__ == "__main__":
    log.MyLogger.instance().init()
    try:
        log.info("python version:" + sys.version)
        log.info({})
        # 强制设置编码格式为utf8
        if sys.version_info.major >= 3:
            import importlib, sys
            importlib.reload(sys)
        else:
            reload(sys)
            sys.setdefaultencoding('utf-8')
        Main()
    except Exception as e:
        print(e)
        log.exception("Exception Err")
    log.MyLogger.instance().uninit()