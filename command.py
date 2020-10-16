#--*-- coding:utf-8 --*--

import os
import sys
import log
import util
import getopt
class Command:
    
    # 命令执行的一些配置
    '''
    pull 拉取文件
    adbz pull -r remote-file  [-l local_path] [-n local_name]
    '''
    @staticmethod
    def pull(cmd_args):
        opts, args = getopt.getopt(cmd_args, "r:l:n:", ["remote-file=", "local-path=", "local-name="])
        log.info("opts %s args:%s" %(opts, args))
        remote_file, local_path, local_name = "", "", ""
        for op, value in opts:
            if op == "-r" or op == "--remote-file":
                remote_file = value
            elif op == "-l" or op == "--local-path":
                local_path = value
            elif op == "-n" or op == "--local-name":
                local_name = value
            else:
                log.error("unkown opt:%s value:%s" % (op, value))
                return False
        if len(opts) == 0:
            remote_file = args[0] if len(args) >= 1 else ""
            local_path = args[1] if len(args) >= 2 else ""
            local_name = args[2] if len(args) >= 3 else ""
        
        if local_path == "":
            local_path = "./"
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        if util.check_dir(remote_file):
            # 目录
            local_file = local_path + "/"
        else:
            remote_fname = os.path.basename(remote_file)
            if local_name == "":
                local_name = remote_fname
            local_file = os.path.join(local_path, local_name)

        log.info("remote:%s local:%s" % (remote_file, local_file))
        shell_cmd = util.getcmd('pull "%s" "%s"' % (remote_file, local_file))
        ret, res_str = util.execute_cmd_with_stdout(shell_cmd)
        if not ret:
            return False
        return True

    '''
    push 上传文件
    adbz push -l local_path [-r remote_path] [-n remote_name]
    '''
    @staticmethod
    def push(cmd_args):
        opts, args = getopt.getopt(cmd_args, "l:r:n:", ["local-file=", "remote-path=", "remote-name=", "bak", "exec"])
        log.info("opts %s args:%s" %(opts, args))
        local_file, remote_path, remote_name = "", "", ""
        bak_file, exec_file = False, False
        for op, value in opts:
            if op == "-l" or op == "--local-file":
                local_file = value
            elif op == "-r" or op == "--remote-path":
                remote_path = value
            elif op == "-n" or op == "--remote-name":
                remote_name = value
            elif op == "--bak":
                bak_file = True
            elif op == "--exec":
                exec_file = True
            else:
                log.error("unkown opt:%s value:%s" % (op, value))
                return False
        if len(opts) == 0:
            local_file = args[0] if len(args) >= 1 else ""
            remote_path = args[1] if len(args) >= 2 else ""
            remote_name = args[2] if len(args) >= 3 else ""
    
        if remote_path == "":
            remote_path = "/data/local/tmp"
        if os.path.isdir(local_file):
            # push 目录
            remote_file = remote_path + "/"
            util.mkdir(remote_file)
        elif os.path.isfile(os.path.join(os.getcwd(), local_file)):
            # push 文件
            # local_path = os.path.dirname(local_file)
            local_fname = os.path.basename(local_file)
            if remote_name == "":
                remote_name = local_fname
            remote_file = remote_path + "/" + remote_name
        else:
            log.error("local file:%s %s not exist" % (local_file, os.path.join(os.getcwd(), local_file)))
            return False
        if bak_file:
            shell_cmd = util.getshell('mv "%s" "%s.bak"' % (remote_file, remote_file))
            if not util.execute_cmd(shell_cmd): return False
        log.info("local:%s remote:%s" % (local_file, remote_file))
        shell_cmd = util.getcmd('push "%s" "%s"' % (local_file, remote_file))
        ret, res_str = util.execute_cmd_with_stdout(shell_cmd)
        if not ret:
            return False
        if exec_file:
            shell_cmd = util.getshell('chmod 777 "%s"' % remote_file)
            return util.execute_cmd(shell_cmd)
        return True
 
    '''
    执行shell命令
    adbz shell ps
    adbz shell "ps | grep sgame"
    '''
    @staticmethod
    def shell(args):
        shell_cmd = util.getshell(args)
        log.info(shell_cmd)
        return util.execute_cmd(shell_cmd)

    '''
    dump 模块或内存
    1. adbz dump -p com.tencent.tmgp.sgame -m libil2cpp.so [-n file_name] [-c cbs]
    2. adbz dump -p com.tencent.tmgp.sgame -b base_addr -s size [-n file_name] [-c cbs]
    '''
    @staticmethod
    def dump(cmd_args):
        opts, args = getopt.getopt(cmd_args, "p:m:b:s:n:c:e:", ["process=", "module=", "base=", "end=", "size=", "name=", "cbs="])
        log.info("opts %s args:%s" %(opts, args))
        process_name, module_name, file_name = "", "", ""
        base_addr, end_addr, mem_size = 0, 0, 0
        cbs = 1
        for op, value in opts:
            if op == "-p" or op == "--process":
                process_name = value
            elif op == "-m" or op == "--module":
                module_name = value
            elif op == "-b" or op == "--base":
                base_addr = int(value, 16)
            elif op == "-e" or op == "--end":
                base_addr = int(value, 16)
            elif op == "-s" or op == "--size":
                mem_size = int(value, 16)
            elif op == "-n" or op == "--name":
                file_name = value
            elif op == "-c" or op == "--cbs":
                cbs = int(value, 10)
            else:
                log.error("unkown opt:%s value:%s" % (op, value))
                return False
        if len(opts) == 0:
            process_name = args[0] if len(args) >= 1 else ""
            module_name = args[1] if len(args) >= 2 else ""

        # check args
        if cbs <= 0:
            log.error("error cbs:%d" % cbs)
            return False
        if process_name == "" or (module_name == "" and base_addr == 0):
            log.error("error args:")
            return False

        # 获取进程id
        process_id = util.get_process_id(process_name)
        if "" == process_id:
            log.error("get process:%s id fail" % process_name)
            return False

        # dump 内存
        if base_addr != 0:
            if mem_size == 0: mem_size = end_addr - base_addr
            module_save_name = file_name if file_name != "" else "%08X" % base_addr
            return util.dump(process_id, base_addr, mem_size, cbs, module_save_name)

        # 获取模块信息
        mi_list = util.get_module_infos(process_id, module_name)
        if 0 == len(mi_list):
            log.error("get process:%s module:%s fail" % (process_name, module_name))
            return False

        # 模块dump
        multi_module = (len(mi_list) != 1)
        for mi in mi_list:
            # 得到模块起始地址和结束地址，计算大小
            module_size = (int(mi[1], 16) - int(mi[0], 16))
            module_base = int(mi[0], 16)
            module_save_name = file_name if file_name != "" else module_name
            if multi_module:
                module_name_elems = os.path.splitext(module_save_name)
                if len(module_name_elems) > 1:
                    module_save_name = "".join(module_name_elems[:-1]) + "_" + mi[0] + module_name_elems[-1]
                else:
                    module_save_name = module_save_name + "_" + mi[0]
            if not util.dump(process_id, module_base, module_size, cbs, module_save_name):
                return False
        return True
    
    '''
    查看进程的模块信息
    adbz moudle -p process_name [-m moudle_name]
    '''
    @staticmethod
    def module(cmd_args):
        opts, args = getopt.getopt(cmd_args, "p:m:", ["process=", "module="])
        log.info("opts %s args:%s" %(opts, args))
        process_name, module_name = "", ""
        for op, value in opts:
            if op == "-p" or op == "--process":
                process_name = value
            elif op == "-m" or op == "--module":
                module_name = value
            else:
                log.error("unkown opt:%s value:%s" % (op, value))
                return False
        if len(opts) == 0:
            process_name = args[0] if len(args) >= 1 else ""
            module_name = args[1] if len(args) >= 2 else ""

        # 获取进程id
        process_id = util.get_process_id(process_name)
        if "" == process_id:
            log.error("get process:%s id fail" % process_name)
            return False
        # 获取模块信息
        if module_name != "":
            module_name = " | grep %s" % module_name
        shell_cmd = util.getshell("cat /proc/%s/maps%s" % (process_id, module_name))
        ret, res_str = util.execute_cmd_with_stdout(shell_cmd)
        if not ret:
            return False
        return True

    '''
    查看进程信息 信息汇总
    adbz moudle -p process_name [-m moudle_name]
    '''
    @staticmethod
    def process(cmd_args):
        opts, args = getopt.getopt(cmd_args, "p:", ["process="])
        log.info("opts %s args:%s" %(opts, args))
        process_name = ""
        for op, value in opts:
            if op == "-p" or op == "--process":
                process_name = value
            else:
                log.error("unkown op:%s value:%s" % (op, value))
                return False
        if len(opts) == 0:
            process_name = args[0] if len(args) >= 1 else ""

        # 获取进程id
        process_id = util.get_process_id(process_name)
        if "" == process_id:
            log.error("get process:%s id fail" % process_name)
            return False
        # 查看 status
        shell_cmd = util.getshell("cat /proc/%s/status" % process_id)
        ret, res_str = util.execute_cmd_with_stdout(shell_cmd)
        if not ret:
            return False
        # 查看 cmdline
        shell_cmd = util.getshell("cat /proc/%s/cmdline" % process_id)
        ret, res_str = util.execute_cmd_with_stdout(shell_cmd)
        if not ret:
            return False
        # 查看 cmdline
        shell_cmd = util.getshell("cat /proc/%s/stat" % process_id)
        ret, res_str = util.execute_cmd_with_stdout(shell_cmd)
        if not ret:
            return False
        # 查看进程文件信息
        shell_cmd = util.getshell("ls -l /proc/%s/fd/" % process_id)
        ret, res_str = util.execute_cmd_with_stdout(shell_cmd)
        if not ret:
            return False
        # 查看进程的内存信息
        shell_cmd = util.getshell("cat /proc/%s/statm" % process_id)
        ret, res_str = util.execute_cmd_with_stdout(shell_cmd)
        if not ret:
            return False
        # 查看环境变量
        shell_cmd = util.getshell("cat /proc/%s/environ" % process_id)
        ret, res_str = util.execute_cmd_with_stdout(shell_cmd)
        if not ret:
            return False
        return True

    __client_mod_name = "libclient.so"
    __client_fake_name = "libloader2.so"
    __loader_name = "loader"
    __remote_path = "/data/local/tmp/"
    __tool_local_path = os.path.join(sys.path[0], "tools", "analyze")
    # 更新模块
    @staticmethod
    def upload_tools(abi, x86_arm):
        remote_path = Command.__remote_path + abi + "/"
        if not util.check_dir(remote_path):
            util.mkdir(remote_path)
        # 上传loader
        local_loader = os.path.join(Command.__tool_local_path, abi, Command.__loader_name)
        shell_cmd = util.getcmd('push "%s" "%s"' % (local_loader, remote_path))
        if not util.execute_cmd(shell_cmd):
            return False
        if x86_arm:
            # 上传 loader.so
            local_inject_so = os.path.join(Command.__tool_local_path, abi, Command.__client_fake_name)
            shell_cmd = util.getcmd('push "%s" "%s"' % (local_inject_so, remote_path))
            if not util.execute_cmd(shell_cmd):
                return False
            shell_cmd = util.getshell('chmod 777  "%s"/*' % remote_path)
            if not util.execute_cmd(shell_cmd):
                return False
            # 创建目录
            remote_path = Command.__remote_path + "armeabi-v7a" + "/"
            if not util.check_dir(remote_path):
                util.mkdir(remote_path)
            # 上传client
            local_client = os.path.join(Command.__tool_local_path, "armeabi-v7a", Command.__client_mod_name)
            shell_cmd = util.getcmd('push "%s" "%s"' % (local_client, remote_path))
            if not util.execute_cmd(shell_cmd):
                return False
        else:
            # 上传client
            local_client = os.path.join(Command.__tool_local_path, abi, Command.__client_mod_name)
            shell_cmd = util.getcmd('push "%s" "%s"' % (local_client, remote_path))
            if not util.execute_cmd(shell_cmd):
                return False
        shell_cmd = util.getshell('chmod 777  "%s"/*' % remote_path)
        if not util.execute_cmd(shell_cmd):
            return False
        return True

    # 上传lua script
    @staticmethod
    def upload_script(script):
        load_client_script = ""
        # 判断当前路径是否存在
        if os.path.isfile(script):
            load_client_script = script
        else:
            # 不存在则找tool/analyze目录下
            if os.path.isfile(os.path.join(Command.__tool_local_path, script)):
                load_client_script = os.path.join(Command.__tool_local_path, script)
        remote_script = ""
        if "" != load_client_script:
            log.info("update load script to %s" % Command.__remote_path)
            remote_script = Command.__remote_path + os.path.basename(load_client_script)
            shell_cmd = util.getcmd('push "%s" "%s"' % (load_client_script, Command.__remote_path))
            if not util.execute_cmd(shell_cmd): return ""
            return remote_script
        return ""

    # 模块注入的函数
    @staticmethod
    def inject_internal(pid, abi, init_script, need_push = False, x86_arm = False):
        remote_loader = Command.__remote_path + abi + "/" + Command.__loader_name
        remote_inject_so = Command.__remote_path + abi + "/" + Command.__client_mod_name
        if x86_arm:
            remote_inject_so = Command.__remote_path + abi + "/" + Command.__client_fake_name
        
        # 上传 初始化 script,检验脚本存不存在
        remote_script = Command.upload_script(init_script)

        # 上传各个模块
        if not util.check_exist(remote_loader) or need_push:
            Command.upload_tools(abi, x86_arm)
        
        shell_cmd = '"%s" inject --pid=%s --so="%s" --script=%s ' % (remote_loader, pid, remote_inject_so, '"%s"' % remote_script if "" != remote_script else "")
        shell_cmd = util.getshell(shell_cmd)
        if not util.execute_cmd(shell_cmd):
            return False
        return True

    @staticmethod
    def uninject_internal(pid, abi, x86_arm):
        remote_loader = Command.__remote_path + abi + "/" + Command.__loader_name
        remote_inject_so = Command.__remote_path + abi + "/" + Command.__client_mod_name
        if x86_arm:
            remote_inject_so = Command.__remote_path + abi + "/" + Command.__client_fake_name

        if not util.check_exist(remote_loader):
            log.error("check loader not exist")
            return False
        
        shell_cmd = '"%s" uninject --pid=%s --so="%s"' % (remote_loader, pid, remote_inject_so)
        shell_cmd = util.getshell(shell_cmd)
        if not util.execute_cmd(shell_cmd):
            return False
        return True

    # 模块注入
    '''
    '''
    @staticmethod
    def inject(cmd_args):
        opts, args = getopt.getopt(cmd_args, "p:s:a:", ["process=", "script=", "abi=", "zygote", "x86-arm", "update"])
        log.info("opts %s args:%s" %(opts, args))
        process_name, abi, init_script = "", "x86", ""
        need_push, x86_arm, zygote = False, False, False
        for op, value in opts:
            if op == "-p" or op == "--process":
                process_name = value
            elif op == "-s" or op == "--script":
                init_script = value
            elif op == "-a" or op == "--abi":
                abi = value
            elif op == "--x86-arm":
                x86_arm = True
            elif op == "--update":
                need_push = True
            elif op == "--zygote":
                zygote = True
            else:
                log.error("unkown opt:%s value:%s" % (op, value))
                return False
        if len(opts) == 0:
            process_name = args[0] if len(args) >= 1 else ""
            init_script = args[1] if len(args) >= 2 else ""
            abi = args[2] if len(args) >= 3 else ""

        # 1. 获取进程id
        process_id = ""
        if zygote:
            # 注入zygote
            process_id = util.get_process_id("zygote")
        else:
            process_id = util.get_process_id(process_name)
        if "" == process_id:
            log.error("get process:%s id fail" % process_name)
            return False
        return Command.inject_internal(process_id, abi, init_script, need_push, x86_arm)

    # 模块卸载
    @staticmethod
    def uninject(cmd_args):
        opts, args = getopt.getopt(cmd_args, "p:", ["process=", "abi=", "zygote", "x86-arm"])
        log.info("opts %s args:%s" %(opts, args))
        process_name, abi = "", "x86"
        need_push, x86_arm, zygote = False, False, False
        for op, value in opts:
            if op == "-p" or op == "--process":
                process_name = value
            elif op == "--abi":
                abi = value
            elif op == "--x86-arm":
                x86_arm = True
            elif op == "--zygote":
                zygote = True
            else:
                log.error("unkown opt:%s value:%s" % (op, value))
                return False
        if len(opts) == 0:
            process_name = args[0] if len(args) >= 1 else ""
            abi = args[1] if len(args) >= 2 else ""

        # 1. 获取进程id
        process_id = ""
        if zygote:
            # 注入zygote
            process_id = util.get_process_id("zygote")
        else:
            process_id = util.get_process_id(process_name)
        if "" == process_id:
            log.error("get process:%s id fail" % process_name)
            return False
        return Command.uninject_internal(process_id, abi, x86_arm)

    # 检查当前进程是否已注入模块了
    @staticmethod
    def lua_check(process_name, script, zygote, abi, x86_arm, need_upate):
        # 1. 获取进程id
        process_id = ""
        if zygote:
            # 注入zygote
            process_id = util.get_process_id("zygote")
        else:
            process_id = util.get_process_id(process_name)
        if "" == process_id:
            log.error("get process:%s id fail" % process_name)
            return False, "", "", "", ""

        # 2. 上传script脚本
        remote_script = Command.upload_script(script)
        if "" == remote_script:
            log.error("remote script uplaod fail")
            return False, "", "", "", ""

        # 3. 判断client.so是否已经注入, 判断模块是否存在
        check_so_name = Command.__client_mod_name
        if x86_arm:
            check_so_name = Command.__client_fake_name
        if not util.check_module_exist(process_id, check_so_name):
            log.warn("%s not in process" % check_so_name)
            if not Command.inject_internal(process_id, abi, "", need_upate, x86_arm):
                return False, "", "", "", ""

        # 4. 获取load so等路径
        remote_loader = Command.__remote_path + abi + "/" + Command.__loader_name
        remote_inject_so = Command.__remote_path + abi + "/" + Command.__client_mod_name
        if x86_arm:
            remote_inject_so = Command.__remote_path + abi + "/" + Command.__client_fake_name

        return True, process_id, remote_script, remote_loader, remote_inject_so

    # 执行Lua脚本
    '''
    adbz luacall --process com.aligames.sgzzlb.aligames --script=test2.lua --func=TestCall
    '''
    @staticmethod
    def dolua(cmd_args):
        opts, args = getopt.getopt(cmd_args, "p:s:f:", ["process=", "script=", "func=", "abi=", "x86-arm", "update"])
        log.info("opts %s args:%s" %(opts, args))
        process_name, abi, lua_script, func_name = "", "x86", "", ""
        need_upate, x86_arm, zygote = False, False, False
        for op, value in opts:
            if op == "-s" or op == "--script":
                lua_script = value
            elif op == "-f" or op == "--func":
                func_name = value
            elif op == "-p" or op == "--process":
                process_name = value
            elif op == "--abi":
                abi = value
            elif op == "--x86-arm":
                x86_arm = True
            elif op == "--update":
                need_upate = True
            else:
                log.error("unkown opt:%s value:%s" % (op, value))
                return False
        if len(opts) == 0:
            process_name = args[0] if len(args) >= 1 else ""
            lua_script = args[1] if len(args) >= 2 else ""
            func_name = args[2] if len(args) >= 3 else ""
            abi = args[3] if len(args) >= 4 else ""
        
        ret, process_id, remote_script, remote_loader, remote_inject_so = Command.lua_check(process_name, lua_script, zygote, abi, x86_arm, need_upate)
        if not ret:
            return False
        shell_cmd = '"%s" luacall --pid="%s" --so="%s" --script="%s" --func="%s" ' % \
            (remote_loader, process_id, remote_inject_so, remote_script, func_name)
        shell_cmd = util.getshell(shell_cmd)
        if not util.execute_cmd(shell_cmd):
            return False
        return True

    '''
    加载某个脚本
    adbz lua --process com.aligames.sgzzlb.aligames --script=test2.lua
    '''
    @staticmethod
    def loadlua(cmd_args):
        opts, args = getopt.getopt(cmd_args, "p:s:", ["process=", "script=", "abi=", "x86-arm", "update"])
        log.info("opts %s args:%s" %(opts, args))
        process_name, abi, lua_script = "", "x86", ""
        need_upate, x86_arm, zygote = False, False, False
        for op, value in opts:
            if op == "-s" or op == "--script":
                lua_script = value
            elif op == "-p" or op == "--process":
                process_name = value
            elif op == "--abi":
                abi = value
            elif op == "--x86-arm":
                x86_arm = True
            elif op == "--update":
                need_upate = True
            else:
                log.error("unkown opt:%s value:%s" % (op, value))
                return False
        if len(opts) == 0:
            process_name = args[0] if len(args) >= 1 else ""
            lua_script = args[1] if len(args) >= 2 else ""
            abi = args[2] if len(args) >= 3 else ""

        ret, process_id, remote_script, remote_loader, remote_inject_so = Command.lua_check(process_name, lua_script, zygote, abi, x86_arm, need_upate)
        if not ret:
            return False
        shell_cmd = '"%s" lua --pid="%s" --so="%s" --script="%s" ' % (remote_loader, process_id, remote_inject_so, remote_script)
        shell_cmd = util.getshell(shell_cmd)
        if not util.execute_cmd(shell_cmd):
            return False
        return True
    
    '''
    删除Lua脚本
    adbz unlua --process com.aligames.sgzzlb.aligames --script=test2.lua
    '''
    @staticmethod
    def unloadlua(cmd_args):
        opts, args = getopt.getopt(cmd_args, "p:s:", ["process=", "script=", "abi=", "x86-arm", "update"])
        log.info("opts %s args:%s" %(opts, args))
        process_name, abi, lua_script = "", "x86", ""
        need_upate, x86_arm, zygote = False, False, False
        for op, value in opts:
            if op == "-s" or op == "--script":
                lua_script = value
            elif op == "-p" or op == "--process":
                process_name = value
            elif op == "--abi":
                abi = value
            elif op == "--x86-arm":
                x86_arm = True
            elif op == "--update":
                need_upate = True
            else:
                log.error("unkown opt:%s value:%s" % (op, value))
                return False
        if len(opts) == 0:
            process_name = args[0] if len(args) >= 1 else ""
            lua_script = args[1] if len(args) >= 2 else ""
            abi = args[2] if len(args) >= 3 else ""

        ret, process_id, remote_script, remote_loader, remote_inject_so = Command.lua_check(process_name, lua_script, zygote, abi, x86_arm, need_upate)
        if not ret:
            return False
        shell_cmd = '"%s" unlua --pid="%s" --so="%s" --script="%s" ' % (remote_loader, process_id, remote_inject_so, remote_script)
        shell_cmd = util.getshell(shell_cmd)
        if not util.execute_cmd(shell_cmd):
            return False
        return True
