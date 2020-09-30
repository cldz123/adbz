#--*-- coding:utf-8 --*--

import os
import log
import util

class Command:
    
    # 命令执行的一些配置

    @staticmethod
    def pull(opts, args):
        log.info(str(args))
        return True
    
    @staticmethod
    def push(opts, args):
        log.info(str(args))

        return True

    @staticmethod
    def shell(args):
        shell_cmd = util.Adb.getshell(args)
        log.info(shell_cmd)
        util.execute_cmd(shell_cmd)
        return True

    @staticmethod
    def get_process_id(process_name):
        # 获取进程id
        shell_cmd = util.Adb.getshell("ps | grep %s" % process_name)
        ret, res_str = util.execute_cmd_with_stdout(shell_cmd)
        if not ret:
            return ""
        if process_name not in res_str:
            shell_cmd = util.Adb.getshell("ps -A | grep %s" % process_name)
            ret, res_str = util.execute_cmd_with_stdout(shell_cmd)
            if not ret:
                return ""
        if process_name not in res_str:
            return ""
        res_str_list = res_str.split("\n")
        process_info = []
        for res_str in res_str_list:
            process_line = [r.strip() for r in res_str.split(" ") if r.strip() != ""]
            if process_name in process_line:
                process_info = process_line
        if 2 >= len(process_info):
            return ""
        return process_info[1]

    @staticmethod
    def dump(args):
        if 2 != len(args):
            return False
        process_name = args[0]
        module_name = args[1]

        # 获取进程id
        process_id = Command.get_process_id(process_name)
        if "" == process_id:
            return False

        # 获取模块信息 基地址和大小
        shell_cmd = util.Adb.getshell("cat /proc/%s/maps | grep %s" % (process_id, module_name))
        ret, res_str = util.execute_cmd_with_stdout(shell_cmd)
        if not ret:
            return False
        if module_name not in res_str:
            log.info("未找到模块")
            return False
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

        # 模块dump
        multi_module = (len(module_info_list) != 1)
        for mi in module_info_list:
            # 得到模块起始地址和结束地址，计算大小
            module_size = (int(mi[1], 16) - int(mi[0], 16))
            module_base = int(mi[0], 16)
            module_name_elems = os.path.splitext(module_name)
            module_save_name = module_name
            if multi_module:
                if len(module_name_elems) > 1:
                    module_save_name = "".join(module_name_elems[:-1]) + "_" + mi[0] + module_name_elems[-1]
                else:
                    module_save_name = module_save_name + "_" + mi[0]
            log.info("base:%08x size:%08x name:%s" % (module_base, module_size, module_save_name))
            cbs = 1
            if module_size > 0x10000:
                cbs = 1024
                while True:
                    if module_size % cbs:
                        cbs = cbs // 4
                    else:
                        break
            module_size = module_size // cbs
            # dd if=/proc/32909/mem skip=2589069312 count=274432 bs=1 of=/data/local/tmp/1
            shell_cmd = util.Adb.getshell("dd if=/proc/%s/mem skip=%d count=%d bs=%s of=/data/local/tmp/%s" % (process_id, module_base, module_size, cbs, module_save_name))
            ret, res_str = util.execute_cmd_with_stdout(shell_cmd)
            if not ret:
                return False
            shell_cmd = util.Adb.getcmd("pull /data/local/tmp/%s %s" % (module_save_name, module_save_name))
            ret, res_str = util.execute_cmd_with_stdout(shell_cmd)
            if not ret:
                return False
            shell_cmd = util.Adb.getshell("rm -rf /data/local/tmp/%s" % module_save_name)
            ret, res_str = util.execute_cmd_with_stdout(shell_cmd)
            if not ret:
                return False
        return True
    
    @staticmethod
    def module():
        # 获取进程id
        process_id = Command.get_process_id(process_name)
        if "" == process_id:
            return False

        return True

    @staticmethod
    def process():
        pass

    
    # 模块注入 
    @staticmethod
    def inject():
        pass

    # 执行Lua脚本
    @staticmethod
    def do_lua():
        pass

    # 模块卸载
    @staticmethod
    def uninject():
        pass
