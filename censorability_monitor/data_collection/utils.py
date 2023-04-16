from typing import List


def split_on_chunks(a: List, chunk_size: int):
    # looping till length l
    for i in range(0, len(a), chunk_size):
        yield a[i:i + chunk_size]
