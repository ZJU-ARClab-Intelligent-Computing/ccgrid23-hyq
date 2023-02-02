#!/usr/bin/python3

from itertools import cycle
import os
import sys
import json


# 将用KB表示的块大小转换为用MB或GB表示，例如：
# 输入："1024k"
# 输出："1m"
def shorten_bs(bs):
    next_unit = {
        "b": "k",
        "k": "m",
        "m": "g",
        "g": "t"
    }

    unit = bs[-1]
    bs_num = int(bs[:-1])
    while bs_num >= 1024:
        bs_num = int(bs_num / 1024)
        unit = next_unit[unit]

    return str(bs_num) + unit


# 将块大小或块大小范围转化为数字，便于比较大小
def bsrange2num(bsrange):
    size_map = {
        "b": 1024 ** 0,
        "k": 1024 ** 1,
        "m": 1024 ** 2,
        "g": 1024 ** 3,
        "t": 1024 ** 4
    }
    bs = bsrange.split("-")[0]
    return int(bs[:-1]) * size_map[bs[-1]]


# 解析一个fio生成的IO性能报告文件
# 输入：文件路径，xxx/xxx.json
# 输出：带宽，IOPS，延迟，读延迟分布，写延迟分布
def parse_io_perf_file(bench_dirname,pattern):
    print("------enter parse_io_perf_file:",bench_dirname,pattern)
    
    filename_list= bench_dirname.split("/")
    key_str=filename_list[-1].split("_")
    print(filename_list)
    print(key_str)
    count = 0
    iops,thru_put, lat_avg, lat_p50, lat_p75, lat_p99, lat_p999, lat_p9999 = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0

    
    for filename in os.listdir(f"{bench_dirname}/{pattern}"):
    # for filename in os.listdir(f"{bench_dirname}"):
            if filename.endswith(".tsv"):
                print("------",bench_dirname,filename)
                with open(f"{bench_dirname}/{pattern}/{filename}", "r") as file:
                # with open(f"{bench_dirname}/{filename}", "r") as file:
                    lines = file.readlines()
                    last_line = lines[-1]
                    # print("------last_line",last_line)
                    parts = last_line.strip().split("\t")
                    # print("parts",parts)
                    iops += float(parts[0])
                    thru_put += float(parts[1])
                    lat_avg += float(parts[11])
                    lat_p50 += float(parts[12])
                    lat_p75 += float(parts[13])
                    lat_p99 += float(parts[14])
                    lat_p999 += float(parts[15])
                    lat_p9999 += float(parts[16])
                    count += 1

    lat_avg /= count
    lat_p50 /= count
    lat_p75 /= count
    lat_p99 /= count
    lat_p999 /= count
    lat_p9999 /= count
    return iops,thru_put, lat_avg, lat_p50, lat_p75, lat_p99, lat_p999, lat_p9999,key_str[0],key_str[1]




# def parse_io_perf_file(bench_dirname):
#     #print("enter parse_io_perf_file:",bench_dirname)
#     count = 0
#     iops,thru_put, lat_avg, lat_p50, lat_p75, lat_p99, lat_p999, lat_p9999 = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0
#     vm_index_list = os.listdir(bench_dirname)
#     for vm_index in vm_index_list:
#         for filename in os.listdir(f"{bench_dirname}/{vm_index}/readrandom"):
#             if filename.endswith(".tsv"):
#                 print(bench_dirname+"/"+vm_index+"/"+filename)
#                 with open(f"{bench_dirname}/{vm_index}/readrandom/{filename}", "r") as file:
#                     lines = file.readlines()
#                     last_line = lines[-1]
#                     # print("------last_line",last_line)
#                     parts = last_line.strip().split("\t")
#                     # print("parts",parts)
#                     iops += float(parts[0])
#                     thru_put += float(parts[1])
#                     lat_avg += float(parts[11])
#                     lat_p50 += float(parts[12])
#                     lat_p75 += float(parts[13])
#                     lat_p99 += float(parts[14])
#                     lat_p999 += float(parts[15])
#                     lat_p9999 += float(parts[16])
#                     count += 1

#     lat_avg /= count
#     lat_p50 /= count
#     lat_p75 /= count
#     lat_p99 /= count
#     lat_p999 /= count
#     lat_p9999 /= count
#     return iops,thru_put, lat_avg, lat_p50, lat_p75, lat_p99, lat_p999, lat_p9999


