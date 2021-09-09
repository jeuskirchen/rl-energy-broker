from concurrent.futures.thread import ThreadPoolExecutor
from typing import Callable

# FIXME : choose adequate pool size
executor = ThreadPoolExecutor(max_workers=8)

def run_async(function: Callable, *args) -> None:
    # TODO : check if the tasks actually complete
    executor.submit(function, *args)
