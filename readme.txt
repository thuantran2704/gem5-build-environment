/workspace/
├── gem5_base/                      # gem5 simulator
│   └── build/ARM/gem5.opt         # gem5 executable
│
└── demo/
    |-- base_arch.py               # gem5 config without argument flags
    ├── base_arch_new.py           # gem5 config (hardware setup with arugment flags)
    ├── dijkstra.cpp               # workload source
    ├── bin/
    │   └── dijkstra               # compiled ARM binary
    ├── data/                       #input graphs
    │   ├── small.txt
    │   ├── medium.txt
    │   └── large.txt

    │   └── ...
    ├── scripts/
        ├── run_matrix.py          # runs all simulations
        └── scrape_results.py      # builds CSV
├── final_results.csv          # final output
├-- final_results.txt          # final output
├── results/                    #results
│   ├── small_256KiB_LocalBP/
│   │   ├── stats.txt
│   │   └── stats.json


OUTPUT RESULTS FILE: final_results.csv; final_results.txt

each result run folder contains:
citations.bib
config.dot
config.dot.pdf
config.dot.svg
config.ini
config.json
stats.json
stats.txt



-- Compile Dijkstra (ARM):
aarch64-linux-gnu-g++ \
  demo/dijkstra.cpp \
-o demo/bin/dijkstra

-- Run ONE gem5 test

```
/gem5_base/build/ARM/gem5.opt \
--outdir=demo/results/test_run \
  demo/base_arch_new.py \
--binary=demo/bin/dijkstra \
--input=demo/data/small.txt \
--l2_size=512KiB \
--bp_type=BiModeBP
```

-- Run all experiments

python3 demo/scripts/run_matrix.py

Creates:

```
/workspace/results/
├── small_256KiB_LocalBP/
├── small_512KiB_BiModeBP/
└── ...
```



-- Scrape stats command:
python3 demo/script/scrape_results.txt

Stats:

board.processor.cores.core.ipc
board.processor.cores.core.cpi
board.cache_hierarchy.l1dcaches.overallMissRate::total
board.cache_hierarchy.l1icaches.overallMissRate::total
board.cache_hierarchy.l2cache.overallMissRate::total
board.processor.cores.core.branchPred.lookups_0::total
board.processor.cores.core.branchPred.mispredicted_0::total
board.memory.mem_ctrl.dram.avgRdBW