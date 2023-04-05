from __future__ import annotations


from pathlib import Path
from . import utils


class Workspace:
  def __init__(self, dir: str):
    self.dir = Path(dir).absolute()
    # make sure the workspace directory exists.
    self.dir.mkdir(exist_ok=True)

    self.src_dir = self.dir / 'src'
    self.src_dir.mkdir(exist_ok=True)

    self.bin_dir = self.dir / 'bin'
    self.bin_dir.mkdir(exist_ok=True)

    self.ir_dir = self.dir / 'ir'
    self.ir_dir.mkdir(exist_ok=True)

    self.suites = []

  def add_suite(self, suite: Suite):
    self.suites.append(suite)

  def acquire(self):
    for suite in self.suites:
      suite_source = self.src_dir / suite.name
      if not suite_source.exists():
        suite.acquire(suite_source)
        suite.configure(suite_source)

  def dump_benchmarks(self):
    for suite in self.suites:
      print(f'suite {suite.name}')
      for benchmark in suite.benchmarks:
        print(f'  {benchmark.name}')

  def compile(self):
    for suite in self.suites:
      suite_source = self.src_dir / suite.name
      suite_bin = self.bin_dir / suite.name
      suite_bin.mkdir(exist_ok=True)
      for benchmark in suite.benchmarks:
        benchmark.compile(suite_source, suite_bin / benchmark.name)

  def get_bitcode(self):
    for suite in self.suites:
      suite_ir = self.ir_dir / suite.name
      suite_ir.mkdir(exist_ok=True)
      suite_bin = self.bin_dir / suite.name
      suite_bin.mkdir(exist_ok=True)
      for benchmark in suite.benchmarks:
        benchmark_ir_dir = suite_ir / benchmark.name
        benchmark_ir_dir.mkdir(exist_ok=True)

        benchmark_bin = suite_bin / benchmark.name

        # defer to gclang, as usual
        utils.run_command(
            ['get-bc', '-o', benchmark_ir_dir / 'input.bc', benchmark_bin])
        utils.run_command(
            ['llvm-dis', benchmark_ir_dir / 'input.bc'])


class Suite:
  """
  A suite is a standard benchmark suite, which contains multiple Benchmark instances.
  The main functionality of a Suite is to fetch the contents of a benchmark, initialize
  the benchmark with patches or configuration, and to expose each benchmark as a
  `waterline.Benchmark` that can be put through the benchmarking pipeline defined by the
  user. A suite also defines how a benchmark is converted from bitcode to an executable.
  """

  def __init__(self, name: str):
    """
    Initialize the benchmark suite with a context and a name
    """
    self.name = name
    self.benchmarks: list[Benchmark] = []

  def acquire(self, path: Path):
    """
    Download, clone, or otherwise acquire the benchmark suite into a certain path.
    """
    print(f'acquire suite {self.name} to {path}')

  def configure(self, path: Path):
    """
    Autoconf, patch, or otherwise configure the suite
    """
    pass

  def add_benchmark(self, benchmark, name: str, **kwargs):
    self.benchmarks.append(benchmark(self, name, **kwargs))

# TODO:


class Runner:
  pass


class ShellRunner(Runner):
  pass


class TimeRunner(Runner):
  pass


class CondorRunner(Runner):
  pass


class Benchmark:
  def __init__(self, suite: Suite, name: str):
    self.suite = suite
    self.name = name

  def run(self, runner: Runner):
    pass

  def compile(self, suite_path: Path, output: Path):
    """
    Compile this benchmark to a certain output directory
    """
