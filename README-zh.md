# PyFuzz-Hybrid: 混合式覆盖率引导模糊测试框架


一个用Python编写的模块化、覆盖率引导的灰盒模糊测试框架。本项目旨在通过将Python的高层逻辑与底层二进制插桩工具（DynamoRIO）相结合，来演示和实现一个现代化的Fuzzer。

这个项目非常适合对软件安全、漏洞挖掘和系统编程感兴趣安全爱好者。

## 核心架构

本Fuzzer采用一种高效的混合式架构，将不同语言和工具的优势最大化：

![fuzzer-en](https://luosc-1323779908.cos.ap-nanjing.myqcloud.com/obsidian/fuzzer-en.png)

1.  **Python (大脑)**: 负责所有高层逻辑，包括变异策略、语料库调度、崩溃报告和进化决策。
2.  **DynamoRIO (眼睛)**: 作为外部高性能的动态二进制插桩（DBI）引擎，它在不修改目标程序源码的情况下，实时监控其执行并生成代码覆盖率日志。
3.  **CoverageRunner (桥梁)**: Python模块，负责调用DynamoRIO执行目标程序，然后解析其输出的覆盖率日志，将关键信息（执行过的代码块）反馈给大脑。

## 功能特性

-   **覆盖率引导引擎**: 不再盲目碰撞，而是根据DynamoRIO反馈的新代码路径，智能地引导变异方向，高效探索程序深层逻辑。
-   **进化式语料库**: 自动将能触发新代码路径或新崩溃类型的“精英”输入添加到语料库中，实现遗传算法，持续进化。
-   **智能崩溃去重**: 通过创建“崩溃指纹” (`状态` + `返回码` + `关键错误信息`)，确保只报告和保存代表**全新程序行为**的样本，避免信息冗余。
-   **高度模块化**: 核心功能（`Mutator`, `Runner`, `Corpus`, `Reporter`）解耦，清晰易懂，便于扩展或替换其中任一模块。
-   **开箱即用**: 只需提供目标程序和初始种子，即可开始Fuzzing。

## 环境设置

1.  **Python 3**:
    -   确保你的系统已安装 Python 3.7 或更高版本。

2.  **C++ 编译器**:
    -   用于编译漏洞测试程序。推荐使用`g++`。
    -   `sudo apt-get install build-essential` (Debian/Ubuntu)

3.  **DynamoRIO**:
    -   从官方GitHub下载最新版本: [DynamoRIO Releases](https://github.com/DynamoRIO/dynamorio/releases)
    -   建议下载 `DynamoRIO-Linux-X.X.X.tar.gz` 版本。
    -   解压到一个固定的位置，例如 `~/dynamorio/`。为了方便使用，可以将其`bin64`目录添加到`PATH`环境变量。

## 如何使用

通过命令行启动Fuzzer，并提供必要的参数。

```bash
python3 main.py -D <path_to_dynamorio> -i <input_corpus> -c <crash_dir> -n <iterations> -- <target_program> [args...]
```

**参数说明**:
-   `-D, --dynamorio`: **(必须)** DynamoRIO的安装根目录路径 (例如 `~/dynamorio`)。
-   `target`: **(必须)** 目标程序及其参数。必须放在`--`之后。
-   `-i, --input`: **(必须)** 初始种子语料库的目录路径。
-   `-c, --crashes`: 保存独特崩溃样本的目录路径 (默认: `./crashes`)。
-   `-n, --iterations`: Fuzzing的最大迭代次数 (默认: `10000`)。
-   `-t, --timeout`: 每次执行的超时时间（秒）(默认: `5`)。

## 实战演练: 寻找整数溢出漏洞

1.  **准备漏洞程序**:
    将项目中的 `target_int_overflow.cpp` 进行编译。
    ```bash
    g++ target_int_overflow.cpp -o target_int_overflow -g
    ```

2.  **准备初始种子**:
    创建一个简单的种子文件。
    ```bash
    mkdir -p inputs
    echo -n "INIT" > inputs/seed.txt
    ```

3.  **启动 Fuzzer**:
    假设DynamoRIO的路径为 `~/dynamorio`。
    ```bash
    python3 main.py -D ~/dynamorio -i ./inputs -c ./crashes -n 50000 -- ./target_int_overflow
    ```

4.  **分析结果**:
    Fuzzer会持续运行，其状态行会显示语料库和覆盖率的增长。当它通过变异生成了 `\xff\xff` 作为输入的前两个字节时，就会触发漏洞。
    
    你会在控制台看到独特的崩溃报告：
    ```
    [!!!] UNIQUE BEHAVIOR DETECTED! Fingerprint: ('crash', -6, 'free(): corrupted size vs. prev_size')
    [*] Saved to 'crashes/UNIQUE_crash_rc-6_...'
    ```
    - 这条信息表示Fuzzer发现了一个返回码为-6 (`SIGABRT`) 的崩溃，其关键错误信息与`free()`函数有关，这是一个典型的堆损坏漏洞。
    - `crashes` 目录下会生成对应的 `.input` 和 `.log` 文件，供你使用`gdb`等工具进行深入的离线分析。
