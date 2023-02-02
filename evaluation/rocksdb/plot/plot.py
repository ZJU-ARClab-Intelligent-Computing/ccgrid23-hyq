#!/usr/bin/python3

from pickle import TRUE
import sys
# from typing import final
import matplotlib.pyplot as plt
import time
import os

from tools import *

# plt.rcParams.update({"hatch.linewidth": 5.0})
plt.rcParams.update({'font.size': 84, 'font.family': 'Times New Roman'})
# plt.rcParams.update({'font.size': 60)



EDGE_COLORS = {
    # 区分不同的方案
    # "native": "#545454",
    # "kernel": "#FFFFFF",
    # "qp-pt": "#A7A7A7",
    # "spdk-vhost": "#FFFFFF"
    "native": "#404040",
    "native-0": "#404040",
    "qp-pt": "#7F7F7F",
    "spdk-vhost": "#FFFFFF",
    "kernel": "#C0C0C0",
}

# 柱状图内条纹类型
# HATCHS = {
#     # 区分不同的方案
#     # "dummy": "***",
#     "kernel": "-",
#     "offload": "|",
#     "scheduler-cx5": "+",
#     "scheduler-cx6": "+",
#     "mixed": "///",
#     # "utility": "///",
#     "utility-driver": "\\\\\\",
#     # "latency": "+++",
#     "latency-driver": "xxx",
#     # "static": "***",
#     "static-driver": "+++",
# }

HATCHS = {
    "native": "-",
    "kernel": "/",
    "qp-pt": "+",
    "spdk-vhost": "|"
}

# 绘制一个柱状图
# 输入：
#   plt：matplotlib的plot实例
#   title：图片标题
#   items：需要绘制的数据
#   x_key：用作x轴的数据的key
#   y_key：用作y轴的数据的key
#   label：柱状图的图例说明
#   offset, width, edgecolor, hatch：控制柱状图位置、宽度、颜色和条纹类型的参数
#   labeled：是否需要添加图例说明


def plot_bar(plt, items, x_key, y_key, label, offset, width, edgecolor, hatch, bar_label=False):
    x = [item[x_key] for item in items]
    y = [item[y_key] for item in items]
    x_lable = [item["vm_num"] for item in items]
    ticks = [i for i in range(len(items))]
    print(edgecolor)
    print(hatch)
    container = plt.bar([i + offset for i in ticks], y, width=width,
                         color=edgecolor, edgecolor="black", linewidth=3, label=label,hatch=hatch)

    plt.set_xticks(ticks)
    plt.set_xticklabels(x_lable)
    # if bar_label:
    #     plt.bar_label(container, labels=["%.4f" % y[0], ""], padding=20, rotation=-90)

    for a, b in zip([i + offset for i in ticks], y):
        plt.text(a, b+0.06, '%.1f' % float(b), ha='center',
                 va='bottom', fontsize=80, rotation=90, clip_on=False)
    # plt.set_ylim(bottom=0, top=120)


# 绘制网格
def plot_grid(plt):
    plt.grid(axis="y", color="silver", linewidth=0.7)


# ORDERED_NAMES = ["static", "utility", "latency", "static-driver", "utility-driver", "latency-driver", "mixed", "kernel", "offload", "dummy"]
ORDERED_NAMES = ["native", "qp-pt","kernel", "spdk-vhost"]


def plot_result(title, names,  io_perfs,  x_key, filename, bool_normalized):
    
   
    # 创建绘图
    # fig, ((thru_put, lat), (cpu, host_cpu)) = plt.subplots(nrows=2, ncols=2, figsize=(48, 36))

    fig, (iops) = plt.subplots(nrows=1, ncols=1, figsize=(48, 36))

    fig.subplots_adjust(left=0.10, right=0.97, top=0.95,
                        bottom=0.1, hspace=0.15, wspace=0.25)

    # 设置x轴名称
    iops.set_xlabel("Number of Threads")

    # 设置y轴名称
    iops.set_ylabel("Normalied Throughput(%)")

    # 计算每一个条的宽度
    width = 0.6 / len(names)

    # 设置每一个条的偏移量
    offset = -((len(names) - 1) / 2.0)

    plot_set_tick(iops, True)

    for name in ORDERED_NAMES:
        if name in names:
            plot_bar(iops, io_perfs[name], x_key, "iops", name,
                     offset * width, width, EDGE_COLORS[name], HATCHS[name])
            # plot_bar(iops, "IOPS", io_perfs[name], x_key, "iops", name, offset * width, width, EDGE_COLORS[name], HATCHS[name])
            # plot_bar(bw, "Bandwidth", io_perfs[name], x_key, "bandwidth", name, offset * width, width, EDGE_COLORS[name], HATCHS[name])

            offset += 1.0

    iops.legend(loc="upper center",ncol=4)
    
    # plt1.legend(loc="upper right",ncol=4,columnspacing=0.3,labelspacing=0.5,markerscale=0.01,handletextpad=0.3)

    # 绘制网格
    # plot_grid(iops)
    if (bool_normalized):
        title = title + filename + "_normalized"
        iops.set_ylim(bottom=0, top=120)
    else:
        title = title + filename

    print(title)

    fig.savefig(f"{title}.pdf", dpi=300)
    fig.savefig(f"{title}.png", dpi=300)


