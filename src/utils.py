from time import perf_counter
from typing import Optional, Tuple

import numpy as np
import numpy.typing as npt


class Timer:
    def __init__(self, name: str):
        self.name = name
        self.time_start = perf_counter()

    def stop(self):
        """Stop the timer returning the elapsed time"""
        return perf_counter() - self.time_start

    def print(self):
        """Stop the timer and print the result"""
        print(f"Timer: {self.name} {perf_counter() - self.time_start}")


class TArray:
    def __init__(self, arr: Optional[np.NDarray[np.int_]] = None, info: int = None):
        self.arr = arr or {}
        self.info = info
        self.adv_info = {}

    def __setitem__(self, key, value):
        self.arr.__setitem__(key, value)

    def __getitem__(self, item):
        self.arr.__getitem__(item)
