from models.cpu_scheduling.fcfs_cpu_scheduling_model import Job, fcfs_schedule

class FCFSCPUController:
    def __init__(self, view):
        self.view = view
        self.view.set_generate_command(self.generate_gantt)

    def add_job(self):
        """Add a single job from the view's entry fields, after validation."""
        try:
            name, arrival_str, burst_str = self.view.get_entry_data()
            arrival = int(arrival_str)
            burst = int(burst_str)
            if burst <= 0:
                raise ValueError("Burst time must be > 0")
        except ValueError as e:
            self.view.show_error(str(e))
            return

        # Retrieve current valid jobs from the view (includes all filled rows)
        current_jobs = self.view.get_all_jobs()

        # Check for duplicate name
        if any(job.name.lower() == name.lower() for job in current_jobs):
            self.view.show_error(f"A process with the name '{name}' already exists.\nPlease use a unique name.")
            return

        # Check for duplicate arrival time
        if any(job.arrival == arrival for job in current_jobs):
            self.view.show_error(f"A process with arrival time {arrival} already exists.\nEach process must have a unique arrival time.")
            return

        # All checks passed – create the job
        job = Job(name, arrival, burst)
        # The view will add the job to its internal list / treeview
        self.view.add_job_to_tree(job)
        self.view.clear_entries()

    def _validate_jobs(self, jobs):
        """
        Returns (True, "") if the job list is valid for generating a Gantt chart.
        Returns (False, error_message) otherwise.
        """
        if not jobs:
            return False, "Add at least one valid process first."

        # Check for duplicate names (case-insensitive)
        seen_names = set()
        for job in jobs:
            lower = job.name.lower()
            if lower in seen_names:
                return False, f"Duplicate process name: '{job.name}'.\nAll process names must be unique."
            seen_names.add(lower)

        # Check for duplicate arrival times
        seen_arrivals = set()
        for job in jobs:
            if job.arrival in seen_arrivals:
                return False, f"Duplicate arrival time: {job.arrival}.\nAll arrival times must be unique."
            seen_arrivals.add(job.arrival)

        return True, ""

    def generate_gantt(self):
        # Fetch all valid jobs from the view
        jobs = self.view.get_all_jobs()

        # Run full validation
        valid, error_msg = self._validate_jobs(jobs)
        if not valid:
            self.view.show_error(error_msg)
            return

        # Schedule and display
        events = fcfs_schedule(jobs)
        self.view.display_gantt(events)

        # Compute and show metrics
        n = len(jobs)
        total_tat = total_wt = total_rt = 0
        for job in jobs:
            tat = job.finish - job.arrival
            wt = tat - job.burst
            rt = job.start - job.arrival
            total_tat += tat
            total_wt += wt
            total_rt += rt

        avg_tat = total_tat / n
        avg_wt = total_wt / n
        avg_rt = total_rt / n

        total_time = max(job.finish for job in jobs)
        total_burst = sum(job.burst for job in jobs)
        cpu_util = (total_burst / total_time) * 100 if total_time > 0 else 0
        throughput = n / total_time if total_time > 0 else 0

        self.view.display_results(avg_tat, avg_wt, avg_rt, cpu_util, throughput)