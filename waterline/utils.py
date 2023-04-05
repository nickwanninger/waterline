from pathlib import Path
import subprocess


def run_command(args: list[str]):
  print('running command', ' '.join(map(str, args)))
  output = subprocess.check_output(args)


def shell(commnad: str):
  run_command(['sh', '-c', commnad])


def git_clone(url: str, destination: Path):
  shell(f'git clone {url} {destination} --depth 1')
