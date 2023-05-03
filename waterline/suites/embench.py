from waterline import Suite, Benchmark, Workspace, Linker
from waterline.utils import run_command
from pathlib import Path
import waterline.utils
import shutil
import os


baseline_flags = [
    "-O1",
    "-Xclang",
    "-disable-llvm-passes",
    "-Xclang",
    "-disable-O0-optnone",
]


class EmbenchBenchmark(Benchmark):
    def __init__(self, suite, name, source):
        super().__init__(suite, name)
        self.source = source

    def compile(self, output):
        source = self.suite.src / "src" / self.source

        source_files = [
            f"{self.suite.src}/config/native/boards/default/boardsupport.c",
            f"{self.suite.src}/config/native/chips/default/chipsupport.c",
            f"{self.suite.src}/config/native/chips/default/chipsupport.c",
            f"{self.suite.src}/support/beebsc.c",
            f"{self.suite.src}/support/main.c",
        ]
        for filename in os.listdir(source):
            _, ext = os.path.splitext(filename)
            if ext == ".c":
                source_files.append(source / filename)

        self.shell(
            "gclang",
            "-fdata-sections",
            "-ffunction-sections",
            f"-I{self.suite.src}/support",
            f"-I{self.suite.src}/config/native/boards/default",
            f"-I{self.suite.src}/config/native/chips/default",
            f"-I{self.suite.src}/config/native",
            "-lm",
            "-gdwarf-2",
            f"-DITERATIONS={self.suite.iters}",
            "-DCPU_MHZ=1",
            "-DWARMUP_HEAT=1",
            *baseline_flags,
            *source_files,
            "-o",
            output,
        )

    def link(self, object, output, linker):
        linker.link(self.suite.workspace, [object], output, args=["-lm"])


benches = [
    "matmult-int",
    "crc32",
    "huffbench",
    "statemate",
    "minver",
    "slre",
    "edn",
    "nbody",
    "tarfind",
    "cubic",
    "aha-mont64",
    "primecount",
    "picojpeg",
    "st",
    "nsichneu",
    "ud",
    "nettle-aes",
    "wikisort",
    "sglib-combined",
    "qrduino",
    "md5sum",
    "nettle-sha256",
]


class Embench(Suite):
    name = "Embench"

    def configure(self, iters=10000):
        self.iters = iters
        for source in benches:
            self.add_benchmark(EmbenchBenchmark, source, source)

    def acquire(self):
        self.workspace.shell(
            "git",
            "clone",
            "https://github.com/embench/embench-iot.git",
            self.src,
            "--depth",
            "1",
        )
        self.apply_patch("Embench")
