import time
import psutil
import sys

from math import inf

_max_usage = inf
_process = psutil.Process()
_start_time = time.perf_counter()


def get_usage() -> 'float':
    ''' Returns memory usage of current process in MB. '''
    global _process
    return _process.memory_info().rss / (1024*1024)

def print_search_status(explored, frontier):
    status_template = '#Expanded: {:8,}, #Frontier: {:8,}, #Generated: {:8,}, Time: {:3.3f} s\n[Alloc: {:4.2f} MB, MaxAlloc: {:4.2f} MB]'
    elapsed_time = time.perf_counter() - _start_time
    print(
        status_template.format(
            len(explored),
            frontier.qsize(),
            len(explored) + frontier.qsize(),
            elapsed_time,
            get_usage(),
            _max_usage
        ),
        file=sys.stderr,
        flush=True
    )
