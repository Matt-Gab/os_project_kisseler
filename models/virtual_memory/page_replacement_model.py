# models/virtual_memory/page_replacement_model.py
from typing import List, Tuple, Dict

def fifo_page_replacement(reference_string: List[int], num_frames: int) -> List[List[int]]:
    """
    Returns a list of frame states after each reference.
    """
    frames = []
    queue = []
    states = []
    for page in reference_string:
        if page not in frames:
            if len(frames) < num_frames:
                frames.append(page)
                queue.append(page)
            else:
                # replace oldest
                oldest = queue.pop(0)
                idx = frames.index(oldest)
                frames[idx] = page
                queue.append(page)
        # record state
        states.append(frames[:] + [None] * (num_frames - len(frames)))
    return states

def optimal_page_replacement(reference_string: List[int], num_frames: int) -> List[List[int]]:
    """
    Returns a list of frame states after each reference.
    """
    frames = []
    states = []
    for i, page in enumerate(reference_string):
        if page not in frames:
            if len(frames) < num_frames:
                frames.append(page)
            else:
                # find page that will not be used for the longest time in future
                future = reference_string[i+1:]
                farthest = -1
                victim = None
                for f in frames:
                    if f not in future:
                        victim = f
                        break
                    else:
                        idx = future.index(f)
                        if idx > farthest:
                            farthest = idx
                            victim = f
                frames[frames.index(victim)] = page
        states.append(frames[:] + [None] * (num_frames - len(frames)))
    return states


def lru_page_replacement(reference_string: List[int], num_frames: int) -> List[List[int]]:
    """
    Least Recently Used page replacement.
    Returns a list of frame states after each reference.
    """
    frames = []            # current pages in memory
    last_used = []         # parallel list tracking order of last use (most recent at end)
    states = []

    for page in reference_string:
        if page in frames:
            # move to most recently used position
            idx = frames.index(page)
            frames.pop(idx)
            last_used.pop(idx)
            frames.append(page)
            last_used.append(page)
        else:
            # page fault
            if len(frames) < num_frames:
                frames.append(page)
                last_used.append(page)
            else:
                # evict least recently used (first in last_used)
                lru_page = last_used.pop(0)
                idx = frames.index(lru_page)
                frames[idx] = page
                last_used.append(page)
        # record state
        states.append(frames[:] + [None] * (num_frames - len(frames)))

    return states


def lfu_page_replacement(reference_string: List[int], num_frames: int) -> Tuple[List[List[int]], List[Dict[int, int]]]:
    """
    Least Frequently Used page replacement.
    Returns (states, counters_per_step).
    """
    frames = []
    freq = {}
    states = []
    counters = []

    for page in reference_string:
        # Update frequency counter
        freq[page] = freq.get(page, 0) + 1

        if page in frames:
            # hit – nothing changes
            pass
        else:
            # page fault
            if len(frames) < num_frames:
                frames.append(page)
            else:
                # find the page with the smallest count (tie-break: oldest)
                lfu = min(frames, key=lambda p: (freq.get(p, 0), frames.index(p)))
                frames.remove(lfu)
                frames.append(page)

        states.append(frames[:] + [None] * (num_frames - len(frames)))
        counters.append(freq.copy())   # record current counters

    return states, counters


def mfu_page_replacement(reference_string: List[int], num_frames: int) -> Tuple[List[List[int]], List[Dict[int, int]]]:
    """
    Most Frequently Used page replacement.
    Returns (states, counters_per_step).
    """
    frames = []
    freq = {}
    states = []
    counters = []

    for page in reference_string:
        freq[page] = freq.get(page, 0) + 1

        if page in frames:
            pass
        else:
            if len(frames) < num_frames:
                frames.append(page)
            else:
                # find the page with the largest count (tie-break: oldest)
                mfu = max(frames, key=lambda p: (freq.get(p, 0), -frames.index(p)))
                frames.remove(mfu)
                frames.append(page)

        states.append(frames[:] + [None] * (num_frames - len(frames)))
        counters.append(freq.copy())

    return states, counters