from pathlib import Path
from .suite import Suite
from .pipeline import Pipeline, NopStage
from . import jobs
import waterline.utils
import subprocess
from .run import Runner

from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
    MofNCompleteColumn,
)

import pandas as pd


class Workspace:
    suites = []

    dir = None
    src_dir = None
    bin_dir = None
    ir_dir = None

    pipelines = {}

    def __init__(self, dir):
        self.dir = Path(dir).absolute()
        # make sure the workspace directory exists.
        self.dir.mkdir(exist_ok=True)

        self.src_dir = self.dir / "src"
        self.src_dir.mkdir(exist_ok=True)

        self.bin_dir = self.dir / "bin"
        self.bin_dir.mkdir(exist_ok=True)

        self.ir_dir = self.dir / "ir"
        self.ir_dir.mkdir(exist_ok=True)

        baseline = Pipeline("baseline")
        baseline.add_stage(NopStage())
        self.add_pipeline(baseline)

    def benchmarks(self):
        """iterate over each benchmark"""
        for suite in self.suites:
            for bench in suite.benchmarks:
                yield bench

    def add_suite(self, suite, *args, **kwargs):
        s = suite(self)
        s.configure(*args, **kwargs)
        self.suites.append(s)

    def dump_benchmarks(self):
        for suite in self.suites:
            print(f"suite {suite.name}")
            for benchmark in suite.benchmarks:
                print(f"  {benchmark.name}")

    def extract_bitcode(self, input, output):
        self.shell("get-bc", "-o", output, input)
        self.shell("llvm-dis", output)

    def add_pipeline(self, pipeline):
        self.pipelines[pipeline.name] = pipeline

    def clear_pipelines(self):
        self.pipelines = {}

    def prepare(self):
        """Prepare this workspace to have bitcode pipeline applied."""

        with waterline.utils.cd(self.dir):
            # a list of jobs to work on. This will be appended to and
            # worked through before a pipeline can run.
            runner = jobs.JobRunner()

            # first, make sure all the benchmarks are acquired. We just do this by
            # checking if the directory of the suite exists.
            for suite in self.suites:
                if not suite.src.exists():
                    runner.add(jobs.FunctionJob(f"acquire {suite.name}", suite.acquire))
            runner.title = "acquire suites"
            runner.run(parallel=True)

            # second, compile the a.out files for each benchmark suite. If the a.out
            # file doesn't exist, add it to the job list.
            for suite in self.suites:
                suite_bin = self.bin_dir / suite.name
                suite_bin.mkdir(exist_ok=True)
                for job in suite.compile_jobs():
                    runner.add(job)
            runner.title = "compile baseline"
            runner.run(parallel=True)

            # Third, make sure input.bc exists in each ir/<suite>/<benchmark>/ folder
            for suite in self.suites:
                suite_ir = self.ir_dir / suite.name
                suite_ir.mkdir(exist_ok=True)
                suite_bin = self.bin_dir / suite.name
                suite_bin.mkdir(exist_ok=True)
                for benchmark in suite.benchmarks:
                    benchmark_ir_dir = suite_ir / benchmark.name
                    benchmark_ir_dir.mkdir(exist_ok=True)

                    input = suite_bin / benchmark.name / "a.out"
                    output = benchmark_ir_dir / "input.bc"
                    if not output.exists():
                        runner.add(
                            jobs.FunctionJob(
                                f"extract {suite.name}/{benchmark.name}",
                                self.extract_bitcode,
                                input,
                                output,
                            )
                        )
            runner.title = "extract bitcode"
            runner.run()

    def run_pipeline(self, pipeline):
        """Run a pipeline over the bitcodes of each benchmark in this workspace"""
        # Make sure everything is setup!
        self.prepare()

        with waterline.utils.cd(self.dir):
            # Now run the pipeline on every benchmark's IR
            runner = jobs.JobRunner(f"pipeline: {pipeline.name}")

            for suite in self.suites:
                suite_ir = self.ir_dir / suite.name
                for benchmark in suite.benchmarks:
                    benchmark_ir_dir = suite_ir / benchmark.name
                    benchmark_ir_input = benchmark_ir_dir / "input.bc"

                    output = benchmark_ir_dir / f"{pipeline.name}.bc"

                    for job in pipeline.jobs(benchmark_ir_input, output, benchmark):
                        runner.add(job)

            runner.run(parallel=False)

    def run(
        self,
        pipeline_names=None,
        runs=1,
        runner=Runner(),
        compile=True,
    ):
        if pipeline_names is None:
            pipeline_names = self.pipelines.keys()

        pipelines = [self.pipelines[name] for name in pipeline_names]

        if compile:
            for pl in pipelines:
                self.run_pipeline(pl)

        configs = []
        for benchmark in self.benchmarks():
            for config in benchmark.run_configs():
                configs.append((benchmark, config))

        results = {"suite": [], "benchmark": [], "config": []}

        title = "Running"
        with Progress(
            # TaskProgressColumn(),
            TimeElapsedColumn(),
            TextColumn(f"{title:20s}"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task(
                "Running", total=len(configs) * runs * len(pipelines)
            )

            for benchmark, config in configs:
                dir: Path = benchmark.suite.bin / benchmark.name
                for pipeline in pipelines:
                    for i in range(runs):
                        binary = dir / pipeline.name
                        if not binary.exists():
                            continue
                            # raise RuntimeError("binary does not exist!")
                        progress.update(
                            task,
                            description=f"{benchmark.suite.name}.{benchmark.name} | {pipeline.name} | {i}/{runs}",
                        )
                        out = runner.run(self, config, binary)
                        progress.update(task, advance=1, description="")

                        results["suite"].append(benchmark.suite.name)
                        results["benchmark"].append(
                            config.name
                        )  # config.name is the name of the variant of the benchmark
                        results["config"].append(pipeline.name)
                        for key in out:
                            if key not in results:
                                results[key] = []
                            results[key].append(out[key])
        return pd.DataFrame(results)

    def shell(self, *args, **kwargs):
        # print('running: ', *args)
        with open(self.dir / "output.txt", "a+") as out:
            out.write("\n\n")
            out.write("$ " + " ".join(map(str, args)) + "\n")
            out.flush()
            proc = subprocess.Popen(args, stdout=out, stderr=out, **kwargs)
            if not proc.wait() == 0:
                raise RuntimeError("failed to run", *args)
