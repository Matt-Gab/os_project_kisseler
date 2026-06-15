# controllers/cpu_scheduling/rr_cpu_scheduling_controller.py
from models.cpu_scheduling.rr_cpu_scheduling_model import Job, rr_schedule

class RRCPUController:
    def __init__(self, view):
        self.view = view
        self.view.set_generate_command(self.generate_gantt)

    def generate_gantt(self):
        job_dicts = self.view.get_all_jobs()
        if not job_dicts:
            self.view.show_info("No Jobs", "Add at least one valid process first.")
            return

        # Read quantum from the view's global control
        quantum_val = self.view.get_global_value("quantum")
        try:
            quantum = int(quantum_val)
            if quantum <= 0:
                raise ValueError("Quantum must be positive.")
        except (TypeError, ValueError):
            self.view.show_error("Invalid Time Quantum. Please enter a positive integer.")
            return

        jobs = [Job(d["name"], d["arrival"], d["burst"], extra=d["extra"]) for d in job_dicts]

        # Duplicate checks
        seen_names = set()
        seen_arrivals = set()
        for job in jobs:
            lower = job.name.lower()
            if lower in seen_names:
                self.view.show_error(f"Duplicate process name: '{job.name}'.")
                return
            seen_names.add(lower)
            if job.arrival in seen_arrivals:
                self.view.show_error(f"Duplicate arrival time: {job.arrival}.")
                return
            seen_arrivals.add(job.arrival)

        events = rr_schedule(jobs, quantum)
        self.view.display_gantt(events)

        n = len(jobs)
        total_tat = sum(job.finish - job.arrival for job in jobs)
        total_wt = sum((job.finish - job.arrival) - job.burst for job in jobs)
        total_rt = sum(job.start - job.arrival for job in jobs)
        avg_tat = total_tat / n
        avg_wt = total_wt / n
        avg_rt = total_rt / n

        total_time = max(job.finish for job in jobs)
        total_burst = sum(job.burst for job in jobs)
        cpu_util = (total_burst / total_time) * 100 if total_time > 0 else 0
        throughput = n / total_time if total_time > 0 else 0

        self.view.display_results(avg_tat, avg_wt, avg_rt, cpu_util, throughput)