ALLOWED_NAMES = {"native", "qp-pt", "spdk-vhost","kernel"}


if __name__ == "__main__":
    # nowdate=time.strftime("%Y%m%d%H%M%S", time.localtime())
    nowdate="20220913154639"
    res_dir = "/home/jinzhen/backup/dragonball/plot_rocksdb/result/"+nowdate+"_0913mark/"
    # os.makedirs(res_dir) 

    # cpu_loads, io_perfs, host_cpu_loads = get_data(sys.argv[1])
    # /home/jinzhen/backup/binary/rocksdb_results/qp-pt/20220725131811

    # pattern_list = ["readrandom", "overwrite", "readwhilewriting"]
    pattern_list = ["readrandom", "overwrite","mergerandom"]

    for pattern in pattern_list:
        io_dir = "/home/jinzhen/backup/binary/rocksdb_results/"
        type_list = os.listdir(io_dir)
        io_perfs = []
        print(type_list)

        # pattern_list = ["bulkload", "readrandom"]

        for type in type_list:  # native,qp-pt,spdk-vhost
                type_dir = io_dir + type
                date_list = os.listdir(type_dir)
                # print("jjjjj", date_list)
                data_dir = type_dir + '/'+date_list[-1]
                # print("data_dir",data_dir)
                # /home/jinzhen/backup/binary/rocksdb_results/qp-pt/20220725131811/10"
                vm_list = os.listdir(data_dir)
                # io_perfs = io_perfs.extend(get_data(data_dir)) # 每一个虚拟机的数据，还需要汇总
                io_perfs = get_data(io_perfs, data_dir,
                                    pattern)  # 每一个虚拟机的数据，还需要汇总
                # print("io_perfs")
                # print(type(io_perfs))
                # print(io_perfs)

            # io_perfs = filter(lambda item: item["type"] in ALLOWED_NAMES and item["benchmark"] != "bulkload", io_perfs)

                io_perfs = filter(
                    lambda item: item["type"] in ALLOWED_NAMES, io_perfs)

                io_perfs = list(io_perfs)

                names, io_perfs_by_names = group_by(
                    "type", io_perfs)  # 分为native，qp-pt,spdk-vhost三类
                for name in names:
                    # io_perfs_by_names[name] = merge_by(
                    #     "vm_num", merge_io_perf, io_perfs_by_names[name])

                    io_perfs_by_names[name] = merge_by(
                        "vm_num", merge_io_perf, io_perfs_by_names[name])
                    io_perfs_by_names[name].sort(
                        key=lambda item: item["vm_num"])

        normalize_io_perfs_res = []
        for name in names:
                # print(name)
                # print(io_perfs_by_names["native"])
                test = normalize_io_perfs(
                    io_perfs_by_names["native"], io_perfs_by_names[name])
                normalize_io_perfs_res.extend(test)

        names, io_perfs_by_names_normalized = group_by(
                "type", normalize_io_perfs_res)  # 分为native，qp-pt,spdk-vhost三类
        # print(io_perfs_by_names_normalized)

     
        # print(names)
        # print(io_perfs_by_names)

        plot_result(res_dir, names, io_perfs_by_names_normalized,
                        "type", pattern, True)
        plot_result(res_dir, names, io_perfs_by_names,
                        "type", pattern, False)
        


            #  plot_result(sys.argv[2], names, cpu_loads_by_names, io_perfs_by_names, host_cpu_loads_by_names, "benchmark", "Benchmarks")
            # plot_result(sys.argv[2], names, norm_cpu_loads, norm_io_perfs, norm_host_cpu_loads, "benchmark", "Benchmarks")
