import matplotlib.pyplot as plt
import numpy as np
from file_manager import get_disk


def show_disk():
    """Show a visualization of the disk blocks and their allocation."""
    disk = get_disk()
    fig, ax = plt.subplots(figsize=(12, 2))
    unique_files = list(set(b for b in disk if b != 'free'))

    # Create visually distinct colors for files
    color_map = {name: f"#{hash(name) % 0xFFFFFF:06x}" for name in unique_files}
    color_map['free'] = "#d3d3d3"  # Light gray for free blocks

    # Draw rectangles representing disk blocks
    for i, block in enumerate(disk):
        color = color_map.get(block, "#d3d3d3")
        ax.add_patch(plt.Rectangle((i, 0), 1, 1, edgecolor='black', facecolor=color))

        # Add a symbol inside each block
        symbol = '.' if block == 'free' else '■'
        ax.text(i + 0.5, 0.5, symbol, ha='center', va='center', fontsize=8)

    # Set plot limits and remove axes
    ax.set_xlim(0, len(disk))
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Add a legend
    legend_elements = [plt.Rectangle((0, 0), 1, 1, color=color_map[k]) for k in color_map]
    ax.legend(legend_elements, color_map.keys(), loc="upper center",
              ncol=min(5, len(color_map)), bbox_to_anchor=(0.5, 1.2))

    plt.tight_layout()
    return fig


def show_disk_access_animation(sequence, disk_size=100):
    """Create an animation-like visualization of disk head movement.

    Args:
        sequence: List of disk positions accessed in order
        disk_size: Total size of the disk

    Returns:
        matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(12, 4))

    # Plot the disk track
    ax.plot([0, disk_size], [0, 0], 'k-', linewidth=2)

    # Add markers for sequence positions
    ax.scatter(sequence, [0] * len(sequence), s=100, c='blue', zorder=3)

    # Connect the points with arrows to show movement
    for i in range(1, len(sequence)):
        ax.annotate('',
                    xy=(sequence[i], 0),
                    xytext=(sequence[i - 1], 0),
                    arrowprops=dict(arrowstyle='->', color='red', lw=1.5))

        # Add a small label with the sequence number
        ax.text(sequence[i], 0.2, f"{i}", ha='center')

    # Mark the start position distinctively
    ax.scatter([sequence[0]], [0], s=150, c='green', zorder=4, marker='*')
    ax.text(sequence[0], 0.2, "Start", ha='center')

    # Calculate total head movement
    total_movement = sum(abs(sequence[i] - sequence[i - 1]) for i in range(1, len(sequence)))

    # Set labels and title
    ax.set_xlim(-1, disk_size + 1)
    ax.set_ylim(-0.5, 1)
    ax.set_xlabel('Disk Position')
    ax.set_title(f'Disk Head Movement\nTotal Movement: {total_movement} cylinders')
    ax.set_yticks([])  # Hide y-axis

    # Add grid for x-axis
    ax.grid(axis='x', linestyle='--', alpha=0.7)

    plt.tight_layout()
    return fig


def visualize_file_fragmentation():
    """Visualize file fragmentation in the disk."""
    disk = get_disk()
    if not disk:
        return None

    # Get unique files
    files = set(block for block in disk if block != 'free')

    # Count fragmentation (number of discontinuous regions)
    fragmentation_data = {}
    for file in files:
        regions = 0
        in_region = False
        for block in disk:
            if block == file and not in_region:
                # Start of a new region
                regions += 1
                in_region = True
            elif block != file:
                in_region = False

        # Count blocks occupied by this file
        block_count = disk.count(file)
        fragmentation_data[file] = {
            'regions': regions,
            'blocks': block_count,
            'frag_ratio': regions / block_count if block_count > 0 else 0
        }

    # Create visualization
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create bar chart
    files = list(fragmentation_data.keys())
    regions = [fragmentation_data[f]['regions'] for f in files]
    blocks = [fragmentation_data[f]['blocks'] for f in files]

    # Calculate positions
    x = np.arange(len(files))
    width = 0.35

    # Create bars
    ax.bar(x - width / 2, blocks, width, label='Total Blocks')
    ax.bar(x + width / 2, regions, width, label='Fragmented Regions')

    # Add fragmentation ratio as text
    for i, file in enumerate(files):
        ratio = fragmentation_data[file]['frag_ratio']
        ax.text(i, max(blocks[i], regions[i]) + 0.1,
                f"Ratio: {ratio:.2f}", ha='center')

    # Add labels and legend
    ax.set_xlabel('Files')
    ax.set_ylabel('Count')
    ax.set_title('File Fragmentation Analysis')
    ax.set_xticks(x)
    ax.set_xticklabels(files)
    ax.legend()

    plt.tight_layout()
    return fig


def visualize_disk_usage_over_time(file_history):
    """Visualize disk usage changes over time.

    Args:
        file_history: List of (timestamp, used_blocks) tuples
    """
    if not file_history or len(file_history) < 2:
        return None

    fig, ax = plt.subplots(figsize=(10, 6))

    # Extract data
    timestamps = [entry[0] for entry in file_history]
    used_blocks = [entry[1] for entry in file_history]

    # Plot line
    ax.plot(timestamps, used_blocks, 'b-o', linewidth=2)

    # Fill area under the curve
    ax.fill_between(timestamps, used_blocks, alpha=0.3)

    # Set labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Used Blocks')
    ax.set_title('Disk Usage Over Time')

    # Format x-axis for better readability
    fig.autofmt_xdate()

    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    return fig