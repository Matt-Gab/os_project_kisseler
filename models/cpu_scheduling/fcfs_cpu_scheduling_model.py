# models/cpu_scheduling/fcfs_cpu_scheduling_model.py
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

@dataclass
class Job:
    name: str
    arrival: int
    burst: int
    extra: Dict[str, str] = field(default_factory=dict)
    start: int = 0
    finish: int = 0

def fcfs_schedule(jobs: List[Job]) -> List[Tuple[int, int, Optional[Job]]]:
    """
    FCFS scheduling.
    Returns list of (start_time, end_time, job) where job is None for idle periods.
    """
    if not jobs:
        return []
    sorted_jobs = sorted(jobs, key=lambda j: j.arrival)
    events = []
    current_time = 0
    for job in sorted_jobs:
        # Idle gap before this job?
        if job.arrival > current_time:
            events.append((current_time, job.arrival, None))   # idle
        start = max(current_time, job.arrival)
        finish = start + job.burst
        job.start = start
        job.finish = finish
        events.append((start, finish, job))
        current_time = finish
    # No trailing idle after the last job
    return events