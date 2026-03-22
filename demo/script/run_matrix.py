import os
import itertools
import subprocess

# ✅ update these paths
GEM5_BIN = "/workspace/gem5_base/build/ARM/gem5.opt"
CONFIG = "/workspace/demo/base_arch_new.py"
BINARY = "/workspace/demo/bin/dijkstra"

graphs = {
    "small": "/workspace/demo/data/small.txt",
    "medium": "/workspace/demo/data/medium.txt",
    "large": "/workspace/demo/data/large.txt",
}

cache_sizes = ["256KiB", "512KiB", "1MiB"]
bp_types = ["LocalBP", "BiModeBP", "TournamentBP"]

#for smoke test:
# graphs = {"small": "/workspace/demo/data/small.txt"}
# cache_sizes = ["256KiB"]
# bp_types = ["LocalBP"]

os.makedirs("results", exist_ok=True)

for size_name, graph_path in graphs.items():
    for cache, bp in itertools.product(cache_sizes, bp_types):
        run_name = f"{size_name}_{cache}_{bp}"
        outdir = os.path.join("results", run_name)
        os.makedirs(outdir, exist_ok=True)

        cmd = [
            GEM5_BIN,
            f"--outdir={outdir}",
            CONFIG,
            f"--binary={BINARY}",
            f"--input={graph_path}",
            f"--l2_size={cache}",
            f"--bp_type={bp}",
        ]

        print("Running:", " ".join(cmd))
        subprocess.run(cmd, check=True)