from __future__ import annotations

from collections import defaultdict
from IPython.display import clear_output
import queue
import os
import ray
import time
from typing import Callable

# Actor to manage heartbeats
@ray.remote
class HeartbeatActor:
    def __init__(self):
        self.last_heartbeat = defaultdict(lambda: time.time())

    def send_heartbeat(self, idx: int):
        self.last_heartbeat[idx] = time.time()

    def time_since_heartbeat(self, idx: int):
        return time.time() - self.last_heartbeat[idx]


def run_ray_tasks(
    f: Callable,  # Ray remote function
    args: list,  # List of arguments to pass to f, one element per task
    max_concurrent: int,
    timeout: int,
    monitor: RayRunsMonitor,
):
    ray.init(ignore_reinit_error=True)

    task_queue = queue.Queue()
    for process_args in args:
        task_queue.put(process_args)

    running_tasks = {}
    heartbeat_actor = HeartbeatActor.remote()

    task_index = 0

    results = {}
    while not task_queue.empty() or running_tasks:
        # While we have capacity, submit tasks
        while len(running_tasks) < max_concurrent and not task_queue.empty():
            input_data = task_queue.get()
            # Start the task
            future = f.remote(
                input_data,
                lambda idx=task_index: heartbeat_actor.send_heartbeat.remote(idx)
            )
            running_tasks[task_index] = future
            monitor.started(task_index, input_data)
            task_index += 1

        # Check if any of the running tasks have finished
        futures = list(running_tasks.values())
        ready, _not_ready = ray.wait(futures, timeout=1)
        if ready:
            for idx, future in list(running_tasks.items()):
                if future in ready:
                    try:
                        result = ray.get(future)
                        results[idx] = result
                        monitor.completed(idx, result)
                    except ray.exceptions.TaskCancelledError:
                        monitor.canceled_cardiac_arrest(idx)
                    except ray.exceptions.WorkerCrashedError:
                        monitor.crashed(idx)
                    except ray.exceptions.RayTaskError as e:
                        monitor.failed(idx, str(e))
                    # Remove the task from running_tasks
                    del running_tasks[idx]

        # Check the heartbeats of the remaining running tasks
        for idx, future in list(running_tasks.items()):
            time_since_heartbeat = ray.get(heartbeat_actor.time_since_heartbeat.remote(idx))
            if time_since_heartbeat > timeout + 5:  # Allow 5 s for responding to ray.cancel
                monitor.failed_to_stop(idx)
                ray.cancel(future, force=True)
            elif time_since_heartbeat > timeout:
                monitor.no_hearbeat(idx)
                ray.cancel(future)
            else:
                monitor.heartbeat(idx, time_since_heartbeat)

        monitor.display_progress()

    ray.shutdown()
    return results


class RayRunsMonitor:
    def __init__(self,
        args: list,  # List of arguments to pass to worker function
        overwrite: bool = True
    ):
        self.args = args
        self.set_task_names()
        self.overwrite = overwrite  # If False, will not clear terminal
        self._status = ["" for _ in args]
        self._progress = ["" for _ in args]
        self._completed = {}
        self._failed = {}
        try:
            __IPYTHON__  # noqa
            self._ipython = True
        except NameError:
            self._ipython = False

    def set_task_names(self):
        self.task_names = [
            f"{i}" for i in range(len(self.args))
        ]  # Name of each task to be displayed in the progress

    def started(self, idx: int, input_data):
        pass

    def completed(self, idx: int, result: str):
        self._status[idx] += f" {result}"
        self._completed[idx] = True

    def canceled_cardiac_arrest(self, idx: int):
        self._status[idx] = "canceled due to cardiac arrest"
        self._failed[idx] = True

    def crashed(self, idx: int):
        self._status[idx] = "canceled forcefully due to cardiac arrest"
        self._failed[idx] = True

    def failed(self, idx: int, error: str):
        self._status[idx] = f"failed: {error}"
        self._failed[idx] = True

    def failed_to_stop(self, idx: int):
        self._status[idx] = "failed to stop, terminating forcefully"
        self._failed[idx] = True

    def no_hearbeat(self, idx: int):
        self._status[idx] = "no heartbeat, terminating gently"
        self._failed[idx] = True

    def heartbeat(self, idx: int, time_since_heartbeat: float):
        self._progress[idx] += "."

    def clear_terminal(self):
        if self._ipython:
            clear_output(wait=True)
        else:
            os.system('cls' if os.name == 'nt' else 'clear')

    def display_progress(self):
        if self.overwrite:
            self.clear_terminal()

        s = "\n".join([
            self.task_names[i] + ": " + self._progress[i] + " " + self._status[i]
            for i in range(len(self.args))
        ])
        print(s)

class DebugRayRunsMonitor(RayRunsMonitor):
    def __init__(self, args: list):
        self.args = args

    def started(self, idx: int, input_data):
        print(f"Task {idx} started with input: {input_data}")

    def completed(self, idx: int, result: str):
        print(f"Task {idx} completed with result: {result}")

    def canceled_cardiac_arrest(self, idx: int):
        print(f"Task {idx} was canceled due to cardiac arrest")

    def crashed(self, idx: int):
        print(f"Task {idx} was canceled forcefully due to cardiac arrest")

    def failed(self, idx: int, error: str):
        print(f"Task {idx} failed with error: {error}")

    def failed_to_stop(self, idx: int):
        print(f"Task {idx} failed to stop, terminating forcefully")

    def no_hearbeat(self, idx: int):
        print(f"No heartbeat detected for task {idx+1}, terminating gently")

    def heartbeat(self, idx: int, time_since_heartbeat: float):
        print(f"Heartbeat for task {idx} received {round(time_since_heartbeat * 1000)} ms ago")

    def display_progress(self):
        pass
