# PyFuzz-Hybrid: A Coverage-Guided Fuzzing Framework

[[中文]](README-zh.md)
[[English]](README.md)

A modular, coverage-guided, gray-box fuzzing framework written in Python. This project aims to demonstrate and implement a modern fuzzer by combining the high-level logic of Python with a powerful, low-level binary instrumentation tool (DynamoRIO).

This project is ideal for students, researchers, and security enthusiasts interested in software security, vulnerability discovery, and systems programming.

## Core Architecture

This fuzzer employs an efficient hybrid architecture to maximize the advantages of different tools and languages:

![fuzzer-en](https://luosc-1323779908.cos.ap-nanjing.myqcloud.com/obsidian/fuzzer-en.png)

1.  **Python (The Brain)**: Handles all high-level logic, including mutation strategies, corpus scheduling, crash reporting, and evolutionary decisions.
2.  **DynamoRIO (The Eyes)**: Acts as a high-performance, external Dynamic Binary Instrumentation (DBI) engine. It monitors the target's execution and generates code coverage logs without needing to recompile the source code.
3.  **CoverageRunner (The Bridge)**: A Python module responsible for invoking the target program under DynamoRIO, then parsing the resulting coverage logs to feed critical information (executed basic blocks) back to the brain.

## Features

-   **Coverage-Guided Engine**: Intelligently steers the fuzzing process based on new code paths discovered via DynamoRIO, moving beyond blind mutations to efficiently explore deep program logic.
-   **Evolutionary Corpus**: Automatically adds "elite" inputs—those that trigger new code paths or unique crashes—to the corpus, enabling a genetic algorithm approach for continuous evolution.
-   **Smart Crash Deduplication**: Utilizes "crash fingerprints" (composed of `status` + `return code` + `key error message`) to ensure that only samples representing **novel program behaviors** are reported and saved.
-   **Highly Modular Design**: Core components (`Mutator`, `Runner`, `Corpus`, `Reporter`) are decoupled for clarity, easy maintenance, and extensibility.
-   **Out-of-the-Box**: Ready to start fuzzing once provided with a target binary and initial seeds.

## Setup & Dependencies

1.  **Python 3**:
    -   Ensure you have Python 3.7 or newer installed.

2.  **C++ Compiler**:
    -   Required for compiling the example targets. `g++` is recommended.
    -   On Debian/Ubuntu: `sudo apt-get install build-essential`

3.  **DynamoRIO**:
    -   Download the latest release from the official GitHub: [DynamoRIO Releases](https://github.com/DynamoRIO/dynamorio/releases)
    -   It's recommended to download a `DynamoRIO-Linux-X.X.X.tar.gz` package.
    -   Extract it to a stable location, e.g., `~/dynamorio/`. For convenience, you can add its `bin64` directory to your `PATH`.

## Usage

Launch the fuzzer from the command line with the required arguments.

```bash
python3 main.py -D <path_to_dynamorio> -i <input_corpus> -c <crash_dir> -n <iterations> -- <target_program> [args...]
```

**Arguments**:

-   `-D, --dynamorio`: **(Required)** The root path of your DynamoRIO installation (e.g., `~/dynamorio`).
-   `target`: **(Required)** The target program and its arguments. Must be placed after `--`.
-   `-i, --input`: **(Required)** Path to the initial seed corpus directory.
-   `-c, --crashes`: Path to the directory for storing unique crash samples (default: `./crashes`).
-   `-n, --iterations`: The maximum number of fuzzing iterations (default: `10000`).
-   `-t, --timeout`: Timeout in seconds for each execution run (default: `5`).

## Example Walkthrough: Finding an Integer Overflow Vulnerability

Let's use the fuzzer to find a heap overflow vulnerability caused by an integer overflow.

1.  **Prepare the Vulnerable Program**:
    Compile the `target_int_overflow.cpp` file included in this project.

    ```bash
    g++ target_int_overflow.cpp -o target_int_overflow -g
    ```

2.  **Prepare an Initial Seed**:
    Create a simple seed file.

    ```bash
    mkdir -p inputs
    echo -n "INIT" > inputs/seed.txt
    ```

3.  **Launch the Fuzzer**:
    Assuming DynamoRIO is located at `~/dynamorio`.

    ```bash
    python3 main.py -D ~/dynamorio -i ./inputs -c ./crashes -n 50000 -- ./target_int_overflow
    ```

4.  **Interpret the Results**:
    The fuzzer will run, and its status line will show the corpus and coverage growing over time. Eventually, it will generate an input where the first two bytes are `\xff\xff` (65535), triggering the vulnerability.

    A unique crash report will appear on your console:

    ```
    [!!!] UNIQUE BEHAVIOR DETECTED! Fingerprint: ('crash', -6, 'free(): corrupted size vs. prev_size')
    [*] Saved to 'crashes/UNIQUE_crash_rc-6_...'
    ```

    - **The Fingerprint**: `rc-6` (`SIGABRT`) combined with the `free()` error message clearly points to a heap corruption vulnerability.
    - **The `crashes` directory**: You will find the corresponding `.input` and `.log` files, which you can use for in-depth offline analysis with tools like `gdb`.