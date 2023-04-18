from typing import Any, Generator, List


def split_on_chunks(a: List, chunk_size: int):
    # looping till length l
    for i in range(0, len(a), chunk_size):
        yield a[i:i + chunk_size]

def split_on_equal_chunks(a: List, n: int) -> Generator[List[Any], None, None]:
    if n <= 0:
        raise ValueError("Number of chunks should be greater than 0")
    
    chunk_size = len(a) // n
    remainder = len(a) % n
    start = 0

    for _ in range(n):
        end = start + chunk_size + (1 if remainder > 0 else 0)
        yield a[start:end]
        start = end
        remainder -= 1
