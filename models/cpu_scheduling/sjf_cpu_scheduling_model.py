# models/cpu_scheduling/sjf_cpu_scheduling_model.py
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

def sjf_schedule(jobs: List[Job]) -> List[Tuple[int, int, Optional[Job]]]:
    """
    Non‑preemptive Shortest Job First.
    Returns (start, end, job) for each execution segment. Idle = job is None.
    """
    if not jobs:
        return []

    # Work with a copy, sorted by arrival, then burst
    remaining = sorted(jobs, key=lambda j: (j.arrival, j.burst))
    events = []
    current_time = 0

    while remaining:
        # Gather all jobs that have arrived by now
        arrived = [j for j in remaining if j.arrival <= current_time]

        if not arrived:
            # No job is ready → CPU idle until the next job arrives
            next_arrival = min(j.arrival for j in remaining)
            events.append((current_time, next_arrival, None))
            current_time = next_arrival
            continue

        # Pick the job with the smallest burst time
        next_job = min(arrived, key=lambda j: j.burst)
        remaining.remove(next_job)

        start = current_time
        finish = start + next_job.burst
        next_job.start = start
        next_job.finish = finish
        events.append((start, finish, next_job))
        current_time = finish

    return events