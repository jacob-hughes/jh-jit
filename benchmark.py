# vim: ai ts=4 sts=4 et sw=4
# -*- coding: utf-8 -*-
import os
import math
import sys

from subprocess import Popen, PIPE
from progress.bar import Bar
from tabulate import tabulate

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
BENCHMARK_DIR = os.path.join(PROJECT_ROOT, 'benchmarks/')
JIT_BIN_PATH = os.path.join(PROJECT_ROOT, 'jhvm-c-jit')
NO_JIT_BIN_PATH = os.path.join(PROJECT_ROOT, 'jhvm-c-o2')



def main():
    benchmarks = get_benchmarks()

    if len(sys.argv) < 3:
        return usage()

    baseline = sys.argv[1] if '/' in sys.argv[1] else './%s' % sys.argv[1]
    comparable = sys.argv[2] if '/' in sys.argv[2] else './%s' % sys.argv[2]
    print run_benchmarks(benchmarks, (baseline, comparable))

def usage():
    print 'Usage: python benchmark.py <baseline> <comparable_binary>'
    return 1

def get_benchmarks():
    files = os.listdir(BENCHMARK_DIR)
    return [f for f in files if f[-3:] != '.jh']

def run_benchmarks(benchmarks, bins):
    headers = ['benchmark', 'baseline', 'jit', 'perf. diff']
    bar = Bar('running benchmarks', max=(len(benchmarks) * len(bins)))
    table = []

    def _get_mean(multitime_stderr):
        real_time_ln = multitime_stderr.splitlines()[3]
        mean_real = real_time_ln.split()[1]
        return float(mean_real)

    def _multitime(binary, benchmark):
        cmd  = ['multitime', binary, os.path.join(BENCHMARK_DIR, benchmark)]
        p = Popen(cmd, stdout = PIPE, stderr = PIPE)
        p.wait()
        out, err = p.communicate()
        bar.next()
        return err

    for benchmark in benchmarks:
        baseline, comparable = [_get_mean(_multitime(binary, benchmark)) for binary in bins]
        diff = (baseline / comparable) * 100
        table.append([benchmark, '%ss' % baseline, '%ss' % comparable, '%s%%' % diff])

    bar.finish()
    return tabulate(table, headers)


if __name__ == '__main__':
    main()



