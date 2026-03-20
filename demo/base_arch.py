from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.private_l1_shared_l2_cache_hierarchy import (
    PrivateL1SharedL2CacheHierarchy,
)
from gem5.components.memory.single_channel import SingleChannelDDR4_2400
from gem5.resources.resource import BinaryResource
from gem5.simulate.simulator import Simulator
from gem5.isas import ISA

from gem5.components.processors.base_cpu_core import BaseCPUCore
from gem5.components.processors.base_cpu_processor import BaseCPUProcessor

from m5.objects import ArmO3CPU
from m5.objects import TournamentBP
from m5.objects import InstCsvTrace

import m5
import os
from pathlib import Path

# --- EXPERIMENT PARAMETERS (Can be passed via argparse) ---
llc_size = "2MiB"  # Sweep: 512KiB, 1MiB, 2MiB, 4MiB
llc_assoc = 16  # Test associativity impact
bp_type = "TournamentBP"  # Choices: LocalBP, BiModeBP, TournamentBP


class MyOutOfOrderCore(BaseCPUCore):
    def __init__(self, width, rob_size, num_int_regs, num_fp_regs):
        core = ArmO3CPU()  # ARM O3
        core.fetchWidth = width
        core.decodeWidth = width
        core.renameWidth = width
        core.dispatchWidth = width
        core.issueWidth = width
        core.wbWidth = width
        core.commitWidth = width

        core.numROBEntries = rob_size
        core.numPhysIntRegs = num_int_regs
        core.numPhysFloatRegs = num_fp_regs

        # core.branchPred = TournamentBP()

        inst_trace = InstCsvTrace()
        inst_trace.trace_file = "inst_trace.csv"
        inst_trace.trace_fetch = True
        inst_trace.trace_mem = True
        inst_trace.start_after_inst = 0
        inst_trace.stop_after_inst = 0
        core.probeListener = inst_trace

        super().__init__(core, ISA.ARM)  # compiled ARM


class MyOutOfOrderProcessor(BaseCPUProcessor):
    def __init__(self, width, rob_size, num_int_regs, num_fp_regs):
        super().__init__(
            cores=[MyOutOfOrderCore(width, rob_size, num_int_regs, num_fp_regs)]
        )


# 1. Setup Cache Hierarchy (Shared L2 acts as your LLC)
cache_hierarchy = PrivateL1SharedL2CacheHierarchy(
    l1d_size="32KiB", l1i_size="32KiB", l2_size=llc_size, l2_assoc=llc_assoc
)


main_memory = SingleChannelDDR4_2400(size="4GB")

my_ooo_processor = MyOutOfOrderProcessor(
    width=8, rob_size=192, num_int_regs=256, num_fp_regs=256
)

# Manually inject the Branch Predictor into the O3 CPU models
for core in my_ooo_processor.get_cores():
    if bp_type == "LocalBP":
        core.core.branchPred = m5.objects.LocalBP()
    elif bp_type == "BiModeBP":
        core.core.branchPred = m5.objects.BiModeBP()
    elif bp_type == "TournamentBP":
        core.core.branchPred = m5.objects.TournamentBP()

board = SimpleBoard(
    clk_freq="3GHz",
    processor=my_ooo_processor,
    memory=main_memory,
    cache_hierarchy=cache_hierarchy,
)

# board.set_se_binary_workload(CustomResource("path/to/your/dijkstra_binary"))

from gem5.resources.resource import BinaryResource

binary = BinaryResource(local_path="dijkstra_arm")

board.set_se_binary_workload(
    binary,
    arguments=["input.txt"],
)

simulator = Simulator(board=board)


outdir = m5.options.outdir

simulator.add_text_stats_output(os.path.join(outdir, "stats.txt"))
simulator.add_json_stats_output(os.path.join(outdir, "stats.json"))

simulator.run()
