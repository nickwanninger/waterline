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

  def link(self, bitcode: Path, dest: Path):
    run_command(['clang', '-lomp', bitcode, '-o', dest, '-lm', '-fopenmp'])


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

    source_file = suite_path / 'src' / (self.name + '.cc')
    print(source_file)
    run_command(['gclang++', source_file, '-fopenmp', '-std=c++11',
                '-O3', '-Wall', '-o', output])

  def link(self, bitcode: Path, output: Path):
    run_command(['gclang++', bitcode, '-fopenmp', '-std=c++11',
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


polybench_benchmarks: tuple[str, str] = [
    ('datamining/correlation/correlation.c', 'correlation'),
    ('datamining/covariance/covariance.c', 'covariance'),
    ('linear-algebra/kernels/2mm/2mm.c', '2mm'),
    ('linear-algebra/kernels/3mm/3mm.c', '3mm'),
    ('linear-algebra/kernels/atax/atax.c', 'atax'),
    ('linear-algebra/kernels/bicg/bicg.c', 'bicg'),
    ('linear-algebra/kernels/cholesky/cholesky.c', 'cholesky'),
    ('linear-algebra/kernels/doitgen/doitgen.c', 'doitgen'),
    ('linear-algebra/kernels/gemm/gemm.c', 'gemm'),
    ('linear-algebra/kernels/gemver/gemver.c', 'gemver'),
    ('linear-algebra/kernels/gesummv/gesummv.c', 'gesummv'),
    ('linear-algebra/kernels/mvt/mvt.c', 'mvt'),
    ('linear-algebra/kernels/symm/symm.c', 'symm'),
    ('linear-algebra/kernels/syr2k/syr2k.c', 'syr2k'),
    ('linear-algebra/kernels/syrk/syrk.c', 'syrk'),
    ('linear-algebra/kernels/trisolv/trisolv.c', 'trisolv'),
    ('linear-algebra/kernels/trmm/trmm.c', 'trmm'),
    ('linear-algebra/solvers/durbin/durbin.c', 'durbin'),
    ('linear-algebra/solvers/dynprog/dynprog.c', 'dynprog'),
    ('linear-algebra/solvers/gramschmidt/gramschmidt.c', 'gramschmidt'),
    ('linear-algebra/solvers/lu/lu.c', 'lu'),
    ('linear-algebra/solvers/ludcmp/ludcmp.c', 'ludcmp'),
    ('medley/floyd-warshall/floyd-warshall.c', 'floyd-warshall'),
    ('medley/reg_detect/reg_detect.c', 'reg_detect'),
    ('stencils/adi/adi.c', 'adi'),
    ('stencils/fdtd-2d/fdtd-2d.c', 'fdtd-2d'),
    ('stencils/fdtd-apml/fdtd-apml.c', 'fdtd-apml'),
    ('stencils/jacobi-1d-imper/jacobi-1d-imper.c', 'jacobi-1d-imper'),
    ('stencils/jacobi-2d-imper/jacobi-2d-imper.c', 'jacobi-2d-imper'),
    ('stencils/seidel-2d/seidel-2d.c', 'seidel-2d')
]


class PolyBenchBenchmark(Benchmark):
  def __init__(self, suite, name, source):
    super().__init__(suite, name)
    self.source = source

  def compile(self, suite_path: Path, output: Path):
    source_file = suite_path / self.source
    print(source_file)

    run_command(['gclang', '-DLARGE_DATASET', '-DPOLYBENCH_TIME', '-O1', '-Xclang', '-disable-llvm-passes', '-Xclang', '-disable-O0-optnone', f'-I{suite_path}/utilities', f'-I{source_file.parent}',
                suite_path / 'utilities' / 'polybench.c', source_file, '-lm', '-Wno-implicit-function-declaration',  '-o', output])

  def link(self, bitcode: Path, output: Path):
    run_command(['gclang', bitcode, '-lm', '-o', output])


class PolyBench(Suite):
  def __init__(self):
    super().__init__('PolyBench')
    for source, name in polybench_benchmarks:
      self.add_benchmark(PolyBenchBenchmark, name, source)

  def acquire(self, path: Path):
    tarball = path.parent / 'polybench-3.1.tar.gz'
    print('get poybench to', path)
    waterline.utils.download(
        'http://web.cse.ohio-state.edu/~pouchet.2/software/polybench/download/polybench-3.1.tar.gz', tarball)

    shutil.unpack_archive(tarball, path.parent, 'gztar')
    shutil.move(path.parent / 'polybench-3.1', path)
    # waterline.utils.shell(f'tar xf {out} -C {path.parent}')

    # shutil.(out / 'polybench-3.1', path)
