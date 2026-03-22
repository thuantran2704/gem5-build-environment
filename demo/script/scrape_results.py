import os
import csv
import re

# --- SETTINGS ---
RESULTS_DIR = "results/"
OUT_CSV = "final_results.csv"
OUT_TXT = "final_results.txt"  # <-- Added TXT output file

# The mapping you requested: { "Label": "gem5_stat_key" }
STAT_MAP = {
    "Total Instructions": "simInsts",
    "CPI": "board.processor.cores.core.cpi",
    "IPC": "board.processor.cores.core.ipc",
    "L1D Miss Rate": "board.cache_hierarchy.l1dcaches.overallMissRate::total",
    "L1I Miss Rate": "board.cache_hierarchy.l1icaches.overallMissRate::total",
    "L2 Miss Rate": "board.cache_hierarchy.l2cache.overallMissRate::total",
    "DRAM Read BW": "board.memory.mem_ctrl.dram.avgRdBW",
    "Total Branches": "board.processor.cores.core.branchPred.lookups_0::total",
    "Branch Mispredicts": "board.processor.cores.core.branchPred.mispredicted_0::total"
}

def extract_stat(text, key):
    """Finds the numeric value for a specific key in the stats file."""
    pattern = rf"^{re.escape(key)}\s+([0-9.eE+-]+)"
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1) if match else "NaN"

def run_scraper():
    # Prepare the CSV Header
    header = ["Folder", "Graph", "L2_Size", "BP_Type"] + list(STAT_MAP.keys())
    rows = [header]

    # This list will hold the formatted text for the .txt file
    txt_output_lines = []

    if not os.path.exists(RESULTS_DIR):
        print(f"Error: {RESULTS_DIR} not found.")
        return

    # Loop through each simulation result folder
    for folder in sorted(os.listdir(RESULTS_DIR)):
        folder_path = os.path.join(RESULTS_DIR, folder)
        stats_path = os.path.join(folder_path, "stats.txt")

        if not os.path.isdir(folder_path) or not os.path.exists(stats_path):
            continue

        with open(stats_path, "r") as f:
            content = f.read()

        # Parse folder name (e.g., small_1MiB_LocalBP)
        parts = folder.split("_")
        if len(parts) == 3:
            graph, l2, bp = parts
        else:
            graph, l2, bp = folder, "n/a", "n/a"

        # Build the data row for CSV
        data_row = [folder, graph, l2, bp]

        # Build the readable block for the TXT file
        txt_output_lines.append(f"=== {folder} ===")
        txt_output_lines.append(f"Graph: {graph}")
        txt_output_lines.append(f"L2_Size: {l2}")
        txt_output_lines.append(f"BP_Type: {bp}")

        for label, key in STAT_MAP.items():
            val = extract_stat(content, key)
            data_row.append(val)
            txt_output_lines.append(f"{label}: {val}") # Add to TXT output

        txt_output_lines.append("") # Add a blank line between folders for readability

        rows.append(data_row)

    # Write the CSV file
    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    # Write the TXT file
    with open(OUT_TXT, "w") as f:
        f.write("\n".join(txt_output_lines))

    print(f"Success! {OUT_CSV} and {OUT_TXT} created with {len(rows)-1} simulation results.")

if __name__ == "__main__":
    run_scraper()