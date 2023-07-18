from waterline import Suite, Benchmark, Workspace, RunConfiguration, Linker
from waterline.utils import run_command
from pathlib import Path


class GAPBenchmark(Benchmark):
    def compile(self, output):
        source_file = self.suite.src / "src" / (self.name + ".cc")

        args = []

        if not self.suite.enable_exceptions:
            args.append("-fno-exceptions")
        if self.suite.enable_openmp:
            args.append("-fopenmp")
        self.shell(
            "gclang++",
            source_file,
            "-std=c++11",
            "-O1",
            "-Wall",
            *args,
            "-o",
            output,
        )

    def link(self, object, output, linker):
        linker.link(
            self.suite.workspace,
            [object],
            output,
            args=["-fopenmp", "-lm", "-lstdc++", "-lpthread"],
        )

    def run_configs(self):

        yield RunConfiguration(self.name, args=["-g", self.suite.graph_size])


class GAP(Suite):
    name = "GAP"

    def configure(self, enable_openmp=True, enable_exceptions=True, graph_size=14):
        self.enable_openmp = enable_openmp
        self.enable_exceptions = enable_exceptions
        self.graph_size = graph_size

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
