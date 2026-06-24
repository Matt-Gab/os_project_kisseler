from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

@dataclass
class MemoryJob:
    name: str
    size: int
    burst: int
    partition_number: Optional[int] = None   # only for Absolute

@dataclass
class Partition:
    size: int
    occupied_by: Optional[str] = None   # job name or "OS"

def simulate_mft(
    jobs: List[MemoryJob],
    partition_sizes: List[int],        # includes OS at index 0
    translation: str,                  # "absolute" or "relocatable"
    allocation: str = "first_fit",     # only used if relocatable
    cpu_sched: str = "FCFS"            # CPU scheduling algorithm (FCFS for now)
) -> List[dict]:
    """
    Single‑CPU sequential execution of jobs in memory.
    Returns snapshot events.
    """
    partitions = [Partition(size=size, occupied_by="OS" if i == 0 else None)
                  for i, size in enumerate(partition_sizes)]

    events = []
    current_time = 0

    # Hold queue (jobs that cannot yet fit into memory)
    hold_queue = list(jobs)   # all jobs start here, they will be "loaded" at time 0 or later
    # Ready queue = jobs that are in memory but not yet finished (burst remaining)
    in_memory = []   # list of (job, partition_index, remaining_burst, start_time)

    # ---------- Initial loading ----------
    # Attempt to load as many jobs as possible from hold_queue
    actions = []
    loaded_jobs = []
    for job in hold_queue[:]:
        allocated = False
        if translation == "absolute":
            target = job.partition_number
            if target is None or target < 1 or target >= len(partitions):
                continue
            if partitions[target].occupied_by is None:
                partitions[target].occupied_by = job.name
                in_memory.append((job, target, job.burst, current_time))
                actions.append((job.name, "load", target))
                hold_queue.remove(job)
                allocated = True
        else:   # relocatable
            free = [i for i in range(1, len(partitions)) if partitions[i].occupied_by is None]
            suitable = [i for i in free if partitions[i].size >= job.size]
            if suitable:
                if allocation == "best_fit":
                    all_suitable = [i for i in range(1, len(partitions)) if partitions[i].size >= job.size]
                    if all_suitable:
                        best = min(all_suitable, key=lambda i: partitions[i].size)
                        if partitions[best].occupied_by is None:
                            target = best
                            partitions[target].occupied_by = job.name
                            in_memory.append((job, target, job.burst, current_time))
                            actions.append((job.name, "load", target))
                            hold_queue.remove(job)
                            allocated = True
                elif allocation == "first_fit":
                    target = min(suitable, key=lambda i: i)
                    partitions[target].occupied_by = job.name
                    in_memory.append((job, target, job.burst, current_time))
                    actions.append((job.name, "load", target))
                    hold_queue.remove(job)
                    allocated = True
                elif allocation == "best_available_fit":
                    target = min(suitable, key=lambda i: partitions[i].size)
                    partitions[target].occupied_by = job.name
                    in_memory.append((job, target, job.burst, current_time))
                    actions.append((job.name, "load", target))
                    hold_queue.remove(job)
                    allocated = True

    # Record initial snapshot
    events.append({
        "time": current_time,
        "partitions": [Partition(p.size, p.occupied_by) for p in partitions],
        "actions": actions,
        "hold_queue": [j.name for j in hold_queue],
        "ready_queue": [(j.name, pidx, rem) for (j, pidx, rem, _) in in_memory]
    })

    # ---------- Main loop: run jobs one at a time ----------
    while in_memory or hold_queue:
        if not in_memory:
            # No job in memory – idle until a job can be loaded (shouldn't happen if hold_queue not empty)
            # Actually if all remaining jobs are too big, we would be stuck.
            # We'll simply break if no job can ever be loaded (all remaining too big for any partition)
            can_load = any(
                any(partitions[i].size >= j.size for i in range(1, len(partitions)))
                for j in hold_queue
            ) if translation == "relocatable" else any(
                j.partition_number and partitions[j.partition_number].occupied_by is None
                for j in hold_queue
            )
            if not can_load:
                break   # no more progress possible
            # Otherwise, load the next job that fits (this shouldn't happen normally)
            # We'll just try loading again later
            # But to avoid infinite loop, we'll force idle? We'll handle later.
            pass

        # Select the next job to run using CPU scheduling algorithm
        if cpu_sched == "FCFS":
            # FCFS among jobs in memory: pick the one with the smallest start_time (load time)
            # Since all loaded at same time, tie-break by order in list (which is original FCFS order)
            next_job_entry = min(in_memory, key=lambda x: (x[3], jobs.index(x[0])))
        else:
            next_job_entry = in_memory[0]   # fallback

        job, pidx, remaining_burst, load_time = next_job_entry
        # Run the job for its remaining burst (non‑preemptive)
        run_time = remaining_burst
        start_run = current_time
        finish_run = current_time + run_time
        current_time = finish_run

        # Job finishes: remove from memory and free partition
        in_memory.remove(next_job_entry)
        partitions[pidx].occupied_by = None
        actions = [(job.name, "unload", pidx)]

        # Try to load waiting jobs from hold_queue into the freed partition (and possibly other free partitions)
        # We'll attempt to load as many as fit at this exact moment.
        for j in hold_queue[:]:
            allocated = False
            if translation == "absolute":
                target = j.partition_number
                if target is None or target < 1 or target >= len(partitions):
                    continue
                if partitions[target].occupied_by is None:
                    partitions[target].occupied_by = j.name
                    in_memory.append((j, target, j.burst, current_time))
                    actions.append((j.name, "load", target))
                    hold_queue.remove(j)
                    allocated = True
            else:
                free = [i for i in range(1, len(partitions)) if partitions[i].occupied_by is None]
                suitable = [i for i in free if partitions[i].size >= j.size]
                if suitable:
                    if allocation == "best_fit":
                        all_suitable = [i for i in range(1, len(partitions)) if partitions[i].size >= j.size]
                        if all_suitable:
                            best = min(all_suitable, key=lambda i: partitions[i].size)
                            if partitions[best].occupied_by is None:
                                target = best
                                partitions[target].occupied_by = j.name
                                in_memory.append((j, target, j.burst, current_time))
                                actions.append((j.name, "load", target))
                                hold_queue.remove(j)
                                allocated = True
                    elif allocation == "first_fit":
                        target = min(suitable, key=lambda i: i)
                        partitions[target].occupied_by = j.name
                        in_memory.append((j, target, j.burst, current_time))
                        actions.append((j.name, "load", target))
                        hold_queue.remove(j)
                        allocated = True
                    elif allocation == "best_available_fit":
                        target = min(suitable, key=lambda i: partitions[i].size)
                        partitions[target].occupied_by = j.name
                        in_memory.append((j, target, j.burst, current_time))
                        actions.append((j.name, "load", target))
                        hold_queue.remove(j)
                        allocated = True

        # Record event after job completion and loading
        events.append({
            "time": current_time,
            "partitions": [Partition(p.size, p.occupied_by) for p in partitions],
            "actions": actions,
            "hold_queue": [j.name for j in hold_queue],
            "ready_queue": [(j.name, pidx, rem) for (j, pidx, rem, _) in in_memory]
        })

    return events