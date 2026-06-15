# models/cpu_scheduling/rr_cpu_scheduling_model.py
from dataclasses import dataclass, field
from collections import deque
from typing import List, Tuple, Optional, Dict

@dataclass
class Job:
    name: str
    arrival: int
    burst: int
    extra: Dict[str, str] = field(default_factory=dict)
    start: int = 0
    finish: int = 0

def rr_schedule(jobs: List[Job], quantum: int) -> List[Tuple[int, int, Optional[Job]]]:
    """
    Round‑Robin scheduling.
    """
    if not jobs or quantum <= 0:
        return []

    remaining = {job.name: job.burst for job in jobs}
    events = []
    current_time = 0
    first_start = {job.name: False for job in jobs}

    # Ready queue with arrival order
    queue = deque()
    # We'll process jobs as they arrive; use a sorted list of arrivals
    sorted_jobs = sorted(jobs, key=lambda j: j.arrival)
    idx = 0
    n = len(jobs)
    finished = set()

    while len(finished) < n:
        # Add all jobs that have arrived by current_time
        while idx < n and sorted_jobs[idx].arrival <= current_time:
            queue.append(sorted_jobs[idx])
            idx += 1

        if not queue:
            # Idle until next arrival
            next_arrival = min(j.arrival for j in jobs if j.arrival > current_time)
            events.append((current_time, next_arrival, None))
            current_time = next_arrival
            continue

        job = queue.popleft()
        if not first_start[job.name]:
            job.start = current_time
            first_start[job.name] = True

        # Time slice = min(quantum, remaining burst)
        run_time = min(quantum, remaining[job.name])
        start = current_time
        end = start + run_time
        events.append((start, end, job))
        remaining[job.name] -= run_time
        current_time = end

        # Add any jobs that arrived during this slice
        while idx < n and sorted_jobs[idx].arrival <= current_time:
            queue.append(sorted_jobs[idx])
            idx += 1

        if remaining[job.name] > 0:
            # Re-queue at the end
            queue.append(job)
        else:
            job.finish = current_time
            finished.add(job.name)

    return events