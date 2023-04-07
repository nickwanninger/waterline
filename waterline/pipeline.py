from pathlib import Path
import shutil
from .suite import Benchmark
from . import jobs


class Pipeline:
    def __init__(self, name: str):
        self.name = name
        self.stages = []

    def add_stage(self, stage, name=None):
        self.stages.append((stage, name))

    def run(self, input_bc: Path, output_bc: Path, bench: Benchmark):
        shutil.copy(input_bc, output_bc)
        dir = output_bc.parent
        for i, stage in enumerate(self.stages):
            stage(output_bc)

    def create_jobs(self, input_bc: Path, output_bc: Path, bench: Benchmark):
        shutil.copy(input_bc, output_bc)

        out = []
        for i, (stage, name) in enumerate(self.stages):
            out.append(jobs.FunctionJob(f"stage {i+1}: {name}", stage, output_bc))
        return out
