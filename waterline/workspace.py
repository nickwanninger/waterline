from pathlib import Path
from .suite import Suite
from .utils import *
from .pipeline import *


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
            suite.compile(suite_source, suite_bin)


    def get_bitcode(self):
        for suite in self.suites:
            suite_ir = self.ir_dir / suite.name
            suite_ir.mkdir(exist_ok=True)
            suite_bin = self.bin_dir / suite.name
            suite_bin.mkdir(exist_ok=True)
            for benchmark in suite.benchmarks:
                benchmark_ir_dir = suite_ir / benchmark.name
                benchmark_ir_dir.mkdir(exist_ok=True)

                benchmark_bin = suite_bin / benchmark.name / 'raw'

                # defer to gclang, as usual
                run_command(
                    ['get-bc', '-o', benchmark_ir_dir / 'input.bc', benchmark_bin])
                run_command(
                    ['llvm-dis', benchmark_ir_dir / 'input.bc'])

    def run_pipeline(self, pipeline: Pipeline):
        for suite in self.suites:
          suite_ir = self.ir_dir / suite.name
          for benchmark in suite.benchmarks:
            benchmark_ir_dir = suite_ir / benchmark.name
            benchmark_ir_input = benchmark_ir_dir / 'input.bc'

            output = benchmark_ir_dir / f'{pipeline.name}.bc'
            pipeline.run(benchmark_ir_input, output, benchmark)
            benchmark_link_dest = self.bin_dir / suite.name / benchmark.name / pipeline.name
            benchmark.link(output, benchmark_link_dest)
