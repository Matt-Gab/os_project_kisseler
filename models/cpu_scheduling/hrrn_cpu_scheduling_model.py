# models/cpu_scheduling/hrrn_cpu_scheduling_model.py
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

def hrrn_schedule(jobs: List[Job]) -> List[Tuple[int, int, Optional[Job]]]:
    """
    Non‑preemptive Highest Response Ratio Next.
    Response Ratio = (waiting_time + burst) / burst
    """
    if not jobs:
        return []

    remaining = list(jobs)
    events = []
    current_time = 0

    while remaining:
        # Jobs that have arrived and not yet scheduled
        ready = [j for j in remaining if j.arrival <= current_time]

        if not ready:
            # Idle gap until the next arrival
            next_arrival = min(j.arrival for j in remaining)
            events.append((current_time, next_arrival, None))
            current_time = next_arrival
            continue

        # Calculate response ratio for each ready job
        # Tie‑breaker: highest ratio → earliest arrival → shortest burst → name
        def sort_key(job):
            waiting = current_time - job.arrival
            ratio = (waiting + job.burst) / job.burst
            return (-ratio, job.arrival, job.burst, job.name)

        next_job = min(ready, key=sort_key)
        remaining.remove(next_job)

        start = current_time
        finish = start + next_job.burst
        next_job.start = start
        next_job.finish = finish
        events.append((start, finish, next_job))
        current_time = finish

    return events