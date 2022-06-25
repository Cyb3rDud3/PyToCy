import timeit
from statistics import median

def do_bench(func_name):
    module = __import__(func_name)
    n = 1
    durations = timeit.Timer(module.main).repeat(repeat=n, number=1)
    print(median(durations))

if __name__ == "__main__":
    do_bench('test')