# adbz

#### 工具说明

在分析Android的app过程中，需要大量的使用到 adb 命令，但是如果开多个模拟器时，运行每个adb命令都需要加 `-s xxxxx`，表示对哪个模拟器操作。

比如在木木模拟器上执行 `ps`

```
adb -s 127.0.0.1:7555 shell ps
```
如果用 adbz

```
adbz shell ps
```

那如何改变 `-s xxxxx` 呢，在命令行中设置一下 `AdbConnect`环境变量。在不同的命令行中将`AdbConnect`设置为不同的值，就能同时分析多个模拟器。

```
set AdbConnect=127.0.0.1:56555
adb shell ps
adb shell cat /proc/xxx/maps
```

#### 前期准备

先下载到本地，并将工具目录加到 PATH 环境变量中。

#### 命令使用

##### 1、push 命令

省去输入 `-s xxxxx`，有部分省略参数

```
adbz push dbgserver
```

将 `dbgserver` 上传到 `/data/local/tmp` 目录下，文件名为 `dbgserver`

```
adbz push dbgserver /data/other/path/
```

将 `dbgserver` 上传到 `/data/other/path` 目录下 文件名为 `dbgserver`

```
adbz push dbgserver /data/other/android_x86_server
```

将 `dbgserver` 上传到 `/data/other` 目录下 文件名为 `android_x86_server`

##### 2、pull 命令

##### 3、shell 命令

```
adbz shell ps
```

多个命令时，需要引号包住。

```
adbz shell "ps | grep sgame"
```

##### 4、dump 命令

比如要dump 王者的 il2cpp 模块，运行如下命令

```
adbz dump com.tencent.tmgp.sgame libil2cpp.so
```

dump的分三步
- 找到进程id
- 获取模块的起始地址和大小
- 使用dd命令写入文件并pull下来