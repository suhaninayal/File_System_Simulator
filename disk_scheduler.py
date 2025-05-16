import matplotlib.pyplot as plt


def fcfs_scheduling(requests, start):
    """First-Come, First-Served disk scheduling algorithm.

    Args:
        requests: List of disk block positions to access
        start: Initial position of disk head

    Returns:
        Complete access sequence including the start position
    """
    sequence = [start] + requests
    return sequence


def sstf_scheduling(requests, start):
    """Shortest Seek Time First disk scheduling algorithm.

    Args:
        requests: List of disk block positions to access
        start: Initial position of disk head

    Returns:
        Complete access sequence including the start position
    """
    sequence = [start]
    remaining = requests.copy()
    current = start

    while remaining:
        # Find the closest request to current position
        nearest = min(remaining, key=lambda x: abs(x - current))
        sequence.append(nearest)
        remaining.remove(nearest)
        current = nearest

    return sequence


def scan_scheduling(requests, start, direction='up'):
    """SCAN (Elevator) disk scheduling algorithm.

    Args:
        requests: List of disk block positions to access
        start: Initial position of disk head
        direction: Initial direction ('up' or 'down')

    Returns:
        Complete access sequence including the start position
    """
    sequence = [start]
    if not requests:
        return sequence

    # Copy requests and add start position for sorting
    positions = sorted(set(requests))

    # Split requests into those greater and less than start
    up_requests = [r for r in positions if r > start]
    down_requests = [r for r in positions if r < start]

    if direction == 'up':
        # Go up first, then reverse and go down
        sequence.extend(up_requests)
        sequence.extend(reversed(down_requests))
    else:
        # Go down first, then reverse and go up
        sequence.extend(reversed(down_requests))
        sequence.extend(up_requests)

    return sequence


def c_scan_scheduling(requests, start):
    """C-SCAN disk scheduling algorithm.

    Args:
        requests: List of disk block positions to access
        start: Initial position of disk head

    Returns:
        Complete access sequence including the start position
    """
    sequence = [start]
    if not requests:
        return sequence

    positions = sorted(set(requests))

    up_requests = [r for r in positions if r > start]
    down_requests = [r for r in positions if r < start]

    # Go up, then jump to beginning and continue
    sequence.extend(up_requests)
    if down_requests:
        sequence.append(0)  # Jump to beginning
        sequence.extend(down_requests)

    return sequence


def look_scheduling(requests, start, direction='up'):
    """LOOK disk scheduling algorithm.

    Args:
        requests: List of disk block positions to access
        start: Initial position of disk head
        direction: Initial direction ('up' or 'down')

    Returns:
        Complete access sequence including the start position
    """
    sequence = [start]
    if not requests:
        return sequence

    positions = sorted(set(requests))

    up_requests = [r for r in positions if r > start]
    down_requests = [r for r in positions if r < start]

    if direction == 'up':
        # Go up first, then reverse and go down
        sequence.extend(up_requests)
        sequence.extend(reversed(down_requests))
    else:
        # Go down first, then reverse and go up
        sequence.extend(reversed(down_requests))
        sequence.extend(up_requests)

    return sequence


def c_look_scheduling(requests, start):
    """C-LOOK disk scheduling algorithm.

    Args:
        requests: List of disk block positions to access
        start: Initial position of disk head

    Returns:
        Complete access sequence including the start position
    """
    sequence = [start]
    if not requests:
        return sequence

    positions = sorted(set(requests))

    up_requests = [r for r in positions if r > start]
    down_requests = [r for r in positions if r < start]

    # Go up to end, then jump to lowest position and continue
    sequence.extend(up_requests)
    if down_requests:
        sequence.extend(down_requests)

    return sequence


def visualize_disk_scheduling(algorithm_name, sequence, disk_size=100):
    """Visualize the disk scheduling algorithm.

    Args:
        algorithm_name: Name of the algorithm
        sequence: Complete access sequence including the start position
        disk_size: Total size of the disk

    Returns:
        matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot the sequence
    ax.plot(sequence, range(len(sequence)), 'b-o', markersize=8)

    # Label the points with their respective order
    for i, (x, y) in enumerate(zip(sequence, range(len(sequence)))):
        ax.annotate(f"{i}: {x}", (x, y), textcoords="offset points",
                    xytext=(5, 5), ha='center')

    # Calculate total head movement
    head_movement = sum(abs(sequence[i] - sequence[i - 1]) for i in range(1, len(sequence)))

    # Set labels and title
    ax.set_xlim(0, disk_size)
    ax.set_ylim(-1, len(sequence))
    ax.set_xlabel('Disk Position')
    ax.set_ylabel('Request Sequence')
    ax.set_title(f'{algorithm_name} Disk Scheduling\nTotal Head Movement: {head_movement} cylinders')

    # Invert y-axis to show sequence going down
    ax.invert_yaxis()

    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    return fig