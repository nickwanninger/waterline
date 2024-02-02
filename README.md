# Waterline

# Design Spec

## Workspace

A `workspace` is effectively a directory in the filesystem with a `src/` and `bin/` subdirectory.
A workspace can have any number of benchmark `suites` added to them.
The job of a workspace is to orchestrate the acquisition and configuration of `suites`, as well as the compilation of the `benchmarks` that `suites` produce according to a set of `CompileConfigurations`.
A `workspace` also runs each of these benchmarks using `RunConfigurations`.

## Suite

A benchmark `suite` informs the system on how to do two tasks: how to `acquire` the code, and how to `configure` benchmarks according to `CompileConfigurations`.
The whole of waterline functions on `Task` structures, which encode the commands to execute to do these two things.
