import sys
import re


def parse_gem5_stats(file_path):
    # Dictionary of metrics we want to extract
    metrics = {
        "simInsts": "Total Instructions",
        "board.processor.cores.core.cpi": "CPI (Cycles Per Instruction)",
        "board.processor.cores.core.ipc": "IPC (Instructions Per Cycle)",
        "board.cache_hierarchy.l1dcaches.overallMissRate::total": "L1 Data Cache Miss Rate",
        "board.cache_hierarchy.l1icaches.overallMissRate::total": "L1 Inst Cache Miss Rate",
        "board.cache_hierarchy.l2cache.overallMissRate::total": "L2 Cache Miss Rate",
        "board.memory.mem_ctrl.dram.avgRdBW": "DRAM Read Bandwidth (MiB/s)",
        "board.processor.cores.core.branchPred.lookups_0::total": "Total Branches",
        "board.processor.cores.core.branchPred.mispredicted_0::total": "Branch Mispredictions",
    }

    results = {}

    try:
        with open(file_path, "r") as f:
            for line in f:
                # Clean up whitespace and ignore empty lines
                parts = line.split()
                if len(parts) < 2:
                    continue

                stat_name = parts[0]
                stat_value = parts[1]

                if stat_name in metrics:
                    results[metrics[stat_name]] = stat_value

        # Calculate derived PhD metrics
        if "Total Branches" in results and "Branch Mispredictions" in results:
            miss_rate = (
                float(results["Branch Mispredictions"])
                / float(results["Total Branches"])
            ) * 100
            results["Branch Misprediction Rate (%)"] = f"{miss_rate:.2f}%"

        print("=" * 40)
        print(" DIJKSTRA ARCHITECTURAL PERFORMANCE REPORT ")
        print("=" * 40)
        for key, value in results.items():
            print(f"{key:<30} : {value}")
        print("=" * 40)

    except FileNotFoundError:
        print(f"Error: {file_path} not found.")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "m5out/stats.txt"
    parse_gem5_stats(path)
