from pathlib import Path
from .run import RunConfiguration
from . import jobs
import shutil


class Suite:
    """
    A suite is a standard benchmark suite, which contains multiple Benchmark instances.
    The main functionality of a Suite is to fetch the contents of a benchmark, initialize
    the benchmark with patches or configuration, and to expose each benchmark as a
    `waterline.Benchmark` that can be put through the benchmarking pipeline defined by the
    user. A suite also defines how a benchmark is converted from bitcode to an executable.
    """

    name = "unknown"

    def __init__(self, workspace):
        """
        Initialize the benchmark suite with a context and a name
        """
        self.workspace = workspace
        self.benchmarks = []

        self.src = self.workspace.src_dir / self.name
        self.bin = self.workspace.bin_dir / self.name
        self.ir = self.workspace.ir_dir / self.name

    def configure(self, *args, **kwargs):
        """
        Called by the Workspace to initialize this benchmark suite with
        """
        pass

    def acquire(self):
        """
        Download, clone, or otherwise acquire the benchmark suite into a certain path.
        This function also emits
        """
        print(f"acquire suite {self.name} to {self.src}")

    def add_benchmark(self, benchmark, name, *args, **kwargs):
        self.benchmarks.append(benchmark(self, name, *args, **kwargs))

    def compile_jobs(self):
        """
        Compile each of the benchmarks in the suite. By default this
        simply defers to each benchmark, but it could do it some other
        way if the suite has a goofy build system.
        """

        for benchmark in self.benchmarks:
            bench_bin_dir = self.bin / benchmark.name
            bench_bin_dir.mkdir(exist_ok=True)

            bin_file = bench_bin_dir / "a.out"
            if not bin_file.exists():
                yield jobs.FunctionJob(
                    f"compile {self.name}/{benchmark.name}",
                    benchmark.compile,
                    bin_file,
                )

    def apply_patch(self, name):
        patches = Path(__file__).parent / "patches"
        shutil.copytree(patches / name, self.src, dirs_exist_ok=True)


class Benchmark:
    def __init__(self, suite, name):
        self.suite = suite
        self.name = name

    def __repr__(self):
        return f"Benchmark({self.suite.name},{self.name})"

    def run_configs(self):
        yield RunConfiguration(self.name)

    def compile(self, output):
        """
        Compile this benchmark to a certain output file
        """
        pass

    def link(self, object, destination, linker):
        """
        Link an object file of this benchmark into a complete executable.
        """
        print(f"link {object} to {destination} not implemented")

    def link_bitcode(self, bitcode, destination, linker):
        """
        Compile a bitcode file to an object file, then link the object file to the destination
        using `self.link()`
        """
        object = bitcode.parent / (bitcode.stem + ".o")
        self.shell(
            "llc",
            "-relocation-model=pic",
            "-O3",
            bitcode,
            "--filetype=obj",
            "-o",
            object,
        )

        self.link(object, destination, linker)
        pass

    def shell(self, *args, **kwargs):
        self.suite.workspace.shell(*args, **kwargs)
