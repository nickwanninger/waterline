from waterline import Suite, Benchmark, Workspace, RunConfiguration, Linker
from waterline.utils import run_command
from pathlib import Path
import waterline.utils
import shutil

baseline_flags = [
    "-O1",
    "-Xclang",
    "-disable-llvm-passes",
    "-Xclang",
    "-disable-O0-optnone",
]


class NASBenchmark(Benchmark):
    def compile(self, output):
        """
        Compile this benchmark to a certain output directory
        """
        self.shell(
            "make", "-C", self.suite.src, self.name, f"CLASS={self.suite.suite_class}"
        )
        # if that compiled, copy the binary to the right location
        compiled = self.suite.src / "bin" / (self.name + "." + self.suite.suite_class)
        shutil.copy(compiled, output)

    def link(self, object, dest, linker):
        # todo: use linker
        linker.link(
            self.suite.workspace, [object], dest, args=["-fPIC", "-lm", "-fopenmp"]
        )


class NAS(Suite):
    name = "NAS"

    def configure(self, enable_openmp=True, suite_class="B"):
        self.enable_openmp = enable_openmp
        self.suite_class = suite_class

        # this is also hacky
        self.add_benchmark(NASBenchmark, "bt")
        self.add_benchmark(NASBenchmark, "sp")
        self.add_benchmark(NASBenchmark, "lu")
        self.add_benchmark(NASBenchmark, "mg")
        self.add_benchmark(NASBenchmark, "ft")
        self.add_benchmark(NASBenchmark, "is")
        self.add_benchmark(NASBenchmark, "cg")
        self.add_benchmark(NASBenchmark, "ep")

    def acquire(self):
        self.workspace.shell(
            "git",
            "clone",
            "https://github.com/nickwanninger/NPB3.0-omp-C.git",
            self.src,
            "--depth",
            "1",
        )
        self.apply_patch("NAS")
        # This is really gross. TODO: refactor this!
        (self.src / "bin").mkdir(exist_ok=True)
        make_def_path = self.src / "config" / "make.def"
        with make_def_path.open("w") as cfg:
            cfg.write(f"CC    = gclang\n")
            cfg.write(f"CLINK = gclang\n")
            cfg.write(f"C_LIB = -lm\n")
            cfg.write(f"C_INC = -I../common\n")
            if self.enable_openmp:
                cfg.write(f"CFLAGS = {' '.join(baseline_flags)} -fPIC -fopenmp\n")
            else:
                cfg.write(f"CFLAGS = {' '.join(baseline_flags)} -fPIC\n")
            cfg.write("CLINKFLAGS = -fPIC -lm -fopenmp\n")
            cfg.write("UCC = cc -O\n")
            cfg.write("BINDIR	= ../bin\n")
            cfg.write("RAND	= randdp\n")
            cfg.write("WTIME	= wtime.c\n")