# 解析一个iostat生成的CPU利用率报告文件
# 输入：文件路径，xxx/xxx.txt
# 输出：平均CPU利用率，每秒的CPU利用率，平均TPS，每秒的TPS
def parse_cpu_load_file(filename):
    with open(filename, "r") as file:
        cpu_load_found = False
        cpu_loads = []
        io_tpss = []
        io_tps, io_tps_cnt = 0.0, 0
        for line in file.readlines():
            if cpu_load_found:
                cpu_loads.append(100.0 - float(line.strip().split()[-1]))
                cpu_load_found = False
            elif line.startswith("avg-cpu:"):
                cpu_load_found = True

            if line.startswith("nvme"):
                io_tps += float(line.strip().split()[1])
                io_tps_cnt += 1
            elif len(line.strip()) == 0 and io_tps_cnt > 0:
                io_tpss.append(io_tps)
                io_tps_cnt = 0
                io_tps = 0.0

        return sum(cpu_loads) / len(cpu_loads), cpu_loads, sum(io_tpss) / len(io_tpss), io_tpss


# 解析某个ioperf文件夹下的所有IO性能信息文件
# 输入：xxx/xxx/ioperf/
# 输出：一个IO性能列表，其中的每一项包含的信息如下：
# {
#     "benchmark": 测试类型,
#     "thru_put": 吞吐量,
#     "name": 使用的调度方案的名字
# }
def parse_io_perfs(dirname, name,pattern):
    print("enter parse_io_perfs:", dirname)
    filename_list= dirname.split("/")
    print(filename_list)
    io_perfs = []
    # bench_dirnames = os.listdir(dirname)
    # print("bech_dirnames:", bench_dirnames)
    # for bench_dirname in bench_dirnames:
    benchmark = dirname
    # thru_put, lat_avg, lat_p50, lat_p75, lat_p99, lat_p999, lat_p9999 = parse_io_perf_file(
    # f"{dirname}/{bench_dirname}")
    iops, thru_put, lat_avg, lat_p50, lat_p75, lat_p99, lat_p999, lat_p9999,vm_num,cycle_cnt = parse_io_perf_file(
        f"{dirname}",pattern)
    io_perfs.append({
        "type":filename_list[-2],
        "pattern":pattern,
        "vm_num":int(vm_num),
        # "benchmark": benchmark,
        "iops":iops/1000,
        "thru_put": thru_put / 1000,
        "lat_avg": lat_avg / 1000,
        "lat_p50": lat_p50 / 1000,
        "lat_p75": lat_p75 / 1000,
        "lat_p99": lat_p99 / 1000,
        "lat_p999": lat_p999 / 1000,
        "lat_p9999": lat_p9999 / 1000,
        # **kwargs
        "cycle_cnt":cycle_cnt,
        "name":vm_num+"-"+cycle_cnt
    })
    # print(io_perfs)
    return io_perfs


# 解析某个cpuload或host_cpuload文件夹下的所有CPU占用率信息文件
# 输入：xxx/xxx/cpuload/或xxx/xxx/host_cpuload
# 输出：一个CPU占用率列表，其中的每一项包含的信息如下：
# {
#     "benchmark": 测试类型,
#     "avg": 平均CPU占用率,
#     "seq": 每秒的CPU占用率,
#     "io_tps": 平均TPS，单位为k,
#     "io_tps_seq": 每秒的TPS,
#     "name": 使用的调度方案的名字
# }
def parse_cpu_loads(dirname, **kwargs):
    cpu_loads = []
    filenames = os.listdir(dirname)
    for filename in filenames:
        [benchmark, _] = filename.split(".")
        avg, seq, io_tps, io_tps_seq = parse_cpu_load_file(
            f"{dirname}/{filename}")
        cpu_loads.append({
            "benchmark": benchmark,
            "avg": avg,
            "seq": seq,
            "io_tps": io_tps / 1000,
            "io_tps_seq": io_tps_seq,
            **kwargs
        })
    return cpu_loads


# 从一个results文件夹下读入所有数据
# 输入：路径，xxx/results_xxx
# 输出：target端CPU利用率数据，IO性能数据，host端CPU利用率数据，target端内存带宽占用率数据
def get_data(io_perfs,path,pattern):
    # print("enter get data:", path)
    # io_perfs = []

    # 将需要绘制的CPU占用率数据、IO性能数据以及内存带宽占用率数据都分别解析到一个数组里
    for folder in os.listdir(path):
        #print(folder)
        # if(folder == "report.tsv"):
        #     # if(folder=)
        #     # print("folder:", folder)
        name = folder.split("_")[0]
        #     # print("name:", name)
        # io_perfs.extend(parse_io_perfs(f"{path}/{folder}/ioperf", name=name))

        io_perfs.extend(parse_io_perfs(f"{path}/{folder}", name=name,pattern=pattern))
    # print(io_perfs)

    return io_perfs


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

    return sorted(list(keys)), groups


