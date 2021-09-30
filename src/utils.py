from time import perf_counter


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
