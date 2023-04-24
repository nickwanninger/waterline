from dataclasses import dataclass
from pathlib import Path
import subprocess
import time
import waterline.utils
import os

class RunConfiguration:
    def __init__(self, name, args=[], env={}, cwd=None):
        self.name = name
        self.args = args
        self.env = env
        self.cwd = None

    def __repr__(self):
        return (
            f"RunConfiguration({self.name}, args={self.args}, dir={self.working_dir})"
        )


class Runner:
    name = "time"

    def run(self, workspace, config: RunConfiguration, binary: Path):
        """Run the benchmark, and return the metric. By default, it returns the execution time"""
        assert binary.exists()


        cwd = os.getcwd() if config.cwd is None else config.cwd
        with waterline.utils.cd(cwd):
            start = time.time()
            proc = subprocess.Popen(
                [binary, *config.args],
                stdout=subprocess.DEVNULL,
                # stderr=subprocess.DEVNULL,
                env=config.env,
                cwd=cwd,
            )
            res = proc.wait()
            # print(res)
            end = time.time()
        return end - start
