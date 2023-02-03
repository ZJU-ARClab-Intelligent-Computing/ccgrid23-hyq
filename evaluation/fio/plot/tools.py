#!/usr/bin/python3

import json
import os
import re
import sys

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


ORDERED_NAMES = ["Non-offloading", "Offloading", "HyQ"]

SCHEME_NAME_MAPS = {
    "non-offloading": "Non-offloading",
    "offloading": "Offloading",
    "hyq": "HyQ",
}

BAR_COLORS = {
    "Non-offloading": "#FFFFFF",
    "Offloading": "#D5D5D5",
    "HyQ": "#8F8F8F",
}

MARKERS = {
    "Non-offloading": "D",
    "Offloading": "^",
    "HyQ": "s",
}

LINE_STYLES = {
    "Non-offloading": "dashdot",
    "Offloading": "dotted",
    "HyQ": "solid",
}

LINE_COLORS = {
    "Non-offloading": {
        "randread": "#5BAF33",
        "randwrite": "#5BAF33",
        "seqwrite": "#5BAF33",
        "seqread": "#5BAF33",
    },
    "Offloading": {
        "randread": "#006FBF",
        "randwrite": "#006FBF",
        "seqwrite": "#006FBF",
        "seqread": "#006FBF",
    },
    "HyQ": {
        "randread": "#FE5F05",
        "randwrite": "#FE5F05",
        "seqwrite": "#FE5F05",
        "seqread": "#FE5F05",
    },
}


# 解析一个fio生成的IO性能报告文件
# 输入：文件路径
# 输出：rbw, riops, rlatency,wbw, wiops, wlatency
def parse_fio_perf_file(filename):
    # print(f"Parsing io perf: {filename}")
    with open(filename, "r") as file:
        result = json.load(file)["jobs"][0]
        rbw = result["read"]["bw"]
        riops = result["read"]["iops"]
        rlatency = result["read"]["lat_ns"]["mean"]
        wbw = result["write"]["bw"]
        wiops = result["write"]["iops"]
        wlatency = result["write"]["lat_ns"]["mean"]
        try:
            rpercentile = result["read"]["clat_ns"]["percentile"]
        except:
            rpercentile = {}
        try:
            wpercentile = result["write"]["clat_ns"]["percentile"]
        except:
            wpercentile = {}

        return rbw, riops, rlatency, rpercentile, wbw, wiops, wlatency, wpercentile


# 解析一个top生成的CPU利用率报告文件
# 输入：文件路径
# 输出：us，sy,id,cutil
def parse_cpu_load_file(filename):
    # print(f"Parsing cpu util: {filename}")
    with open(filename, "r") as file:
        us_list = []
        sy_list = []
        id_list = []
        cutil_list = []
        for line in file.readlines():
            line = line.strip()
            if not line.startswith("%Cpu(s):"):
                continue

            if len(line.split()) < 8:
                continue

            res = re.split(r"[ ,]+", line)
            us, sy, id = float(res[1]), float(res[3]), float(res[7])
            cutil = 100.0 - id

            us_list.append(us)
            sy_list.append(sy)
            id_list.append(id)
            cutil_list.append(cutil)

        us_list.pop(0)
        sy_list.pop(0)
        id_list.pop(0)
        cutil_list.pop(0)

        return (
            sum(us_list) / len(us_list),
            sum(sy_list) / len(sy_list),
            sum(id_list) / len(id_list),
            sum(cutil_list) / len(cutil_list),
        )


