from datetime import datetime
import heapq
import matplotlib.pyplot as plt


class Process:
    def __init__(self, pid, action, target_file, priority=0, user='user'):
        self.pid = pid
        self.action = action  # read, write, delete
        self.target_file = target_file
        self.priority = priority
        self.user = user
        self.timestamp = datetime.now()
        self.status = "waiting"  # waiting, running, completed
        self.start_time = None
        self.end_time = None

    def __lt__(self, other):
        # Compare processes based on priority (lower value = higher priority)
        if self.priority != other.priority:
            return self.priority < other.priority
        # If same priority, use timestamp (FIFO)
        return self.timestamp < other.timestamp

    def start(self):
        self.status = "running"
        self.start_time = datetime.now()

    def complete(self):
        self.status = "completed"
        self.end_time = datetime.now()

    def get_duration(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0


class ProcessManager:
    def __init__(self, scheduling_algorithm="priority"):
        """Initialize the process manager with a specified scheduling algorithm.

        Args:
            scheduling_algorithm: The algorithm to use for scheduling.
                Options: "priority", "fcfs", "round_robin", "sjf"
        """
        self.queue = []
        self.completed = []
        self.algorithm = scheduling_algorithm
        self.current_process = None
        self.time_quantum = 2  # For round-robin scheduling

    def add_process(self, process):
        """Add a process to the queue using the current scheduling algorithm."""
        if self.algorithm == "priority":
            heapq.heappush(self.queue, process)
        elif self.algorithm == "fcfs":
            # First-come, first-served - just append to list
            self.queue.append(process)
        elif self.algorithm == "sjf":
            # Shortest Job First - we'll use priority as a proxy for job length
            heapq.heappush(self.queue, process)
        else:
            # Default to priority queue
            heapq.heappush(self.queue, process)

    def get_next_process(self):
        """Get the next process based on the scheduling algorithm."""
        if not self.queue:
            return None

        if self.current_process:
            # Complete the current process
            self.current_process.complete()
            self.completed.append(self.current_process)
            self.current_process = None

        if self.algorithm == "priority" or self.algorithm == "sjf":
            next_process = heapq.heappop(self.queue)
        elif self.algorithm == "fcfs":
            next_process = self.queue.pop(0) if self.queue else None
        elif self.algorithm == "round_robin":
            # In round robin, we would cycle through processes
            next_process = self.queue.pop(0) if self.queue else None
            # If using real round robin, we'd add back to queue after time quantum
            # But we're simplifying for this simulator
        else:
            # Default to priority queue
            next_process = heapq.heappop(self.queue) if self.queue else None

        if next_process:
            next_process.start()
            self.current_process = next_process

        return next_process

    def list_processes(self):
        """Return list of processes in queue."""
        return list(self.queue)

    def list_completed_processes(self):
        """Return list of completed processes."""
        return self.completed

    def change_algorithm(self, new_algorithm):
        """Change the scheduling algorithm."""
        valid_algorithms = ["priority", "fcfs", "round_robin", "sjf"]
        if new_algorithm not in valid_algorithms:
            raise ValueError(f"Invalid algorithm: {new_algorithm}. Choose from {valid_algorithms}")

        # We need to rebuild the queue for the new algorithm
        old_queue = list(self.queue)
        self.queue = []
        self.algorithm = new_algorithm

        # Re-add processes with the new algorithm
        for process in old_queue:
            self.add_process(process)

    def visualize_gantt_chart(self):
        """Create a Gantt chart of completed processes."""
        if not self.completed:
            return None

        fig, ax = plt.subplots(figsize=(10, 5))

        # Sort by start time
        processes = sorted(self.completed, key=lambda p: p.start_time)

        # Plot each process as a horizontal bar
        y_positions = range(len(processes))
        labels = [f"{p.pid}: {p.action} {p.target_file}" for p in processes]

        # Calculate durations
        durations = [p.get_duration() for p in processes]
        start_times = [(p.start_time - processes[0].start_time).total_seconds() for p in processes]

        # Create distinct colors based on priority
        colors = [plt.cm.viridis(p.priority / 10) for p in processes]

        # Plot bars
        bars = ax.barh(y_positions, durations, left=start_times, height=0.5,
                       color=colors, alpha=0.8)

        # Add labels
        ax.set_yticks(y_positions)
        ax.set_yticklabels(labels)
        ax.set_xlabel('Time (seconds)')
        ax.set_title(f'Process Execution Timeline ({self.algorithm.upper()})')

        # Add priority legend
        for i, bar in enumerate(bars):
            ax.text(start_times[i] + durations[i] / 2,
                    y_positions[i],
                    f"P:{processes[i].priority}",
                    ha='center',
                    va='center',
                    color='white',
                    fontweight='bold')

        ax.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        return fig
