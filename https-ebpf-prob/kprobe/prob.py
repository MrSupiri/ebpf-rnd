#!/usr/bin/python
# @lint-avoid-python-3-compatibility-imports
#
# tcptop    Summarize TCP send/recv throughput by host.
#           For Linux, uses BCC, eBPF. Embedded C.
#
# USAGE: tcptop [-h] [-C] [-S] [-p PID] [interval [count]] [-4 | -6]
#
# This uses dynamic tracing of kernel functions, and will need to be updated
# to match kernel changes.
#
# WARNING: This traces all send/receives at the TCP level, and while it
# summarizes data in-kernel to reduce overhead, there may still be some
# overhead at high TCP send/receive rates (eg, ~13% of one CPU at 100k TCP
# events/sec. This is not the same as packet rate: funccount can be used to
# count the kprobes below to find out the TCP rate). Test in a lab environment
# first. If your send/receive rate is low (eg, <1k/sec) then the overhead is
# expected to be negligible.
#
# ToDo: Fit output to screen size (top X only) in default (not -C) mode.
#
# Copyright 2016 Netflix, Inc.
# Licensed under the Apache License, Version 2.0 (the "License")
#
# 02-Sep-2016   Brendan Gregg   Created this.

from __future__ import print_function
from bcc import BPF
from bcc.containers import filter_by_containers
import argparse
from socket import inet_ntop, AF_INET, AF_INET6
from struct import pack
from time import sleep, strftime
from subprocess import call
from collections import namedtuple, defaultdict

# arguments
def range_check(string):
    value = int(string)
    if value < 1:
        msg = "value must be stricly positive, got %d" % (value,)
        raise argparse.ArgumentTypeError(msg)
    return value

examples = """examples:
    ./tcptop           # trace TCP send/recv by host
    ./tcptop -C        # don't clear the screen
    ./tcptop -p 181    # only trace PID 181
    ./tcptop --cgroupmap mappath  # only trace cgroups in this BPF map
    ./tcptop --mntnsmap mappath   # only trace mount namespaces in the map
    ./tcptop -4        # trace IPv4 family only
    ./tcptop -6        # trace IPv6 family only
"""
parser = argparse.ArgumentParser(
    description="Summarize TCP send/recv throughput by host",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)
parser.add_argument("-C", "--noclear", action="store_true",
    help="don't clear the screen")
parser.add_argument("-S", "--nosummary", action="store_true",
    help="skip system summary line")
parser.add_argument("-p", "--pid",
    help="trace this PID only")
parser.add_argument("interval", nargs="?", default=1, type=range_check,
    help="output interval, in seconds (default 1)")
parser.add_argument("count", nargs="?", default=-1, type=range_check,
    help="number of outputs")
parser.add_argument("--cgroupmap",
    help="trace cgroups in this BPF map only")
parser.add_argument("--mntnsmap",
    help="trace mount namespaces in this BPF map only")
group = parser.add_mutually_exclusive_group()
group.add_argument("-4", "--ipv4", action="store_true",
    help="trace IPv4 family only")
group.add_argument("-6", "--ipv6", action="store_true",
    help="trace IPv6 family only")
parser.add_argument("--ebpf", action="store_true",
    help=argparse.SUPPRESS)
args = parser.parse_args()
debug = 0

# linux stats
loadavg = "/proc/loadavg"

# define BPF program
with open('prob.c', 'r') as f:
    bpf_text = f.read()

# code substitutions
if args.pid:
    bpf_text = bpf_text.replace('FILTER_PID',
        'if (pid != %s) { return 0; }' % args.pid)
else:
    bpf_text = bpf_text.replace('FILTER_PID', '')
if args.ipv4:
    bpf_text = bpf_text.replace('FILTER_FAMILY',
        'if (family != AF_INET) { return 0; }')
elif args.ipv6:
    bpf_text = bpf_text.replace('FILTER_FAMILY',
        'if (family != AF_INET6) { return 0; }')
bpf_text = bpf_text.replace('FILTER_FAMILY', '')
bpf_text = filter_by_containers(args) + bpf_text
if debug or args.ebpf:
    print(bpf_text)
    if args.ebpf:
        exit()

TCPSessionKey = namedtuple('TCPSession', ['pid', 'name', 'laddr', 'lport', 'daddr', 'dport'])

def get_ipv4_session_key(k):
    return TCPSessionKey(pid=k.pid,
                         name=k.name,
                         laddr=inet_ntop(AF_INET, pack("I", k.saddr)),
                         lport=k.lport,
                         daddr=inet_ntop(AF_INET, pack("I", k.daddr)),
                         dport=k.dport)