# 将IO性能数据汇总到io_perf数组中
def read_fio_perfs(fio_path):
    fio_perfs = []
    # 将IO性能数据汇总到io_perf数组中
    for filename in os.listdir(fio_path):
        [basename, _] = filename.split(".")
        [
            scheme,
            rw,
            rwmixwrite,
            bs,
            ba,
            numjobs,
            iodepth,
            rate,
            _,
            numcores,
            cycle_cnt,
        ] = basename.split("_")
        (
            rbw,
            riops,
            rlatency,
            rpercentile,
            wbw,
            wiops,
            wlatency,
            wpercentile,
        ) = parse_fio_perf_file(f"{fio_path}/{filename}")

        fio_perfs.append(
            {
                "scheme": SCHEME_NAME_MAPS[scheme],
                "rw": rw,
                "rwmixwrite": int(rwmixwrite),
                "blockalign": ba,
                "blocksize": bs,
                "iodepth": int(iodepth),
                "numjobs": int(numjobs),
                "cycle_cnt": int(cycle_cnt),
                "rate": int(rate) * 16 / 1000,
                "numcores": int(numcores),
                "rbandwidth": rbw / 1024,  # MB
                "riops": riops / 1000,  # k
                "rlatency": rlatency / 1000,  # us
                "rpercentile": rpercentile,
                "wbandwidth": wbw / 1024,  # MB
                "wiops": wiops / 1000,  # k
                "wlatency": wlatency / 1000,  # us
                "wpercentile": wpercentile,
                "iops": riops / 1000 + wiops / 1000,  # k
                "bandwidth": rbw / 1024 + wbw / 1024,  # MB
                "casename": rw + "\n" + bs + "-" + numjobs + "-" + iodepth,
                "latency": rlatency / 1000 + wlatency / 1000,
            }
        )

    return fio_perfs


# 将CPU占用率数据汇总到cpu_load
def read_cpu_loads(cpu_path):
    cpu_loads = []
    for filename in os.listdir(cpu_path):
        [basename, _] = filename.split(".")
        [
            scheme,
            rw,
            rwmixwrite,
            bs,
            ba,
            numjobs,
            iodepth,
            rate,
            _,
            numcores,
            cycle_cnt,
        ] = basename.split("_")

        us, sy, id, cutil = parse_cpu_load_file(f"{cpu_path}/{filename}")

        cpu_loads.append(
            {
                "scheme": SCHEME_NAME_MAPS[scheme],
                "rw": rw,
                "rwmixwrite": int(rwmixwrite),
                "blockalign": ba,
                "blocksize": bs,
                "iodepth": int(iodepth),
                "numjobs": int(numjobs),
                "cycle_cnt": int(cycle_cnt),
                "rate": int(rate) * 16 / 1000,
                "numcores": int(numcores),
                "us": us,
                "sy": sy,
                "id": id,
                "cutil": cutil * 48 / 100,
                "casename": rw + "\n" + bs + "-" + numjobs + "-" + iodepth,
            }
        )
    return cpu_loads


def filter_results(results, requirements):
    def check(item):
        for key, value in requirements.items():
            if item[key] not in value:
                return False
        return True

    results = filter(check, results)
    return list(results)


def isnumber(aString):
    try:
        float(aString)
        return True
    except:
        return False


# 基于每个数据的多个key为其创建一个新的key，例如：
# 输入：items=[
#   {"name": "a", "devname": "name0n1", "bw": 123},
#   {"name": "a", "devname": "name1n1", "bw": 456},
#   {"name": "b", "devname": "name0n1", "bw": 789},
#   {"name": "b", "devname": "name1n1", "bw": 1011}
# ], new_key_name="name_devname", key_names=["name", "devname"]
#
# 输出：[
#   {"name": "a", "devname": "name0n1", "bw": 123, "name_devname": "a/nvme1n1"},
#   {"name": "a", "devname": "name1n1", "bw": 456, "name_devname": "a/nvme2n1"},
#   {"name": "b", "devname": "name0n1", "bw": 789, "name_devname": "b/nvme1n1"},
#   {"name": "b", "devname": "name1n1", "bw": 1011, "name_devname": "b/nvme2n1"}
# ]
def combine_key(items, new_key_name, *key_names):
    for item in items:
        keys = []
        for key_name in key_names:
            keys.append(str(item[key_name]))
        item[new_key_name] = "-".join(keys)
    return items


