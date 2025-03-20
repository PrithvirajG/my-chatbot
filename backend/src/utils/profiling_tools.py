import time
import functools
from loguru import logger

def measure_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record start time
        result = func(*args, **kwargs)  # Execute function
        end_time = time.time()  # Record end time

        logger.debug(f"{func.__name__} executed in {end_time - start_time:.6f} seconds")
        return result

    return wrapper