def get_ipv6_session_key(k):
    return TCPSessionKey(pid=k.pid,
                         name=k.name,
                         laddr=inet_ntop(AF_INET6, k.saddr),
                         lport=k.lport,
                         daddr=inet_ntop(AF_INET6, k.daddr),
                         dport=k.dport)

# initialize BPF
b = BPF(text=bpf_text)

# ipv4_send_bytes = b["ipv4_send_bytes"]
# ipv4_recv_bytes = b["ipv4_recv_bytes"]
# ipv6_send_bytes = b["ipv6_send_bytes"]
# ipv6_recv_bytes = b["ipv6_recv_bytes"]

# print('Tracing... Output every %s secs. Hit Ctrl-C to end' % args.interval)

# # output
# i = 0
# exiting = False
# while i != args.count and not exiting:
#     try:
#         sleep(args.interval)
#     except KeyboardInterrupt:
#         exiting = True

#     # header
#     if args.noclear:
#         print()
#     else:
#         call("clear")
#     if not args.nosummary:
#         with open(loadavg) as stats:
#             print("%-8s loadavg: %s" % (strftime("%H:%M:%S"), stats.read()))

#     # IPv4: build dict of all seen keys
#     ipv4_throughput = defaultdict(lambda: [0, 0])
#     for k, v in ipv4_send_bytes.items():
#         key = get_ipv4_session_key(k)
#         ipv4_throughput[key][0] = v.value
#     ipv4_send_bytes.clear()

#     for k, v in ipv4_recv_bytes.items():
#         key = get_ipv4_session_key(k)
#         ipv4_throughput[key][1] = v.value
#     ipv4_recv_bytes.clear()

#     if ipv4_throughput:
#         print("%-7s %-12s %-21s %-21s %6s %6s" % ("PID", "COMM",
#             "LADDR", "RADDR", "RX_KB", "TX_KB"))

#     # output
#     for k, (send_bytes, recv_bytes) in sorted(ipv4_throughput.items(),
#                                               key=lambda kv: sum(kv[1]),
#                                               reverse=True):
#         print("%-7d %-12.12s %-21s %-21s %6d %6d" % (k.pid,
#             k.name,
#             k.laddr + ":" + str(k.lport),
#             k.daddr + ":" + str(k.dport),
#             int(recv_bytes / 1024), int(send_bytes / 1024)))

#     # IPv6: build dict of all seen keys
#     ipv6_throughput = defaultdict(lambda: [0, 0])
#     for k, v in ipv6_send_bytes.items():
#         key = get_ipv6_session_key(k)
#         ipv6_throughput[key][0] = v.value
#     ipv6_send_bytes.clear()

#     for k, v in ipv6_recv_bytes.items():
#         key = get_ipv6_session_key(k)
#         ipv6_throughput[key][1] = v.value
#     ipv6_recv_bytes.clear()

#     if ipv6_throughput:
#         # more than 80 chars, sadly.
#         print("\n%-7s %-12s %-32s %-32s %6s %6s" % ("PID", "COMM",
#             "LADDR6", "RADDR6", "RX_KB", "TX_KB"))

#     # output
#     for k, (send_bytes, recv_bytes) in sorted(ipv6_throughput.items(),
#                                               key=lambda kv: sum(kv[1]),
#                                               reverse=True):
#         print("%-7d %-12.12s %-32s %-32s %6d %6d" % (k.pid,
#             k.name,
#             k.laddr + ":" + str(k.lport),
#             k.daddr + ":" + str(k.dport),
#             int(recv_bytes / 1024), int(send_bytes / 1024)))

#     i += 1


def print_ipv4_event(cpu, data, size):
    event = b["ipv4_events"].event(data)

    dataDict = {
        "SourceIP": inet_ntop(AF_INET, pack("I", event.saddr)),
        "LocalPort": event.lport,
        "DestinationIP": inet_ntop(AF_INET, pack("I", event.daddr)),
        "DestinationPort": event.dport,
        "TransmitBytes": int(event.tx_b),
        "ReceiveBytes": int(event.rx_b),
        "Duration(ms)": float(event.span_us) / 1000
    }

    print(dataDict)

def print_ipv6_event(cpu, data, size):
    event = b["ipv6_events"].event(data)

    dataDict = {
        "SourceIP": inet_ntop(AF_INET6, event.saddr),
        "LocalPort": event.lport,
        "DestinationIP": inet_ntop(AF_INET6, event.daddr),
        "DestinationPort": event.dport,
        "TransmitBytes": int(event.tx_b),
        "ReceiveBytes": int(event.rx_b),
        "Duration(ms)": float(event.span_us) / 1000,

    }

    print(dataDict)


# read events
b["ipv4_events"].open_perf_buffer(print_ipv4_event, page_cnt=64)
b["ipv6_events"].open_perf_buffer(print_ipv6_event, page_cnt=64)
print("Probing")
while 1:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exit()