# 将某个数据复制一份返回
def copy(value):
    new = {}
    for key, value in value.items():
        new[key] = value
    return new


# 对IO性能数据进行合并操作，参见merge_by函数
def merge_io_perf(values):
    count = 1
    merged = copy(values[0])
    for value in values[1:]:
        merged["iops"] += value["iops"]
        merged["thru_put"] += value["thru_put"]
        merged["lat_avg"] += value["lat_avg"]
        merged["lat_p50"] += value["lat_p50"]
        merged["lat_p75"] += value["lat_p75"]
        merged["lat_p99"] += value["lat_p99"]
        merged["lat_p999"] += value["lat_p999"]
        merged["lat_p9999"] += value["lat_p9999"]
        count += 1


    merged["iops"] /= count
    merged["thru_put"] /= count
    merged["lat_avg"] /= count
    merged["lat_p50"] /= count
    merged["lat_p75"] /= count
    merged["lat_p99"] /= count
    merged["lat_p999"] /= count
    merged["lat_p9999"] /= count
    return merged


# 对CPU占用率数据进行合并操作，参见merge_by函数
def merge_cpu_load(values):
    count = 1
    merged = copy(values[0])
    for value in values[1:]:
        merged["avg"] += value["avg"]
        merged["io_tps"] += value["io_tps"]
        count += 1

    merged["avg"] /= count
    merged["io_tps"] /= count
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


# 基于每个数据的多个key为其创建一个新的key，例如：
# 输入：items=[
#   {"name": "a", "devname": "name0n1", "bw": 123},
#   {"name": "a", "devname": "name1n1", "bw": 456},
#   {"name": "b", "devname": "name0n1", "bw": 789},
#   {"name": "b", "devname": "name1n1", "bw": 1011}
# ], new_key_name="name_devname", key_names=["name", "devname"]
#
# 输出：[
#   {"name": "a", "devname": "name0n1", "bw": 123, "name_devname": "a/nvme0n1"},
#   {"name": "a", "devname": "name1n1", "bw": 456, "name_devname": "a/nvme1n1"},
#   {"name": "b", "devname": "name0n1", "bw": 789, "name_devname": "b/nvme0n1"},
#   {"name": "b", "devname": "name1n1", "bw": 1011, "name_devname": "b/nvme1n1"}
# ]
def combine_key(items, new_key_name, *key_names):
    for item in items:
        keys = []
        for key_name in key_names:
            keys.append(item[key_name])
        item[new_key_name] = "/".join(keys)
    return items


# 计算value相对于base的百分比
def normalize(value, base):
    return int((value / base) * 10000) / 100


# 将CPU利用率归一化
def normalize_cpu_loads(bases, values):
    new_values = []
    for base, value in zip(bases, values):
        new_value = copy(value)
        new_value["avg"] = normalize(new_value["avg"], base["avg"])
        new_values.append(new_value)
    return new_values


# 将IO性能归一化
def normalize_io_perfs(bases, values):
    new_values = []
    for base, value in zip(bases, values):
        new_value = copy(value)
        new_value["iops"] = normalize(
            new_value["iops"], base["iops"])
        print(new_value["thru_put"], base["thru_put"])
        new_value["thru_put"] = normalize(
            new_value["thru_put"], base["thru_put"])
        new_value["lat_avg"] = normalize(new_value["lat_avg"], base["lat_avg"])
        new_value["lat_p50"] = normalize(new_value["lat_p50"], base["lat_p50"])
        new_value["lat_p75"] = normalize(new_value["lat_p75"], base["lat_p75"])
        new_value["lat_p99"] = normalize(new_value["lat_p99"], base["lat_p99"])
        new_value["lat_p999"] = normalize(
            new_value["lat_p999"], base["lat_p999"])
        new_value["lat_p9999"] = normalize(
            new_value["lat_p9999"], base["lat_p9999"])
        new_values.append(new_value)
    return new_values

def plot_set_tick(ax, top_bool):
    if(top_bool):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    else:
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)

    ax.tick_params("y", which='major',
                   length=15, width=2.0,
                   colors="black")
    ax.tick_params(which="minor",
                   length=5, width=1.0,
                   labelsize=100, labelcolor="0.25")