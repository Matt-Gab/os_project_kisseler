from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

@dataclass
class MemoryBlock:
    base: int
    size: int
    occupied_by: Optional[str] = None   # job name, "OS", or None for free

def simulate_mvt(
    jobs: List[dict],          # list of dicts with name, size, burst, priority (optional)
    os_size: int,
    max_memory: int,
    compaction: bool,
    scheduling: str,            # FCFS, SJF, HRRN, Priority NP
    allocation: str,            # first_fit, best_fit, worst_fit
    quantum=1
) -> List[dict]:
    """
    Simulates MVT memory management with single‑CPU execution.
    Returns a list of snapshot events.
    """
    # Initial memory: OS at bottom, rest free
    blocks = [
        MemoryBlock(0, os_size, "OS"),
        MemoryBlock(os_size, max_memory - os_size, None)
    ]

    events = []
    current_time = 0
    waiting_jobs = list(jobs)   # jobs not yet in memory (arrival=0)
    in_memory = []              # list of (job_dict, start_time, remaining_burst)

    # ---------- Initial loading ----------
    actions = []
    loaded_any = True
    while loaded_any:
        loaded_any = False
        for job in waiting_jobs[:]:
            success = try_load_job(job, blocks, allocation, compaction)
            if success:
                waiting_jobs.remove(job)
                in_memory.append((job, current_time, job["burst"]))
                actions.append((job["name"], "load", None))
                loaded_any = True

    events.append({
        "time": current_time,
        "blocks": [MemoryBlock(b.base, b.size, b.occupied_by) for b in blocks],
        "actions": actions,
        "hold_queue": [j["name"] for j in waiting_jobs],
        "ready_queue": [j["name"] for j, _, _ in in_memory]
    })

    # ---------- Main loop ----------
    while in_memory:
        if scheduling == "RR":
            next_entry = in_memory[0]
            job, start_time, remaining = next_entry
            if len(in_memory) == 1:
                run_time = remaining
            else:
                run_time = min(quantum, remaining)
        elif scheduling == "FCFS":
            next_entry = min(in_memory, key=lambda x: x[1])
            job, start_time, remaining = next_entry
            run_time = remaining
        elif scheduling == "SJF":
            next_entry = min(in_memory, key=lambda x: x[2])
            job, start_time, remaining = next_entry
            run_time = remaining
        elif scheduling == "HRRN":
            def response_ratio(entry):
                job, start, remaining = entry
                waiting = current_time - start
                return -((waiting + job["burst"]) / job["burst"])
            next_entry = min(in_memory, key=response_ratio)
            job, start_time, remaining = next_entry
            run_time = remaining
        elif scheduling == "Priority NP":
            next_entry = min(in_memory, key=lambda x: (x[0].get("priority", 99), x[1]))
            job, start_time, remaining = next_entry
            run_time = remaining
        else:
            next_entry = in_memory[0]
            job, start_time, remaining = next_entry
            run_time = remaining

        finish_time = current_time + run_time
        current_time = finish_time
        remaining -= run_time

        if remaining == 0:
            # job finished
            base_of_freed = None
            for b in blocks:
                if b.occupied_by == job["name"]:
                    base_of_freed = b.base
                    break
            in_memory.remove(next_entry)
            free_job_memory(job["name"], blocks)
            actions = [(job["name"], "unload", base_of_freed)]

            # Load waiting jobs
            loaded_any = True
            while loaded_any:
                loaded_any = False
                for wjob in waiting_jobs[:]:
                    if try_load_job(wjob, blocks, allocation, compaction):
                        waiting_jobs.remove(wjob)
                        in_memory.append((wjob, current_time, wjob["burst"]))
                        actions.append((wjob["name"], "load", None))
                        loaded_any = True

            events.append({...})   # record event
        else:
            # RR partial execution – job not finished
            if scheduling == "RR":
                idx = in_memory.index(next_entry)
                in_memory[idx] = (job, start_time, remaining)
                in_memory.append(in_memory.pop(idx))
            continue

    return events


def try_load_job(job: dict, blocks: List[MemoryBlock], allocation: str, compaction_enabled: bool) -> bool:
    """
    Attempt to load job into memory using the given allocation policy.
    If no single hole fits and total free space is sufficient, try compaction (if enabled).
    Returns True if loaded, False otherwise.
    """
    holes = [b for b in blocks if b.occupied_by is None]
    suitable = [h for h in holes if h.size >= job["size"]]
    if suitable:
        if allocation == "first_fit":
            chosen = min(suitable, key=lambda h: h.base)
        elif allocation == "best_fit":
            chosen = min(suitable, key=lambda h: h.size)
        elif allocation == "worst_fit":
            chosen = max(suitable, key=lambda h: h.size)
        else:
            chosen = suitable[0]
        allocate_in_hole(job["name"], job["size"], chosen, blocks)
        return True
    else:
        total_free = sum(h.size for h in holes)
        if total_free >= job["size"] and compaction_enabled:
            compact_memory(blocks)
            holes = [b for b in blocks if b.occupied_by is None]
            suitable = [h for h in holes if h.size >= job["size"]]
            if suitable:
                chosen = suitable[0]   # only one hole after compaction
                allocate_in_hole(job["name"], job["size"], chosen, blocks)
                return True
        return False


def allocate_in_hole(job_name: str, job_size: int, hole: MemoryBlock, blocks: List[MemoryBlock]):
    idx = blocks.index(hole)
    if hole.size == job_size:
        hole.occupied_by = job_name
    else:
        hole.occupied_by = job_name
        old_size = hole.size
        hole.size = job_size
        new_free = MemoryBlock(hole.base + job_size, old_size - job_size, None)
        blocks.insert(idx + 1, new_free)


def free_job_memory(job_name: str, blocks: List[MemoryBlock]):
    for block in blocks:
        if block.occupied_by == job_name:
            block.occupied_by = None
            break
    i = 0
    while i < len(blocks) - 1:
        if blocks[i].occupied_by is None and blocks[i+1].occupied_by is None:
            blocks[i].size += blocks[i+1].size
            del blocks[i+1]
        else:
            i += 1


def compact_memory(blocks: List[MemoryBlock]):
    allocated = [b for b in blocks if b.occupied_by is not None]
    allocated.sort(key=lambda b: b.base)
    current = 0
    new_blocks = []
    for b in allocated:
        b.base = current
        new_blocks.append(b)
        current += b.size
    total_memory = sum(b.size for b in blocks)
    free_size = total_memory - current
    if free_size > 0:
        new_blocks.append(MemoryBlock(current, free_size, None))
    blocks.clear()
    blocks.extend(new_blocks)