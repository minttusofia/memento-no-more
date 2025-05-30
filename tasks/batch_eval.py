import asyncio
from copy import deepcopy
from datetime import datetime
from IPython.display import clear_output, HTML, display
import json
import os
from pathlib import Path

from agent import AGENT_BATCH_RUNS_PATH
from agent.agent import Agent
from agent.clients import BaseClient
from agent.configs import AgentConfig
from agent.stats import Stats
import tasks as t


RUN_REPORT = "run_report.json"

def save_score_and_stats(run_path: Path, status: str, score: float | None, stats: Stats | None):
    score_stats = {
        "status": status,
        "score": score,
        "stats": stats.to_dict() if stats else None
    }
    run_rpt_path = run_path / RUN_REPORT
    with open(run_rpt_path, "w") as f:
        json.dump(score_stats, f, indent=2)

async def execute_task(
    task: t.BaseTask,
    run_path: Path,
    config: AgentConfig,
    client: BaseClient,
    verbose: bool = True,
) -> tuple[str, float | None, Agent]:
    agent = Agent(
        task=task.task,
        run_path=run_path,
        config=config,
        input_variables=task.input_variables,
        return_cls_name=task.return_cls_name,
        init_script=task.init_script,
    )
    task.agent_home = run_path
    with task:
        try:
            success = await agent.run(
                client=client,
                max_llm_calls=task.budget,
            )
            if success:
                if verbose:
                    agent.print_report()
                score, report = task.evaluate(agent, verbose=verbose)
                agent.logger.info(
                    "Evaluation results:\n" +
                    f"{score=:0.2f}\n" +
                    "\nReport:\n" + report
                )
                status = f"done: {score:0.2f}"

            else:
                if verbose:
                    print(agent.final_report)
                score = 0.
                status = f"failed: {agent.final_report}"

        except asyncio.CancelledError:
            score = None
            status = "asyncio-cancelled"
            agent.logger.info("Task cancelled.")

        except Exception as e:
            score = None
            status = f"code failure: {e}"
            agent.logger.exception("An error occurred: %s", e)

        save_score_and_stats(run_path, status, score, agent.stats)

    return status, score, agent, task


def save_results(
    run_names: list[str],
    scores: list[float | None],
    stats: list[Stats],
    batch_run_path: Path,
    update: bool = False,
    verbose: bool = True
):
    ind_scores = {run_name: score for run_name, score in zip(run_names, scores, strict=True)}
    stats_dict = {run_name: s.to_dict() if s else None for run_name, s in zip(run_names, stats, strict=True)}

    scores_path = batch_run_path / "scores.json"
    stats_path = batch_run_path / "stats.json"
    if update and scores_path.exists() and stats_path.exists():
        new_ind_scores = ind_scores
        with open(scores_path, "r") as f:
            avi_scores = json.load(f)
            ind_scores = avi_scores["individual"]
            ind_scores.update(new_ind_scores)

        new_stats_dict = stats_dict
        with open(stats_path, "r") as f:
            stats_dict = json.load(f)
            stats_dict.update(new_stats_dict)


    scores = {
        "average": sum([x or 0.0 for x in ind_scores.values()]) / len(ind_scores),
        "individual": ind_scores,
    }

    with open(scores_path, "w") as f:
        json.dump(scores, f, indent=2)
    if verbose:
        print("Results saved to", batch_run_path)

    with open(stats_path, "w") as f:
        json.dump(stats_dict, f, indent=2)

    return dict(scores), stats_dict


