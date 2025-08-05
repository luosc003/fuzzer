import time
import sys
import random
from .corpus import Corpus
from .mutator import Mutator
from .runner import CoverageRunner
from .reporter import Reporter
from typing import Set


class Fuzzer:
    def __init__(
        self,
        runner: CoverageRunner,
        mutator: Mutator,
        corpus: Corpus,
        reporter: Reporter,
    ):
        self.runner = runner
        self.mutator = mutator
        self.corpus = corpus
        self.reporter = reporter
        self.total_executions = 0
        self.total_finds = 0
        self.start_time = 0
        self.global_coverage: Set[int] = set()

    def fuzz_loop(self, iterations: int):
        self.start_time = time.time()
        print("[*] Starting coverage-guided fuzzing loop...")

        for i in range(1, iterations + 1):
            seed = self.corpus.get_random_seed()
            num_mutations = random.randint(1, 8)
            mutated_data = self.mutator.mutate(seed, num_mutations)

            result = self.runner.run(mutated_data)
            self.total_executions += 1

            new_coverage = result.get("coverage", set())
            if new_coverage - self.global_coverage:
                print(
                    f"\n[+] New coverage found! {len(new_coverage - self.global_coverage)} new blocks. Total: {len(self.global_coverage | new_coverage)}"
                )
                self.global_coverage.update(new_coverage)
                self.corpus.add(mutated_data)

            if result["status"] not in ["ok", "fuzzer_error"]:
                is_new_crash_behavior = self.reporter.save_crash(mutated_data, result)
                if is_new_crash_behavior:
                    self.total_finds += 1
                    self.corpus.add(mutated_data)

            self.print_stats(len(self.corpus.seeds))

        print("\n[*] Fuzzing finished.")

    def print_stats(self, corpus_size: int):
        if self.total_executions % 100 != 0:
            return

        elapsed_time = time.time() - self.start_time
        exec_per_sec = self.total_executions / elapsed_time if elapsed_time > 0 else 0

        sys.stdout.write(
            f"\r[*] Iter: {self.total_executions} | "
            f"Corpus: {corpus_size} | "
            f"Finds: {self.total_finds} | "
            f"Coverage: {len(self.global_coverage)} BBs | "
            f"Speed: {exec_per_sec:.2f} exec/s"
        )
        sys.stdout.flush()
