
from pathlib import Path


class Runner:
    pass


class ShellRunner(Runner):
    pass


class TimeRunner(Runner):
    pass


class CondorRunner(Runner):
    pass


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

    def add_benchmark(self, benchmark, name: str, *args):
        self.benchmarks.append(benchmark(self, name, *args))

    def compile(self, suite_src: Path, suite_bin: Path):
        """
        Compile each of the benchmarks in the suite. By default this 
        simply defers to each benchmark, but it could do it some other
        way if the suite has a goofy build system.
        """
        for benchmark in self.benchmarks:
            bench_bin_dir = suite_bin / benchmark.name
            bench_bin_dir.mkdir(exist_ok=True)
            benchmark.compile(suite_src, bench_bin_dir / 'raw')


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

    def link(self, bitcode: Path, destination: Path):
        """
        Link a bitcode file of this benchmark into a complete executable.
        """
        print(f'link {bitcode} to {destination} not implemented')
