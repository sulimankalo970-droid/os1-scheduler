from collections import deque
import copy

class Process:
    pass

def create_process(name, arrival, burst, priority):
    p = Process()
    p.name = name
    p.arrival = int(arrival)
    p.burst = int(burst)
    p.priority = int(priority)
    p.remaining = int(burst)
    p.finish = 0
    p.turnaround = 0
    p.waiting = 0
    p.response = -1
    return p

def get_id(p):
    digits = "".join(c for c in p.name if c.isdigit())
    return int(digits) if digits else 0

def read_file(filename="input.txt"):
    processes = []
    quantum = 2
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            words = line.split()
            first_word = next(iter(words))
            if first_word.lower() == "q":
                _, q_str = words
                quantum = int(q_str)
            else:
                name, arr, burst, prio = words
                processes.append(create_process(name, arr, burst, prio))
    return processes, quantum

def compute_averages(processes):
    count = len(processes)
    sum_wait = 0
    sum_turn = 0
    sum_resp = 0
    for p in processes:
        p.turnaround = p.finish - p.arrival
        p.waiting = p.turnaround - p.burst
        sum_wait += p.waiting
        sum_turn += p.turnaround
        sum_resp += p.response
    return sum_wait / count, sum_turn / count, sum_resp / count

def run_fcfs(input_procs):
    procs = copy.deepcopy(input_procs)
    procs.sort(key=lambda p: (p.arrival, get_id(p)))
    time = 0
    gantt = []
    for p in procs:
        if time < p.arrival:
            gantt.append(("IDLE", time, p.arrival))
            time = p.arrival
        p.response = time - p.arrival
        start = time
        time += p.burst
        p.finish = time
        gantt.append((p.name, start, time))
    avgs = compute_averages(procs)
    return procs, gantt, avgs

def run_rr(input_procs, quantum):
    procs = copy.deepcopy(input_procs)
    procs.sort(key=lambda p: (p.arrival, get_id(p)))
    time = 0
    gantt = []
    ready = deque()
    pending = deque(procs)
    total = len(procs)
    done = 0

    while done < total:
        while pending:
            head = next(iter(pending))
            if head.arrival <= time:
                ready.append(pending.popleft())
            else:
                break

        if not ready:
            next_arr = next(iter(pending)).arrival
            gantt.append(("IDLE", time, next_arr))
            time = next_arr
            continue

        curr = ready.popleft()
        if curr.response == -1:
            curr.response = time - curr.arrival

        step = min(quantum, curr.remaining)
        start = time
        time += step
        curr.remaining -= step
        gantt.append((curr.name, start, time))

        while pending:
            head = next(iter(pending))
            if head.arrival <= time:
                ready.append(pending.popleft())
            else:
                break

        if curr.remaining > 0:
            ready.append(curr)
        else:
            curr.finish = time
            done += 1

    procs.sort(key=lambda p: (p.arrival, get_id(p)))
    avgs = compute_averages(procs)
    return procs, gantt, avgs

def show_output(title, procs, gantt, avgs):
    print(f"\n=== {title} ===")
    chart = " | ".join(f"{name} {s}-{e}" for name, s, e in gantt)
    print(f"Gantt: | {chart} |\n")
    print(f"{'Proc':<6} {'Finish':<8} {'Turnaround':<12} {'Waiting':<10} {'Response':<10}")
    for p in procs:
        print(f"{p.name:<6} {p.finish:<8} {p.turnaround:<12} {p.waiting:<10} {p.response:<10}")
    w, t, r = avgs
    print(f"\nAverage: waiting = {w:.2f}  turnaround = {t:.2f}  response = {r:.2f}")

def show_comparison(fcfs_avgs, rr_avgs, quantum):
    print("\n=== Comparison ===")
    fw, ft, fr = fcfs_avgs
    rw, rt, rr = rr_avgs
    rows = (
            ("Waiting", fw, rw),
            ("Turnaround", ft, rt),
            ("Response", fr, rr)
        )
    for label, f_val, r_val in rows:
            if f_val < r_val:
                res = f"FCFS is better ({f_val:.2f} vs {r_val:.2f})"
            elif r_val < f_val:
                res = f"RR (q={quantum}) is better ({r_val:.2f} vs {f_val:.2f})"
            else:
                res = f"Tie ({f_val:.2f} vs {r_val:.2f})"
            print(f"{label:<11}: {res}")

def main():
    procs, q = read_file("input.txt")
    f_procs, f_gantt, f_avgs = run_fcfs(procs)
    show_output("FCFS", f_procs, f_gantt, f_avgs)
    r_procs, r_gantt, r_avgs = run_rr(procs, q)
    show_output(f"RR (q = {q})", r_procs, r_gantt, r_avgs)
    show_comparison(f_avgs, r_avgs, q)

main()