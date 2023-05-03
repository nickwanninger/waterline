import multiprocessing
from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
    MofNCompleteColumn,
)


class Job:
    def __init__(self, name):
        self.name = name

    def run(self):
        """Run this job"""
        pass


class FunctionJob(Job):
    def __init__(self, name, func, *args):
        super().__init__(name)
        self.func = func
        self.args = args

    def run(self):
        """Run the function with the arguments passed in the constructor"""
        self.func(*self.args)


class JobRunner:
    jobs = []

    def __init__(self, title=""):
        self.title = title

    def run_job(self, job):
        job.run()

    def run(self, parallel=False):
        if len(self.jobs) == 0:
            return
        parallel = False

        with Progress(
            # TaskProgressColumn(),
            TimeElapsedColumn(),
            TextColumn(f"{self.title:20s}"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task(self.title, total=len(self.jobs))

            if parallel:
                with multiprocessing.Pool(None) as pool:
                    results = pool.map(self.run_job, self.jobs)
                    for _ in results:
                        progress.update(task, advance=1, description="")
            else:
                for job in self.jobs:
                    progress.update(task, description=job.name)
                    job.run()
                    progress.update(task, advance=1, description="")

        self.jobs.clear()

    def add(self, *jobs):
        """Add a job to the worklist"""
        self.jobs += jobs  # Simply append the lists
