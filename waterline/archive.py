import shlex
import shutil
from pathlib import Path


def _write_run_script(path: Path, binary_rel: str, config):
    lines = ["#!/bin/sh", 'SELF="$(cd "$(dirname "$0")" && pwd)"']

    for key, value in config.env.items():
        lines.append(f"export {key}={shlex.quote(str(value))}")

    if config.cwd is not None:
        lines.append(f"cd {shlex.quote(str(config.cwd))}")
    else:
        lines.append('cd "$SELF"')

    args_str = " ".join(shlex.quote(str(a)) for a in config.args)
    cmd = f'"$SELF"/{binary_rel}'
    lines.append(f"exec {cmd} {args_str}" if args_str else f"exec {cmd}")

    path.write_text("\n".join(lines) + "\n")
    path.chmod(0o755)


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
            for config in benchmark.run_configs():
                for pipeline in pipelines:
                    binary = suite.bin / benchmark.name / pipeline.name
                    if not binary.exists():
                        continue

                    dest_dir = output_dir / suite.name / benchmark.name
                    dest_dir.mkdir(exist_ok=True, parents=True)

                    dest_binary = dest_dir / pipeline.name
                    shutil.copy2(binary, dest_binary)
                    dest_binary.chmod(0o755)

                    script_name = f"run_{pipeline.name}.sh"
                    script = dest_dir / script_name
                    binary_rel = f"{suite.name}/{benchmark.name}/{pipeline.name}"
                    _write_run_script(script, binary_rel, config)

                    if config.name == benchmark.name:
                        label = f"{suite.name}/{benchmark.name}/{pipeline.name}"
                    else:
                        label = f"{suite.name}/{benchmark.name}/{config.name}/{pipeline.name}"
                    entries.append((label, f"{suite.name}/{benchmark.name}/{script_name}"))

    _write_run_all_script(output_dir / "run_all.sh", entries)
    return output_dir
