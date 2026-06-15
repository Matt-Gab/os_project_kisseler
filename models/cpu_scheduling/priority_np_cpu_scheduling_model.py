# models/cpu_scheduling/priority_np_cpu_scheduling_model.py
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

def priority_np_schedule(jobs: List[Job]) -> List[Tuple[int, int, Optional[Job]]]:
    """
    Non‑preemptive Priority Scheduling.
    Lower priority number = higher priority (0 = highest).
    Priority is stored in job.extra['priority'] as a string; converted to int.
    Tie‑breaker: FCFS (arrival time).
    """
    if not jobs:
        return []

    remaining = list(jobs)
    events = []
    current_time = 0

    while remaining:
        ready = [j for j in remaining if j.arrival <= current_time]
        if not ready:
            next_arrival = min(j.arrival for j in remaining)
            events.append((current_time, next_arrival, None))
            current_time = next_arrival
            continue

        # Sort by priority (lower number = higher priority), then arrival
        next_job = min(ready, key=lambda j: (int(j.extra.get('priority', 99)), j.arrival))
        remaining.remove(next_job)

        start = current_time
        finish = start + next_job.burst
        next_job.start = start
        next_job.finish = finish
        events.append((start, finish, next_job))
        current_time = finish

    return events