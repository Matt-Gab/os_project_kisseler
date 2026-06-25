from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

@dataclass
class MemoryJob:
    name: str
    size: int
    burst: int
    partition_number: Optional[int] = None   # only for Absolute
    priority: int = 99                       # lower = higher priority

@dataclass
class Partition:
    size: int
    occupied_by: Optional[str] = None

def simulate_mft(
    jobs: List[MemoryJob],
    partition_sizes: List[int],        # includes OS at index 0
    translation: str,                  # "absolute" or "relocatable"
    allocation: str = "first_fit",     # only used if relocatable
    cpu_sched: str = "FCFS",           # CPU scheduling algorithm
    quantum=1
) -> List[dict]:
    partitions = [Partition(size=size, occupied_by="OS" if i == 0 else None)
                  for i, size in enumerate(partition_sizes)]

    events = []
    current_time = 0
    hold_queue = list(jobs)
    in_memory = []   # (job, partition_index, remaining_burst, load_time)

    # ---------- Initial loading ----------
    actions = _load_jobs(hold_queue, partitions, translation, allocation, current_time, in_memory)

    events.append({
        "time": current_time,
        "partitions": [Partition(p.size, p.occupied_by) for p in partitions],
        "actions": actions,
        "hold_queue": [j.name for j in hold_queue],
        "ready_queue": [(j.name, pidx, rem) for (j, pidx, rem, _) in in_memory]
    })

    # ---------- Main loop ----------
    while in_memory or hold_queue:
        if not in_memory:
            actions = _load_jobs(hold_queue, partitions, translation, allocation, current_time, in_memory)
            if not actions:
                break
            events.append({
                "time": current_time,
                "partitions": [Partition(p.size, p.occupied_by) for p in partitions],
                "actions": actions,
                "hold_queue": [j.name for j in hold_queue],
                "ready_queue": [(j.name, pidx, rem) for (j, pidx, rem, _) in in_memory]
            })
            continue

        # ---- Select next job ----
        if cpu_sched == "RR":
            next_entry = in_memory[0]                     # front of round‑robin queue
            job, pidx, remaining, load_time = next_entry
            if len(in_memory) == 1:
                run_time = remaining                     # no preemption when alone
            else:
                run_time = min(quantum, remaining)
        elif cpu_sched == "FCFS":
            next_entry = min(in_memory, key=lambda x: x[3])
            job, pidx, remaining, load_time = next_entry
            run_time = remaining
        elif cpu_sched == "SJF":
            next_entry = min(in_memory, key=lambda x: x[2])
            job, pidx, remaining, load_time = next_entry
            run_time = remaining
        elif cpu_sched == "HRRN":
            def response_ratio(entry):
                job, pidx, rem, load_t = entry
                waiting = current_time - load_t
                return -((waiting + job.burst) / job.burst)
            next_entry = min(in_memory, key=response_ratio)
            job, pidx, remaining, load_time = next_entry
            run_time = remaining
        elif cpu_sched == "Priority NP":
            next_entry = min(in_memory, key=lambda x: (x[0].priority, x[3]))
            job, pidx, remaining, load_time = next_entry
            run_time = remaining
        else:
            next_entry = in_memory[0]
            job, pidx, remaining, load_time = next_entry
            run_time = remaining

        # ---- Execute the job ----
        finish_time = current_time + run_time
        current_time = finish_time
        remaining -= run_time

        if remaining == 0:                    # job completed
            in_memory.remove(next_entry)
            partitions[pidx].occupied_by = None
            actions = [(job.name, "unload", pidx)]

            # Reload waiting jobs
            new_actions = _load_jobs(hold_queue, partitions, translation, allocation, current_time, in_memory)
            actions.extend(new_actions)

            events.append({...})   # record event (unchanged format)
        else:
            # RR partial execution – job still in memory
            if cpu_sched == "RR":
                # Update remaining burst and move to end of round‑robin queue
                idx = in_memory.index(next_entry)
                in_memory[idx] = (job, pidx, remaining, load_time)
                in_memory.append(in_memory.pop(idx))
            # No event is recorded – the memory layout doesn't change
            continue

    return events


def _load_jobs(hold_queue, partitions, translation, allocation, current_time, in_memory):
    actions = []
    while True:
        loaded_one = False
        for job in hold_queue[:]:
            allocated = False
            if translation == "absolute":
                target = job.partition_number
                if target is None or target < 1 or target >= len(partitions):
                    continue
                if partitions[target].occupied_by is None and partitions[target].size >= job.size:
                    partitions[target].occupied_by = job.name
                    in_memory.append((job, target, job.burst, current_time))
                    actions.append((job.name, "load", target))
                    hold_queue.remove(job)
                    allocated = True
                    loaded_one = True
            else:
                free = [i for i in range(1, len(partitions)) if partitions[i].occupied_by is None]
                suitable = [i for i in free if partitions[i].size >= job.size]
                if suitable:
                    if allocation == "best_fit":
                        all_possible = [i for i in range(1, len(partitions)) if partitions[i].size >= job.size]
                        if all_possible:
                            best = min(all_possible, key=lambda i: partitions[i].size)
                            if partitions[best].occupied_by is None:
                                target = best
                            else:
                                continue
                        else:
                            continue
                    elif allocation == "first_fit":
                        target = min(suitable, key=lambda i: i)
                    elif allocation == "best_available_fit":
                        target = min(suitable, key=lambda i: partitions[i].size)
                    else:
                        target = suitable[0]

                    partitions[target].occupied_by = job.name
                    in_memory.append((job, target, job.burst, current_time))
                    actions.append((job.name, "load", target))
                    hold_queue.remove(job)
                    allocated = True
                    loaded_one = True
        if not loaded_one:
            break
    return actions