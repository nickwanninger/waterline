from waterline import Suite, Benchmark, Workspace, RunConfiguration, Linker
from waterline.utils import run_command
from pathlib import Path


class GAPBenchmark(Benchmark):
    def compile(self, output: Path):
        source_file = self.suite.src / "src" / (self.name + ".cc")
        self.shell(
            "gclang++",
            source_file,
            "-fopenmp",
            "-std=c++11",
            "-O1",
            "-Wall",
            "-o",
            output,
        )

    def link(self, object: Path, output: Path, linker: Linker):
        # todo: use linker
        self.shell(
            "clang++",
            object,
            "-fopenmp",
            "-std=c++11",
            "-Wall",
            "-o",
            output,
        )

    def run_configs(self):
        yield RunConfiguration(self.name, args=["-g", "14"])


class GAP(Suite):
    name = "GAP"

    def configure(self, enable_openmp: bool = True):
        self.enable_openmp = enable_openmp

        self.add_benchmark(GAPBenchmark, "bc")
        self.add_benchmark(GAPBenchmark, "bfs")
        self.add_benchmark(GAPBenchmark, "cc")
        self.add_benchmark(GAPBenchmark, "cc_sv")
        # self.add_benchmark(GAPBenchmark, "converter")
        self.add_benchmark(GAPBenchmark, "pr")
        self.add_benchmark(GAPBenchmark, "pr_spmv")
        self.add_benchmark(GAPBenchmark, "sssp")
        self.add_benchmark(GAPBenchmark, "tc")

    def acquire(self):
        self.workspace.shell(
            "git",
            "clone",
            "--depth",
            "1",
            "https://github.com/sbeamer/gapbs.git",
            self.src,
        )
