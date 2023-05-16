from dataclasses import dataclass
from pathlib import Path
import subprocess
import time
import waterline.utils
import os
import resource
import pandas as pd
import multiprocessing as mp


class RunConfiguration:
    def __init__(self, name, args=[], env={}, cwd=None):
        self.name = name
        self.args = args
        self.env = env
        self.cwd = cwd


def _run(config, binary, send):
    cwd = os.getcwd() if config.cwd is None else config.cwd
    # print(f'run {config.name} in {cwd}')

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
        end = time.time()

    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    out = {}
    out["time"] = usage.ru_utime + usage.ru_stime
    out["stime"] = usage.ru_stime
    out["utime"] = usage.ru_utime
    out["major"] = usage.ru_majflt
    out["minor"] = usage.ru_minflt
    out["maxrss"] = usage.ru_maxrss
    out["status"] = res
    send.send(out)


class Runner:
    name = "time"

    def run(self, workspace, config, binary):
        """Run the benchmark, and return the metric. By default, it returns the execution time"""
        assert binary.exists()

        start = 0
        end = 0

        recv, send = mp.Pipe(False)
        p = mp.Process(target=_run, args=(config, binary, send))
        p.start()
        p.join()
        res = recv.recv()
        return res
