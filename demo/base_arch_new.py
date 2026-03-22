import argparse
import os

import m5
from m5.objects import ArmO3CPU, InstCsvTrace

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


parser = argparse.ArgumentParser()
parser.add_argument("--binary", required=True)
parser.add_argument("--input", required=True)
parser.add_argument("--l2_size", default="2MiB")
parser.add_argument("--bp_type", default="TournamentBP",
                    choices=["LocalBP", "BiModeBP", "TournamentBP"])
parser.add_argument("--l2_assoc", type=int, default=16)
args = parser.parse_args()

llc_size = args.l2_size
llc_assoc = args.l2_assoc
bp_type = args.bp_type


class MyOutOfOrderCore(BaseCPUCore):
    def __init__(self, width, rob_size, num_int_regs, num_fp_regs):
        core = ArmO3CPU()
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



        # inst_trace = InstCsvTrace()
        # inst_trace.trace_file = "inst_trace.csv"
        # inst_trace.trace_fetch = True
        # inst_trace.trace_mem = True
        # inst_trace.start_after_inst = 0
        # inst_trace.stop_after_inst = 0
        # core.probeListener = inst_trace

        super().__init__(core, ISA.ARM)


class MyOutOfOrderProcessor(BaseCPUProcessor):
    def __init__(self, width, rob_size, num_int_regs, num_fp_regs):
        super().__init__(
            cores=[MyOutOfOrderCore(width, rob_size, num_int_regs, num_fp_regs)]
        )


cache_hierarchy = PrivateL1SharedL2CacheHierarchy(
    l1d_size="32KiB",
    l1i_size="32KiB",
    l2_size=llc_size,
    l2_assoc=llc_assoc,
)

main_memory = SingleChannelDDR4_2400(size="4GB")

my_ooo_processor = MyOutOfOrderProcessor(
    width=8, rob_size=192, num_int_regs=256, num_fp_regs=256
)

for core in my_ooo_processor.get_cores():
    if bp_type == "LocalBP":
        core.core.branchPred = m5.objects.LocalBP()
    elif bp_type == "BiModeBP":
        core.core.branchPred = m5.objects.BiModeBP()
    else:
        core.core.branchPred = m5.objects.TournamentBP()

board = SimpleBoard(
    clk_freq="3GHz",
    processor=my_ooo_processor,
    memory=main_memory,
    cache_hierarchy=cache_hierarchy,
)

binary = BinaryResource(local_path=args.binary)

board.set_se_binary_workload(
    binary,
    arguments=[args.input],
)

simulator = Simulator(board=board)

outdir = m5.options.outdir
simulator.add_text_stats_output(os.path.join(outdir, "stats.txt"))
simulator.add_json_stats_output(os.path.join(outdir, "stats.json"))

print("Starting simulation...")
print(f"binary={args.binary}")
print(f"input={args.input}")
print(f"l2_size={args.l2_size}")
print(f"bp_type={args.bp_type}")

simulator.run()
print("Done.")