from pathlib import Path
import subprocess
import requests
from contextlib import contextmanager
import os


@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def run_command(args):
    proc = subprocess.Popen(args)
    proc.wait()


def shell(cmd):
    run_command(["sh", "-c", cmd])


def git_clone(url, destination):
    shell(f"git clone {url} {destination} --depth 1")


def download(url, output):
    r = requests.get(url)
    with open(output, "wb") as f:
        f.write(r.content)
