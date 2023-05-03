from pathlib import Path
import shutil
from .utils import shell
from .suite import Benchmark
from .linker import Linker
from . import jobs


def _should_run(input, output) -> bool:
    """Given an input and an output, check if the input is newer than the output"""
    return not output.exists() or output.stat().st_mtime < input.stat().st_mtime


class Stage:
    def run(self, input, output, benchmark):
        shutil.copy(input, output)


class OptStage(Stage):
    def __init__(self, passes=[]):
        self.passes = passes

    def run(self, input, output, benchmark):
        if _should_run(input, output):
            shell(f'opt {input} -o {output} {" ".join(self.passes)}')
            shell(f"llvm-dis {output}")


class NopStage(Stage):
    def run(self, input, output, benchmark):
        if _should_run(input, output) and input != output:
            shutil.copy(input, output)


class StageJob(jobs.Job):
    """
    A stage job simply runs a certain stage on a benchmark
    """

    def __init__(self, name, stage, input, output, bench):
        super().__init__(name)
        self.stage = stage
        self.in_bc = input
        self.out_bc = output
        self.benchmark = bench

    def run(self):
        self.stage.run(self.in_bc, self.out_bc, self.benchmark)


class LinkJob(jobs.Job):
    """
    A link job is a job that links benchmarks
    """

    def __init__(self, name, bench, input, output, linker):
        super().__init__(name)
        self.bench = bench
        self.input = input
        self.output = output
        self.linker = linker

    def run(self):
        if _should_run(self.input, self.output):
            self.bench.link_bitcode(self.input, self.output, self.linker)


class Pipeline:
    def __init__(self, name):
        self.name = name
        self.stages = []
        self.linker = None

    def set_linker(self, linker):
        self.linker = linker

    def add_stage(self, stage, name=None):
        self.stages.append((stage, name))

    def jobs(self, input_bc, output_bc, bench):
        io = []
        for i, (stage, name) in enumerate(self.stages):
            input = input_bc.parent / f"{self.name}-stage{i - 1}.bc"
            output = input_bc.parent / f"{self.name}-stage{i}.bc"
            if i == 0:
                input = input_bc
            if i == len(self.stages) - 1:
                output = output_bc
            io.append((input, output))

        linker = self.linker
        if linker is None:
            linker = Linker()

        for i, ((inp, outp), (stage, name)) in enumerate(zip(io, self.stages)):
            yield StageJob(f"stage {i+1}: {name}", stage, inp, outp, bench)

        # Create a link job
        yield LinkJob(
            f"link {bench.suite.name}/{bench.name}",
            bench,
            output_bc,
            bench.suite.bin / bench.name / self.name,
            linker,
        )
