import sys

def deb(*msg: str):
    print(*msg, file=sys.stderr, flush=True)
