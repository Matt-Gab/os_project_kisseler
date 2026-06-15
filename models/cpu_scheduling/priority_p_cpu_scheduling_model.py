# models/cpu_scheduling/priority_p_cpu_scheduling_model.py
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

def priority_p_schedule(jobs: List[Job]) -> List[Tuple[int, int, Optional[Job]]]:
    """
    Preemptive Priority Scheduling.
    Lower priority number = higher priority (0 = highest).
    Tie‑breaker: FCFS (arrival time).
    """
    if not jobs:
        return []

    remaining = {job.name: job.burst for job in jobs}
    events = []
    current_time = 0
    completed = 0
    n = len(jobs)
    first_start = {job.name: False for job in jobs}
    # Last running job info to avoid unnecessary preemption for equal priority
    current_job = None
    current_priority = None

    while completed < n:
        # Ready jobs: arrived and still have remaining time
        ready = [job for job in jobs if job.arrival <= current_time and remaining[job.name] > 0]

        if not ready:
            # Idle until next arrival
            next_arrival = min(job.arrival for job in jobs if job.arrival > current_time)
            events.append((current_time, next_arrival, None))
            current_time = next_arrival
            current_job = None
            continue

        # Select the job with the smallest priority number (highest priority)
        # If tie, use earliest arrival, then name to break consistently
        def sort_key(job):
            prio = int(job.extra.get('priority', 99))
            return (prio, job.arrival, job.name)

        next_job = min(ready, key=sort_key)
        prio_next = int(next_job.extra.get('priority', 99))

        # If the chosen job is different from the currently running one, we have a context switch
        # (including first time or after idle)
        if next_job is not current_job:
            # If there is a current job, it will be preempted (its slice ends now)
            # We don't need to do anything special; just start a new event.
            current_job = next_job
            current_priority = prio_next

        # Determine how long this job will run before the next scheduling decision
        # Next decision points: next job arrival OR this job's completion
        next_arrival = min((j.arrival for j in jobs if j.arrival > current_time), default=float('inf'))
        time_to_finish = remaining[current_job.name]
        run_duration = min(time_to_finish, next_arrival - current_time)

        start = current_time
        end = start + run_duration
        if not first_start[current_job.name]:
            current_job.start = start
            first_start[current_job.name] = True

        events.append((start, end, current_job))
        remaining[current_job.name] -= run_duration
        current_time = end

        if remaining[current_job.name] == 0:
            current_job.finish = current_time
            completed += 1
            current_job = None  # will reselect next loop

    return events