import argparse
import sys
from fuzzer.core import Fuzzer
from fuzzer.corpus import Corpus
from fuzzer.mutator import Mutator
from fuzzer.runner import CoverageRunner
from fuzzer.reporter import Reporter

def main():
    parser = argparse.ArgumentParser(description="A coverage-guided fuzzer using DynamoRIO.")
    parser.add_argument("-D", "--dynamorio", required=True, help="Path to the DynamoRIO installation directory.")
    parser.add_argument("target", nargs='+', help="Target program and its arguments (e.g., ./my_app).")
    parser.add_argument("-i", "--input", required=True, help="Path to the input corpus directory.")
    parser.add_argument("-c", "--crashes", default="./crashes", help="Path to the directory to store crashes.")
    parser.add_argument("-n", "--iterations", type=int, default=10000, help="Number of fuzzing iterations.")
    parser.add_argument("-t", "--timeout", type=int, default=5, help="Timeout for each run in seconds.")
    
    args = parser.parse_args()

    try:
        corpus = Corpus(input_dir=args.input)
        corpus.load()

        mutator = Mutator()
        reporter = Reporter(crash_dir=args.crashes)
        runner = CoverageRunner(target_cmd=args.target, dynamorio_path=args.dynamorio, timeout=args.timeout)

        fuzzer = Fuzzer(runner, mutator, corpus, reporter)
        fuzzer.fuzz_loop(iterations=args.iterations)

    except (FileNotFoundError, ValueError) as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[*] Fuzzing stopped by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()