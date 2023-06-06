from waterline import Suite, Benchmark, Workspace, RunConfiguration, Linker
from waterline.utils import run_command
from pathlib import Path
import shutil



baseline_flags = [
    "-O1",
    "-Xclang",
    "-disable-llvm-passes",
    "-Xclang",
    "-disable-O0-optnone",
]

class SqliteTPCHBenchmark(Benchmark):
    def compile(self, output):
        self.shell(
            "gclang",
            *baseline_flags,
            self.suite.src / "sqlite3.c",
            self.suite.src / "driver.c",
            "-lm",
            "-ldl",
            "-Wno-implicit-function-declaration",
            "-o",
            output,
        )


    def link(self, object, output, linker):
        linker.link(
            self.suite.workspace,
            [object],
            output,
            args=["-ldl", "-pthread"],
        )

    def run_configs(self):
        for i in range(1, 23):
            print(i)
            yield RunConfiguration(f'Q{i}', args=[self.suite.src / "TPC-H.db", self.suite.src / f"queries/{i}.sql"])


class SqliteTPCH(Suite):
    name = "Sqlite-TPC-H"

    def configure(self):
        self.add_benchmark(SqliteTPCHBenchmark, "sqlite-tpch")
        pass

    def acquire(self):
        self.workspace.shell(
            "git",
            "clone",
            "--depth",
            "1",
            "https://github.com/nickwanninger/sqlite-tpch-bench.git",
            self.src,
        )

        # Make sure the right database is available
        self.workspace.shell(
            "make",
            "-C",
            self.src,
            "TPC-H.db",
        )
