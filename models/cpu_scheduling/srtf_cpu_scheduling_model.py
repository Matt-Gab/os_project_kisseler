from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict

@dataclass
class Job:
    name: str
    arrival: int
    burst: int
    extra: Dict[str, str] = field(default_factory=dict)
    start: int = 0
    finish: int = 0

def srtf_schedule(jobs: List[Job]) -> List[Tuple[int, int, Optional[Job]]]:
    """
    Preemptive Shortest Remaining Time First (SRTF).
    """
    if not jobs:
        return []
    remaining = {job.name: job.burst for job in jobs}
    events = []
    current_time = 0
    completed = 0
    n = len(jobs)
    first_start = {job.name: False for job in jobs}

    while completed < n:
        ready = [job for job in jobs if job.arrival <= current_time and remaining[job.name] > 0]
        if not ready:
            next_arrival = min(job.arrival for job in jobs if job.arrival > current_time)
            events.append((current_time, next_arrival, None))
            current_time = next_arrival
            continue

        job = min(ready, key=lambda j: remaining[j.name])
        if not first_start[job.name]:
            job.start = current_time
            first_start[job.name] = True

        next_arrival = min((j.arrival for j in jobs if j.arrival > current_time), default=float('inf'))
        time_to_finish = remaining[job.name]
        run_duration = min(time_to_finish, next_arrival - current_time)

        start = current_time
        end = start + run_duration
        events.append((start, end, job))
        remaining[job.name] -= run_duration
        current_time = end

        if remaining[job.name] == 0:
            job.finish = current_time
            completed += 1

    return events