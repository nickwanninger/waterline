from waterline import Suite, Benchmark, Workspace, Linker
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


polybench_benchmarks = [
    ("datamining/correlation/correlation.c", "correlation"),
    ("datamining/covariance/covariance.c", "covariance"),
    ("linear-algebra/kernels/2mm/2mm.c", "2mm"),
    ("linear-algebra/kernels/3mm/3mm.c", "3mm"),
    ("linear-algebra/kernels/atax/atax.c", "atax"),
    ("linear-algebra/kernels/bicg/bicg.c", "bicg"),
    ("linear-algebra/kernels/cholesky/cholesky.c", "cholesky"),
    ("linear-algebra/kernels/doitgen/doitgen.c", "doitgen"),
    ("linear-algebra/kernels/gemm/gemm.c", "gemm"),
    ("linear-algebra/kernels/gemver/gemver.c", "gemver"),
    ("linear-algebra/kernels/gesummv/gesummv.c", "gesummv"),
    ("linear-algebra/kernels/mvt/mvt.c", "mvt"),
    ("linear-algebra/kernels/symm/symm.c", "symm"),
    ("linear-algebra/kernels/syr2k/syr2k.c", "syr2k"),
    ("linear-algebra/kernels/syrk/syrk.c", "syrk"),
    ("linear-algebra/kernels/trisolv/trisolv.c", "trisolv"),
    ("linear-algebra/kernels/trmm/trmm.c", "trmm"),
    ("linear-algebra/solvers/durbin/durbin.c", "durbin"),
    ("linear-algebra/solvers/dynprog/dynprog.c", "dynprog"),
    ("linear-algebra/solvers/gramschmidt/gramschmidt.c", "gramschmidt"),
    ("linear-algebra/solvers/lu/lu.c", "lu"),
    ("linear-algebra/solvers/ludcmp/ludcmp.c", "ludcmp"),
    ("medley/floyd-warshall/floyd-warshall.c", "floyd-warshall"),
    ("medley/reg_detect/reg_detect.c", "reg_detect"),
    ("stencils/adi/adi.c", "adi"),
    ("stencils/fdtd-2d/fdtd-2d.c", "fdtd-2d"),
    ("stencils/fdtd-apml/fdtd-apml.c", "fdtd-apml"),
    ("stencils/jacobi-1d-imper/jacobi-1d-imper.c", "jacobi-1d-imper"),
    ("stencils/jacobi-2d-imper/jacobi-2d-imper.c", "jacobi-2d-imper"),
    ("stencils/seidel-2d/seidel-2d.c", "seidel-2d"),
]


class PolyBenchBenchmark(Benchmark):
    def __init__(self, suite, name, source):
        super().__init__(suite, name)
        self.source = source

    def compile(self, output):
        source_file = self.suite.src / self.source
        self.shell(
            "gclang",
            f"-D{self.suite.size}_DATASET",
            "-DPOLYBENCH_TIME",
            *baseline_flags,
            f"-I{self.suite.src}/utilities",
            f"-I{source_file.parent}",
            self.suite.src / "utilities" / "polybench.c",
            source_file,
            "-lm",
            "-Wno-implicit-function-declaration",
            "-o",
            output,
        )

    def link(self, object, output, linker):
        linker.link(self.suite.workspace, [object], output, args=["-lm"])


class PolyBench(Suite):
    name = "PolyBench"

    def configure(self, size="LARGE"):
        self.size = size
        for source, name in polybench_benchmarks:
            self.add_benchmark(PolyBenchBenchmark, name, source)

    def acquire(self):
        tarball = self.src.parent / "polybench-3.1.tar.gz"
        waterline.utils.download(
            "http://web.cse.ohio-state.edu/~pouchet.2/software/polybench/download/polybench-3.1.tar.gz",
            tarball,
        )

        shutil.unpack_archive(tarball, self.src.parent, "gztar")
        shutil.move(self.src.parent / "polybench-3.1", self.src)
