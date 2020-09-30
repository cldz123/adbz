# adbz

#### 工具说明

在分析Android的app过程中，需要大量的使用到 adb 命令，但是如果开多个模拟器时，运行每个adb命令都需要加 `-s xxxxx`，表示对哪个模拟器操作。比如在木木模拟器上执行 `ps`

```
adb -s 127.0.0.1:7555 shell ps
```

如果用 `adbz`, 可以简化为如下命令

```
adbz shell ps
```

那如何改变 `-s xxxxx` 呢，在命令行中设置一下 `AdbConnect` 环境变量。在不同的命令行中将 `AdbConnect` 设置为不同的值，就能同时分析多个模拟器。
如果当前就一个模拟器，则可以将 `AdbConnect` 环境变量设置为空

```
set AdbConnect=127.0.0.1:56555
adbz shell ps
adbz shell cat /proc/xxx/maps
```

上面真正执行的是

```
adb -s 127.0.0.1:56555 shell ps
adb -s 127.0.0.1:56555 shell cat /proc/xxx/maps
```

adb shell 命令样式

目前遇到三种样式

```
:: 1、最常见的样式
adb shell ps  或 adb shell " ps "
:: 2、部分手机
adb shell "su -c ' ps '"
:: 3、部分手机
adb shell "su c ps "
```

可以通过设置 `AdbShell` 环境变量改变 `adb shell`命令样式，`0` 表示第一种，`1` 表示第二种，`2` 表示第三种。默认是第一种。

#### 前期准备

先下载到本地，并将工具目录加到 PATH 环境变量中。

#### 命令使用

##### 1、push 命令

主要三种用法

- 仅指定要上传的文件（相对路径）

```
adbz push dbgserver
```

将 `dbgserver` 上传到 `/data/local/tmp` 目录下，文件名为 `dbgserver`

- 指定上传的文件以及目的路径

```
adbz push dbgserver /data/other/path/
```

将 `dbgserver` 上传到 `/data/other/path` 目录下 文件名为 `dbgserver`

- 指定上传的文件以及目的路径以及文件名

```
adbz push dbgserver /data/other/android_x86_server
```

将 `dbgserver` 上传到 `/data/other` 目录下 文件名为 `android_x86_server`

##### 2、pull 命令

##### 3、shell 命令

跟正常执行 `adb shell xxx` 命令是一样的

```
adbz shell ps
```

需要在模拟器上执行多个命令时，需要引号包住。

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