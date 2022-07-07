#!/usr/bin/env python
from bcc import BPF, USDT
import sys

bpf = """
#include <uapi/linux/ptrace.h>

static int strncmp(char *s1, char *s2, int size) {
    for (int i = 0; i < size; ++i)
        if (s1[i] != s2[i])
            return 1;
    return 0;
}

int trace_file_transfers(struct pt_regs *ctx) {
    uint64_t fnameptr;
    char fname[128]={0}, searchname[8]="request";

    bpf_usdt_readarg(1, ctx, &fnameptr);
    bpf_probe_read(&fname, sizeof(fname), (void *)fnameptr);

        bpf_trace_printk("\%s \\n", fname);
    return 0;
};
"""

u = USDT(pid=int(sys.argv[1]))
u.enable_probe(probe="function__entry", fn_name="trace_file_transfers")
b = BPF(text=bpf, usdt_contexts=[u])
while 1:
    try:
        (_, _, _, _, ts, msg) = b.trace_fields()
    except ValueError:
        continue
    print("%-18.9f %s" % (ts, msg))