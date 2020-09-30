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

#改变标准输出的默认编码
#sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

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
    opts, args = getopt.getopt(sys.argv[1:], "h:", ["help="])
    log.info("opts %s args:%s" %(opts, args))
    for op, value in opts:
        if op == "-h":
            Usage()
            return
        log.info("op:%s value:%s" % (op, value))

    Adb.init_env()

    Adb.check()
    if args[0] == "pull":
        Adb.getcmd("pull /data/local/tmp/data")
        pass
    if args[0] == "push":
        pass
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
    try:
        # 强制设置编码格式为utf8
        reload(sys)
        sys.setdefaultencoding('utf-8')
        log.MyLogger.instance().init()
        Main()
    except Exception as e:
        print(e)
        log.exception("Exception Err")
    log.MyLogger.instance().uninit()