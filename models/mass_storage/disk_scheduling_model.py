from typing import List, Tuple

def fcfs_disk(requests: List[int], start: int, _max: int, **kwargs) -> Tuple[List[int], int]:
    sequence = [start] + requests
    movement = sum(abs(sequence[i] - sequence[i-1]) for i in range(1, len(sequence)))
    return sequence, movement

def sstf_disk(requests: List[int], start: int, _max: int, **kwargs) -> Tuple[List[int], int]:
    current = start
    remaining = list(requests)
    sequence = [start]
    movement = 0
    while remaining:
        closest = min(remaining, key=lambda x: abs(x - current))
        movement += abs(closest - current)
        current = closest
        sequence.append(current)
        remaining.remove(current)
    return sequence, movement

def scan_disk(requests: List[int], start: int, max_track: int, direction: str = "left", **kwargs) -> Tuple[List[int], int]:
    """
    SCAN with initial direction.
    direction = 'left' -> head moves towards 0 first
    direction = 'right' -> head moves towards max_track first
    """
    current = start
    sequence = [start]
    movement = 0

    left = sorted([r for r in requests if r < current], reverse=True)   # descending
    right = sorted([r for r in requests if r >= current])                # ascending

    if direction == "left":
        # service left first, go to 0, then right
        for r in left:
            movement += abs(current - r)
            current = r
            sequence.append(current)
        if current != 0:
            movement += current - 0
            current = 0
            sequence.append(current)
        for r in right:
            movement += abs(current - r)
            current = r
            sequence.append(current)
    else:   # direction == "right"
        # service right first, go to max_track, then left
        for r in right:
            movement += abs(current - r)
            current = r
            sequence.append(current)
        if current != max_track:
            movement += abs(max_track - current)
            current = max_track
            sequence.append(current)
        for r in left:
            movement += abs(current - r)
            current = r
            sequence.append(current)

    return sequence, movement

def cscan_disk(requests: List[int], start: int, max_track: int, direction: str = "left", **kwargs) -> Tuple[List[int], int]:
    """
    C-SCAN with initial direction.
    """
    current = start
    sequence = [start]
    movement = 0

    left = sorted([r for r in requests if r < current])
    right = sorted([r for r in requests if r >= current])

    if direction == "left":
        # service left first down to 0, then jump to max_track, then service right from max down
        for r in reversed(left):
            movement += abs(current - r)
            current = r
            sequence.append(current)
        if current != 0:
            movement += current - 0
            current = 0
            sequence.append(current)
        # jump to max_track
        movement += max_track - 0
        current = max_track
        sequence.append(current)
        for r in sorted(right, reverse=True):
            movement += abs(current - r)
            current = r
            sequence.append(current)
    else:   # direction == "right"
        # service right first up to max_track, then jump to 0, then service left from 0 up
        for r in right:
            movement += abs(current - r)
            current = r
            sequence.append(current)
        if current != max_track:
            movement += abs(max_track - current)
            current = max_track
            sequence.append(current)
        # jump to 0
        movement += max_track - 0
        current = 0
        sequence.append(current)
        for r in left:
            movement += abs(current - r)
            current = r
            sequence.append(current)

    return sequence, movement

def look_disk(requests: List[int], start: int, _max: int, direction: str = "left", **kwargs) -> Tuple[List[int], int]:
    """
    LOOK with initial direction.
    """
    current = start
    sequence = [start]
    movement = 0

    left = sorted([r for r in requests if r < current], reverse=True)
    right = sorted([r for r in requests if r >= current])

    if direction == "left":
        for r in left:
            movement += abs(current - r)
            current = r
            sequence.append(current)
        for r in right:
            movement += abs(current - r)
            current = r
            sequence.append(current)
    else:
        for r in right:
            movement += abs(current - r)
            current = r
            sequence.append(current)
        for r in left:
            movement += abs(current - r)
            current = r
            sequence.append(current)

    return sequence, movement