# 将一个数据列表按照其中元素的某个key分组，例如：
# 输入：key="name", items=[
#   {"name": "a", "bw": 123},
#   {"name": "a", "bw": 456},
#   {"name": "b", "bw": 789},
#   {"name": "b", "bw": 1011}
# ]
# 输出：["a", "b"], {
#   "a": [
#       {"name": "a", "bw": 123},
#       {"name": "a", "bw": 456},
#   ],
#   "b": [
#       {"name": "b", "bw": 789},
#       {"name": "b", "bw": 1011},
#   ],
# }
def group_by(key, items):
    keys, groups = set(), dict()
    for item in items:
        values = groups.setdefault(item[key], [])
        values.append(item)
        keys.add(item[key])
    # print(groups)
    return sorted(list(keys)), groups


# 对IO性能数据进行合并操作，参见merge_by函数
def merge_io_perf(values):
    count = 1
    merged = copy(values[0])
    # print(merged)
    for value in values[1:]:
        merged["rbandwidth"] += value["rbandwidth"]
        merged["riops"] += value["riops"]
        merged["rlatency"] += value["rlatency"]
        merged["wbandwidth"] += value["wbandwidth"]
        merged["wiops"] += value["wiops"]
        merged["wlatency"] += value["wlatency"]
        merged["bandwidth"] += value["bandwidth"]
        merged["iops"] += value["iops"]
        merged["latency"] += value["latency"]
        for k, v in merged["rpercentile"].items():
            merged["rpercentile"][k] += value["rpercentile"][k]
        for k, v in merged["wpercentile"].items():
            merged["wpercentile"][k] += value["wpercentile"][k]
        count += 1
        # print(merged["wlatency"])
        # print(count)

    merged["rbandwidth"] /= count
    merged["riops"] /= count
    merged["rlatency"] /= count
    merged["wbandwidth"] /= count
    merged["wiops"] /= count
    merged["wlatency"] /= count
    merged["iops"] /= count
    merged["bandwidth"] /= count
    merged["latency"] /= count
    for k, v in merged["rpercentile"].items():
        merged["rpercentile"][k] /= count
    for k, v in merged["wpercentile"].items():
        merged["wpercentile"][k] /= count
    return merged


# 将某个数据复制一份返回
def copy(value):
    new = {}
    for key, value in value.items():
        new[key] = value
    return new


# 对CPU占用率数据进行合并操作，参见merge_by函数
def merge_cpu_load(values):
    count = 1
    merged = copy(values[0])
    for value in values[1:]:

        merged["us"] += value["us"]
        merged["sy"] += value["sy"]
        merged["id"] += value["id"]
        merged["cutil"] += value["cutil"]
        count += 1

    merged["us"] /= count
    merged["sy"] /= count
    merged["id"] /= count
    merged["cutil"] /= count
    return merged


# 将一个数据列表按照其中元素的某个key使用给定的合并函数进行合并，例如：
# 输入：key="name", func=对bw取平均的函数, items=[
#   {"name": "a", "bw": 123},
#   {"name": "a", "bw": 456},
#   {"name": "b", "bw": 789},
#   {"name": "b", "bw": 1011}
# ]
# 输出：[
#   {"name": "a", "bw": (123 + 456) / 2},
#   {"name": "b", "bw": (789 + 1011) / 2}
# ]
def merge_by(key, func, items):
    merged = []
    _, grouped = group_by(key, items)
    for _, value in grouped.items():
        merged.append(func(value))

    return merged


def filter_lat(per_list, percents, latencies):
    percents_res = []
    latencies_res = []
    for index, per in enumerate(percents):
        if per in per_list:
            percents_res.append(percents[index])
            latencies_res.append(latencies[index])
    return percents_res, latencies_res


def plot_grid(plt):
    plt.grid(axis="y", color="silver", linewidth=0.7, zorder=0)


def plot_set_tick(ax):
    ax.tick_params("y", which="major", length=7, colors="black")
    ax.tick_params("x", length=7, colors="black")


# Unified font type and size.
plt.rcParams.update({"font.size": 22, "font.family": "Times New Roman"})
