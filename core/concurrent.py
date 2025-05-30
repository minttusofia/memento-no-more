import asyncio
from IPython.display import clear_output
import os
from typing import Callable, Iterable


async def parallel_map_with_limit(func: Callable, iterable: Iterable, max_concurrent: int):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def sem_task(item):
        async with semaphore:
            return await func(item)

    tasks = [asyncio.create_task(sem_task(item)) for item in iterable]
    return await asyncio.gather(*tasks)


class ConcurrentRunsMonitor:
    def __init__(self, overwrite: bool = True):
        self.overwrite = overwrite  # If False, will not clear terminal
        try:
            __IPYTHON__  # noqa
            self._ipython = True
        except NameError:
            self._ipython = False

    async def run(self):
        try:
            while True:
                self.display_progress()
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.display_progress()

    def clear_terminal(self):
        if self._ipython:
            clear_output(wait=True)
        else:
            os.system('cls' if os.name == 'nt' else 'clear')

    def display_progress(self):
        if self.overwrite:
            self.clear_terminal()


async def monitor(display_progress: Callable, *args, overwrite: bool = True):
    try:
        while True:
            display_progress(*args, overwrite=overwrite)
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        display_progress(*args, overwrite=overwrite)


def is_ipython():
    try:
        __IPYTHON__  # noqa
        return True
    except NameError:
        return False


def clear_terminal():
    if is_ipython():
        clear_output(wait=True)
    else:
        os.system('cls' if os.name == 'nt' else 'clear')
