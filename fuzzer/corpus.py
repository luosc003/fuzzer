import os
import random
from typing import List


class Corpus:
    def __init__(self, input_dir: str):
        self.input_dir = input_dir
        self.seeds: List[bytearray] = []

    def load(self):
        if not os.path.isdir(self.input_dir):
            raise FileNotFoundError(
                f"Input corpus directory not found: {self.input_dir}"
            )

        print(f"[*] Loading seeds from '{self.input_dir}'...")
        for filename in os.listdir(self.input_dir):
            path = os.path.join(self.input_dir, filename)
            if os.path.isfile(path):
                with open(path, "rb") as f:
                    self.seeds.append(bytearray(f.read()))

        if not self.seeds:
            raise ValueError(f"No seeds found in '{self.input_dir}'.")

        print(f"[*] Loaded {len(self.seeds)} seeds.")

    def get_random_seed(self) -> bytearray:
        return random.choice(self.seeds)

    def add(self, data: bytearray):
        self.seeds.append(data)
