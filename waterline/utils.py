from pathlib import Path
import subprocess
import requests


def run_command(args: list[str]):
    print("running command", " ".join(map(str, args)))
    output = subprocess.check_output(args)


def shell(commnad: str):
    run_command(["sh", "-c", commnad])


def git_clone(url: str, destination: Path):
    shell(f"git clone {url} {destination} --depth 1")


def download(url: str, output: Path):
    r = requests.get(url)
    with open(output, "wb") as f:
        f.write(r.content)
