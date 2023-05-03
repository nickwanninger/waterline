from waterline import Suite, Benchmark, Workspace, RunConfiguration, Linker
from waterline.utils import run_command
from pathlib import Path
import shutil


class StockfishBenchmark(Benchmark):
    def compile(self, output):
        source = self.suite.src / "src"
        self.shell(
            "make",
            "-j8",
            "ARCH=general-64",
            "COMP=gclang",
            "COMPCXX=gclang++",
            "EXTRACXXFLAGS=-O1",
            "debug=yes",
            "build",
            "-C",
            source,
        )
        shutil.copy(source / "stockfish", output)
        print(
            "NOTE: stockfish leads to 'errors' when running opt due to 'missing .incbin file'. These are benign and you can safely ignore them."
        )

    def link(self, object, output, linker):
        linker.link(
            self.suite.workspace,
            [object],
            output,
            args=["-fopenmp", "-lm", "-lstdc++", "-lpthread"],
        )

    def run_configs(self):
        yield RunConfiguration(self.name, args=["bench"])

    def link_bitcode(self, bitcode, destination, linker):
        object = bitcode.parent / (bitcode.stem + ".o")
        srcdir = self.suite.src / "src"
        nnue = "nn-e1fb1ade4432.nnue"

        self.shell(
            "llc",
            "-relocation-model=pic",
            "-O3",
            bitcode,
            "--filetype=obj",
            "-o",
            object,
            cwd=srcdir,
        )
        self.link(object, destination, linker)


class Stockfish(Suite):
    name = "Stockfish"

    def configure(self):
        self.add_benchmark(StockfishBenchmark, "stockfish")

    def acquire(self):
        self.workspace.shell(
            "git",
            "clone",
            "--depth",
            "1",
            "https://github.com/official-stockfish/Stockfish.git",
            self.src,
        )
        self.workspace.shell(
            "git",
            "-C",
            self.src,
            "checkout",
            "41f50b2c83a0ba36a2b9c507c1783e57c9b13485",
        )
        # Huge hack to get gclang working (replace all references to clang with gclang)
        self.workspace.shell("sed", "-i", "s/clang/gclang/g", self.src / "src/Makefile")
