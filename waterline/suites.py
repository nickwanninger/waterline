from waterline import Suite, Benchmark, Workspace
from waterline.utils import run_command
from pathlib import Path
import waterline.utils
import shutil


class NASBenchmark(Benchmark):
  def compile(self, suite_path: Path, output: Path):
    """
    Compile this benchmark to a certain output directory
    """
    print(f'compile {self.name} to {output}')
    run_command(['make', '-C', suite_path, self.name.split('.')[0],
                f'CLASS={self.suite.suite_class}'])
    # if that compiled, copy the binary to the right location
    shutil.copy(suite_path / 'bin' / self.name, output)


class NAS(Suite):
  def __init__(self, enable_openmp: bool = True, suite_class: str = 'B'):
    super().__init__('NAS')
    self.enable_openmp = enable_openmp
    self.suite_class = suite_class

    # this is also hacky
    self.add_benchmark(NASBenchmark, 'bt.' + suite_class)
    self.add_benchmark(NASBenchmark, 'sp.' + suite_class)
    self.add_benchmark(NASBenchmark, 'lu.' + suite_class)
    self.add_benchmark(NASBenchmark, 'mg.' + suite_class)
    self.add_benchmark(NASBenchmark, 'ft.' + suite_class)
    self.add_benchmark(NASBenchmark, 'is.' + suite_class)
    self.add_benchmark(NASBenchmark, 'cg.' + suite_class)
    self.add_benchmark(NASBenchmark, 'ep.' + suite_class)

  def acquire(self, path: Path):
    waterline.utils.git_clone(
        'https://github.com/nickwanninger/NPB3.0-omp-C.git', path)

  def configure(self, path: Path):
    print('Configure NAS Parallel Benchmarks')
    # This is really gross. TODO: refactor this!
    (path / 'bin').mkdir(exist_ok=True)
    make_def_path = path / 'config' / 'make.def'
    with make_def_path.open('w') as cfg:
      cfg.write(f'CC    = gclang\n')
      cfg.write(f'CLINK = gclang\n')
      cfg.write(f'C_LIB = -lm\n')
      cfg.write(f'C_INC = -I../common\n')
      if self.enable_openmp:
        cfg.write(f'CFLAGS = -O3 -fPIC -fopenmp\n')
      else:
        cfg.write(f'CFLAGS = -O3 -fPIC\n')
      cfg.write('CLINKFLAGS = -fPIC -lm -fopenmp\n')
      cfg.write('UCC = cc -O\n')
      cfg.write('BINDIR	= ../bin\n')
      cfg.write('RAND	= randdp\n')
      cfg.write('WTIME	= wtime.c\n')


class GAPBenchmark(Benchmark):
  def compile(self, suite_path: Path, output: Path):
    """
    Compile this benchmark to a certain output directory
    """
    print(f'compile {self.name} to {output}')

    source_file = suite_path / 'src' / (self.name + '.cc')
    print(source_file)
    run_command(['gclang++', source_file, '-fopenmp', '-std=c++11',
                '-O3', '-Wall', '-o', output])


class GAP(Suite):
  def __init__(self, enable_openmp: bool = True):
    super().__init__('GAP')
    self.enable_openmp = enable_openmp

    self.add_benchmark(GAPBenchmark, 'bc')
    self.add_benchmark(GAPBenchmark, 'bfs')
    self.add_benchmark(GAPBenchmark, 'cc')
    self.add_benchmark(GAPBenchmark, 'cc_sv')
    self.add_benchmark(GAPBenchmark, 'converter')
    self.add_benchmark(GAPBenchmark, 'pr')
    self.add_benchmark(GAPBenchmark, 'pr_spmv')
    self.add_benchmark(GAPBenchmark, 'sssp')
    self.add_benchmark(GAPBenchmark, 'tc')

  def acquire(self, path: Path):
    waterline.utils.git_clone('https://github.com/sbeamer/gapbs.git', path)
