import json
import shlex
import shutil
from pathlib import Path


def _copy_run_inputs(dest_dir: Path, config):
    if config.cwd is None:
        return

    cwd = Path(config.cwd)
    copied = set()
    for arg in config.args:
        arg_path = Path(arg)
        if arg_path.is_absolute():
            continue

        source = cwd / arg_path
        if not source.exists() or source in copied:
            continue

        copied.add(source)
        dest = dest_dir / arg_path
        dest.parent.mkdir(exist_ok=True, parents=True)
        if source.is_dir():
            shutil.copytree(source, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(source, dest)


def _write_run_script(path: Path, binary_name: str, config):
    # The script and binary live in the same directory.
    lines = ["#!/bin/sh", 'SELF="$(cd "$(dirname "$0")" && pwd)"']

    for key, value in config.env.items():
        lines.append(f"export {key}={shlex.quote(str(value))}")

    lines.append('cd "$SELF"')

    args_str = " ".join(shlex.quote(str(a)) for a in config.args)
    cmd = f'"$SELF"/{binary_name}'
    lines.append(f"exec {cmd} {args_str}" if args_str else f"exec {cmd}")

    path.write_text("\n".join(lines) + "\n")
    path.chmod(0o755)


def _write_config_json(path: Path, suite_name: str, benchmark_name: str, pipeline_names, configurations):
    path.write_text(
        json.dumps(
            {
                "suite": suite_name,
                "benchmark": benchmark_name,
                "pipelines": pipeline_names,
                "configurations": configurations,
            },
            indent=2,
        )
        + "\n"
    )


def _write_run_all_script(path: Path, entries):
    """
    entries: list of (label, script_path_relative_to_archive_root)
    """
    lines = [
        "#!/bin/sh",
        'ARCHIVE="$(cd "$(dirname "$0")" && pwd)"',
        'RESULTS="$ARCHIVE/results.txt"',
        ': > "$RESULTS"',
        "",
        "run_bench() {",
        '    local label="$1" script="$2"',
        '    printf "%s\\t" "$label" | tee -a "$RESULTS"',
        '    start=$(date +%s)',
        '    "$script"',
        '    status=$?',
        '    end=$(date +%s)',
        '    printf "status=%d time_s=%d\\n" "$status" "$((end - start))" | tee -a "$RESULTS"',
        "}",
        "",
    ]
    for label, script_rel in entries:
        lines.append(f'run_bench {shlex.quote(label)} "$ARCHIVE/{script_rel}"')

    path.write_text("\n".join(lines) + "\n")
    path.chmod(0o755)


def archive_workspace(workspace, output_dir, pipeline_names=None):
    """
    Copy compiled binaries and generate run scripts into output_dir.
    The resulting directory is self-contained and can be tarballed for
    transfer to a target host.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    if pipeline_names is None:
        pipeline_names = list(workspace.pipelines.keys())

    pipelines = [workspace.pipelines[name] for name in pipeline_names]
    entries = []

    for suite in workspace.suites:
        for benchmark in suite.benchmarks:
            configs = list(benchmark.run_configs())
            archived_pipelines = []
            config_data = {
                config.name: {
                    "name": config.name,
                    "args": list(config.args),
                    "cwd": ".",
                    "env": dict(config.env),
                    "scripts": {},
                }
                for config in configs
            }

            for pipeline in pipelines:
                binary = suite.bin / benchmark.name / pipeline.name
                if not binary.exists():
                    continue

                dest_dir = output_dir / suite.name / benchmark.name
                dest_dir.mkdir(exist_ok=True, parents=True)

                dest_binary = dest_dir / pipeline.name
                shutil.copy2(binary, dest_binary)
                dest_binary.chmod(0o755)
                archived_pipelines.append(pipeline.name)

                for config in configs:
                    _copy_run_inputs(dest_dir, config)

                    script_name = f"run_{config.name}_{pipeline.name}.sh"
                    script = dest_dir / script_name
                    _write_run_script(script, pipeline.name, config)
                    config_data[config.name]["scripts"][pipeline.name] = script_name

                    if config.name == benchmark.name:
                        label = f"{suite.name}/{benchmark.name}/{pipeline.name}"
                    else:
                        label = f"{suite.name}/{benchmark.name}/{config.name}/{pipeline.name}"
                    entries.append((label, f"{suite.name}/{benchmark.name}/{script_name}"))

            if archived_pipelines:
                _write_config_json(
                    dest_dir / "config.json",
                    suite.name,
                    benchmark.name,
                    archived_pipelines,
                    [config_data[config.name] for config in configs],
                )

    _write_run_all_script(output_dir / "run_all.sh", entries)
    return output_dir
