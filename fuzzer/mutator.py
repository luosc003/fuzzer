import random
import os
import struct

INTERESTING_VALUES = {
    1: [0, 1, 16, 32, 64, 128, 255],
    2: [0, 1, 256, 512, 1024, 32767, 65535],
    4: [0, 1, 2**31 - 1, 2**32 - 1],
}
INTERESTING_VALUES[2].extend([-v for v in INTERESTING_VALUES[2] if v != 0])
INTERESTING_VALUES[4].extend([-v for v in INTERESTING_VALUES[4] if v != 0])


class Mutator:
    def __init__(self):
        self.mutators = [
            self.delete_random_block,
            self.insert_random_block,
            self.flip_random_bit,
            self.swap_random_bytes,
            self.replace_with_interesting_value,
        ]

    def mutate(self, data: bytearray, num_mutations: int = 1) -> bytearray:
        mutated_data = data[:]
        for _ in range(num_mutations):
            if not mutated_data:
                mutated_data = bytearray(os.urandom(1))
            mutator_func = random.choice(self.mutators)
            mutated_data = mutator_func(mutated_data)
        return mutated_data

    def delete_random_block(self, data: bytearray) -> bytearray:
        if len(data) < 2:
            return data
        length = random.randint(1, int(len(data) / 2) + 1)
        start = random.randint(0, len(data) - length)
        del data[start : start + length]
        return data

    def insert_random_block(self, data: bytearray) -> bytearray:
        pos = random.randint(0, len(data))
        length = random.randint(1, 32)
        block = os.urandom(length)
        data[pos:pos] = block
        return data

    def flip_random_bit(self, data: bytearray) -> bytearray:
        if not data:
            return data
        pos = random.randint(0, len(data) - 1)
        bit = 1 << random.randint(0, 7)
        data[pos] ^= bit
        return data

    def swap_random_bytes(self, data: bytearray) -> bytearray:
        if len(data) < 2:
            return data
        pos1, pos2 = random.sample(range(len(data)), 2)
        data[pos1], data[pos2] = data[pos2], data[pos1]
        return data

    def replace_with_interesting_value(self, data: bytearray) -> bytearray:
        if len(data) < 4:
            return data
        pos = random.randint(0, len(data) - 4)
        size = random.choice([1, 2, 4])
        if pos + size > len(data):
            return data
        val = random.choice(INTERESTING_VALUES[size])
        try:
            packed_val = struct.pack(
                f'<{ {1: "B", 2: "H", 4: "I"}[size]}', val & ((1 << size * 8) - 1)
            )
            data[pos : pos + size] = packed_val
        except struct.error:
            pass
        return data