class Manager:
    def __init__(
        self,
        tasks: list[t.BaseTask],
        agent_configs: list[AgentConfig],
        batch_run_paths: Path | list[Path],
        max_concurrent_tasks: int = None,  # None means no limit
        debug: bool = False
    ):
        self.tasks = tasks
        self.agent_configs = agent_configs
        self.batch_run_paths = batch_run_paths
        self.jobs = []
        self.run_names = []
        self.run_paths = []
        self.max_concurrent_tasks = max_concurrent_tasks or len(tasks)
        self.debug = debug
        try:
            __IPYTHON__  # noqa
            self._ipython = True
        except NameError:
            self._ipython = False

    # Coroutine to monitor the progress of concurrent runs
    async def monitor(self):
        try:
            while True:
                self.display_progress()
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.display_progress()

    def clear_terminal(self):
        if self._ipython:
            clear_output(wait=True)
        else:
            os.system('cls' if os.name == 'nt' else 'clear')

    def display_progress(self):
        if self.debug:
            print(self.jobs)
        else:
            self.clear_terminal()

        content = ""
        for run_name, run_path in zip(self.run_names, self.run_paths, strict=True):
            n_steps = len(list(run_path.glob("**/*.xml")))
            progress = f"{'.'*n_steps}"
            run_rpt_path = run_path / RUN_REPORT
            if run_rpt_path.exists():
                with open(run_rpt_path, "r") as f:
                    report = json.load(f)
                status = report["status"].split("\n")[0]
                progress += f" {status}"

            log_path = run_path / "output.ans"
            if self._ipython:
                content += f'{run_name}: <a href="file://{log_path}" target="_blank">log</a> {progress}<br>'
            else:
                content += f'{run_name}: {progress}\n'

        done = [job.done() for job in self.jobs]
        content += f"Finished: {sum(done)}/{len(self.jobs)}"
        if self._ipython:
            html_content = '''<div style="font-family: Menlo, Monaco, 'Courier New', monospace; font-size: inherit;">{content}</div>'''
            display(HTML(html_content.format(content=content)))
        else:
            print(content)

    async def run_task_with_semaphore(self, semaphore, task, run_name, run_path, config, client):
        try:
            async with semaphore:
                return await execute_task(task, run_path, config, client, verbose=False)
                #for i in range(10):
                #    print(f"{run_name}: {i}")
                #    await asyncio.sleep(1)
        except asyncio.CancelledError:
            #print(f"Task {run_name} cancelled.")
            return None, None, None, task

    async def run(
        self,
        client,
        debug=False  # Use True to see exceptions
    ):
        self.debug = debug
        try:
            self.monitor_job = asyncio.create_task(self.monitor())
            run_names = self.run_names

            semaphore = asyncio.Semaphore(self.max_concurrent_tasks)

            jobs = self.jobs
            for task, agent_config, batch_run_path in zip(
                self.tasks, self.agent_configs, self.batch_run_paths, strict=True
            ):
                agent_config.verbose = 0
                run_name = task.name
                run_names.append(run_name)
                run_path = batch_run_path / run_name
                self.run_paths.append(run_path)

                jobs.append(asyncio.create_task(
                    self.run_task_with_semaphore(semaphore, deepcopy(task), run_name, run_path, agent_config, client)))

            if debug:
                try:
                    task_results = await asyncio.gather(*jobs, return_exceptions=False)

                except Exception as e:
                    print(f"An exception occurred: {e}")
                    self.monitor_job.cancel()
                    raise e

            else:
                task_results = await asyncio.gather(*jobs, return_exceptions=True)

            statuses, scores, agents, tasks = zip(*task_results, strict=True)
            self.monitor_job.cancel()
            await self.monitor_job
            print("Jobs finished.")

            return run_names, statuses, scores, agents, tasks

        except asyncio.CancelledError:
            for job in self.jobs:
                job.cancel()
            # Wait for all jobs to stop
            await asyncio.gather(*self.jobs, return_exceptions=True)

            self.monitor_job.cancel()
            await self.monitor_job
            print("Jobs cancelled.")

            return None, None, None, None


def create_batch_run_path(model: str, taskset_name: str, stime: str = None):
    if stime is None:
        stime = datetime.now().strftime("%Y%m%d-%H%M%S")
    batch_run_path = AGENT_BATCH_RUNS_PATH / model / f"{stime}_{taskset_name}"
    batch_run_path.mkdir(parents=True, exist_ok=True)
    return batch_run_path
