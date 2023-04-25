from pathlib import Path
from .suite import Suite
from .pipeline import Pipeline, NopStage
from typing import Tuple, List, Dict, Optional
from . import jobs
import waterline.utils
import subprocess
from .run import Runner


class Workspace:
    suites: List[Suite] = []

    dir: Path
    src_dir: Path
    bin_dir: Path
    ir_dir: Path

    pipelines: Dict[str, Pipeline] = {}

    def __init__(self, dir: str):
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

    def run_pipeline(self, pipeline: Pipeline):
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

    def run(self, pipeline_names: Optional[List[str]] = None, runs=1, runner=Runner()):
        if pipeline_names is None:
            pipeline_names = self.pipelines.keys()

        pipelines: List[Pipeline] = [self.pipelines[name] for name in pipeline_names]

        for pl in pipelines:
            self.run_pipeline(pl)

        configs = []
        for benchmark in self.benchmarks():
            for config in benchmark.run_configs():
                configs.append((benchmark, config))
        print(f"benchmark,{','.join(map(lambda p: p.name, pipelines))}")
        for benchmark, config in configs:
            dir: Path = benchmark.suite.bin / benchmark.name
            for i in range(runs):
                times = []
                for pipeline in pipelines:
                    binary = dir / pipeline.name
                    if not binary.exists():
                        raise RuntimeError("binary does not exist!")
                    time = runner.run(self, config, binary)
                    times.append(time)
                print(
                    f"{benchmark.suite.name}.{config.name},{','.join(map(str, times))}"
                )

    def shell(self, *args):
        # print('running: ', *args)
        with open(self.dir / "output.txt", "a+") as out:
            out.write("\n\n")
            out.write("$ " + " ".join(map(str, args)) + "\n")
            out.flush()
            proc = subprocess.Popen(args, stdout=out, stderr=out)
            if not proc.wait() == 0:
                raise RuntimeError("failed to run", *args)
