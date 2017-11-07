# JHVM

A small language written in RPython with a PyPy JIT.

## Installation
1. Clone jhvm:
`git clone https://github.com/jacob-hughes/jh-jit`

2. Get PyPy. Using Mercurial:
`hg clone http://bitbucket.org/pypy/pypy`

3. Add PyPy to your python path. `export PYTHONPATH=/path/to/pypy/`
4. Install the pip requirements `pip install -r requirements.txt`
5. Build a jhvm binary from the `jhvm.py` module. `python /path/to/pypy/rpython/bin/rpython --ouput <outname> jhvm.py`
    * Include `-Ojit` flag to translate with a JIT. This will take ≈5m on a high spec laptop so be patient and enjoy pretty mandelbrot drawing while you wait.

## Usage

Save your jhvm program with the `.jh` extension.

Compile it to bytecode:

`python compile.py example-prog.jh`

Run the bytecode:

`./<jhvm-bin-name> example-prog`

## Benchmarking

A benchmarking script is provided to measure the performance of the jit against a baseline (O1/O2 etc level optimisation). Note that this requires you to install [multitime](https://github.com/ltratt/multitime/).

Run it by passing the baseline and jit binaries as command-line args:

`python benchmark.py baseline jit`

Use `-d` to provide a directory of bytecode progs to benchmark. Defaults to `benchmarks/`



