#!/usr/bin/python3

import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

# import xlwt

from tools import *


COLORS = {
    "HyQ": "#8F8F8F",
    "Offloading": "#D5D5D5",
    "Non-offloading": "#FFFFFF",
}


plt.rcParams.update({"font.size": 22, "font.family": "Times New Roman"})


def plot_bar(plt, items, x_key, y_key, label, offset, width, edgecolor):
    x = [item[x_key] for item in items]
    y = [item[y_key] for item in items]

    if y_key == "iops":
        off = 1000
        y = [item * 100 for item in y]
    elif y_key == "lat_avg":
        off = 100

    ticks = [i for i in range(len(items))]
    container = plt.bar(
        [i + offset for i in ticks],
        y,
        width=width,
        label=label,
        color=edgecolor,
        edgecolor="black",
        linewidth=1,
        # hatch=hatch,
        zorder=100,
    )

    plt.set_xticks(ticks)
    plt.set_xticklabels(x, fontsize=22)
    for a, b in zip([i + offset for i in ticks], y):
        plt.text(
            a,
            b + off,
            "%.2f" % float(b),
            ha="center",
            va="bottom",
            fontsize=20,
            rotation=90,
            clip_on=False,
        )


def get_tail_lat(item):
    res = []
    res.append(item["lat_p50"] / 1000)
    res.append(item["lat_p99"] / 1000)
    res.append(item["lat_p999"] / 1000)
    res.append(item["lat_p9999"] / 1000)
    return res


MARKERS = {
    "HyQ": "s",
    "Non-offloading": "D",
    "native": "o",
    "spdk-vhost": "^",
    "Vhost-1Core": "D",
    "Vhost-4Cores": "^",
    "Vhost-8Cores": "v",
    "Offloading": "o",
}

LINESTYLE = {
    "Non-offloading": "dashed",
    "HyQ": "solid",
    "SPDK-Vhost": "dotted",
    "Offloading": "dotted",
    "Vhost-1Core": "dashdot",
    "Vhost-4Cores": "dashdot",
    "Vhost-8Cores": "dashdot",
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
def plot_line(plt, items, x_key, y_key, label, edgecolor, hatch, pattern, abcd_index):
    x = [item[x_key] for item in items]
    # y = [item[y_key] for item in items]
    y = []
    for index, item in enumerate(items):
        if item["pattern"] == pattern:
            y = get_tail_lat(item)
            break
    # y=[]
    # y.append()

    x = range(1, len(y) + 1)

    x_lable = [item["pattern"] for item in items]

    plt.plot(
        x,
        y,
        # label=f"{io_perf[name_key][0]}-{io_perf[name_key][-1]}: avg {avg_lat}",
        # label=f"{io_perf[name_key][0]}: avg {avg_lat}",
        label=f"{label}",
        # color=COLORS1[io_perf["type"]][io_perf["rw"]],
        linestyle=LINESTYLE[label],
        # linestyle="dashed",
        color="black",
        # linestyle="solid",
        linewidth=1.5,
        marker=MARKERS[label],
        # marker="o",
        markersize=13,
        # markeredgecolor=COLORS1[io_perf["type"]][io_perf["rw"]],
        markerfacecolor="white",
        markeredgewidth=1.5,
    )
    plt.set_title(f"({abcd_index}){pattern}")
    plt.set_xticks(x)
    # plot.set_xticks(x)

    plt.set_xticklabels(["50", "99.0", "99.9", "99.99"], fontsize=22)


# 绘制网格
def plot_grid(plt):
    plt.grid(axis="y", color="silver", linewidth=0.7, zorder=0)


# ORDERED_NAMES = ["static", "utility", "latency", "static-driver", "utility-driver", "latency-driver", "mixed", "Non-offloading", "offload", "dummy"]
ORDERED_NAMES = [
    "Non-offloading",
    "Offloading",
    "HyQ",
]


def plot_result(title, names, io_perfs, x_key, filename):
    fig, iops = plt.subplots(nrows=1, ncols=1, figsize=(10, 4))
    fig.subplots_adjust(left=0.14, right=0.995, top=0.85, bottom=0.12)

    # 设置y轴名称
    iops.set_ylabel("OPS (Operations/second)")

    # 计算每一个条的宽度
    width = 0.75 / len(names)

    # 设置每一个条的偏移量
    offset = -((len(names) - 1) / 2.0)

    plot_set_tick(iops)

    for name in ORDERED_NAMES:
        if name in names:
            plot_bar(
                iops,
                io_perfs[name],
                x_key,
                "iops",
                name,
                offset * width,
                width,
                COLORS[name],
            )
            offset += 1.0

    iops.legend(
        loc="upper center",
        ncol=5,
        fontsize="small",
        frameon=True,
        handletextpad=0.1,
        handlelength=1,
        bbox_to_anchor=(0.51, 1.24),
        fancybox=False,
        columnspacing=1,
        edgecolor="black",
    )
    iops.yaxis.set_major_locator(MultipleLocator(15000))
    iops.set_ylim(0, 70000)

    title = title + "/" + filename
    fig.savefig(f"{title}.pdf", dpi=300)
    fig.savefig(f"{title}.png", dpi=300)


def plot_result_lat(title, names, io_perfs, x_key, filename):
    fig, iops = plt.subplots(nrows=1, ncols=1, figsize=(10, 4))
    fig.subplots_adjust(left=0.115, right=0.995, top=0.85, bottom=0.12)

    # 设置y轴名称
    iops.set_ylabel("Latency (μs)")

    # 计算每一个条的宽度
    width = 0.6 / len(names)

    # 设置每一个条的偏移量
    offset = -((len(names) - 1) / 2.0)

    plot_set_tick(iops)

    for name in ORDERED_NAMES:
        if name in names:
            plot_bar(
                iops,
                io_perfs[name],
                x_key,
                "lat_avg",
                name,
                offset * width,
                width,
                COLORS[name],
            )
            offset += 1.0

    iops.legend(
        loc="upper center",
        ncol=5,
        fontsize="small",
        frameon=True,
        handletextpad=0.1,
        handlelength=1,
        bbox_to_anchor=(0.51, 1.24),
        fancybox=False,
        columnspacing=1,
        edgecolor="black",
    )

    iops.yaxis.set_major_locator(MultipleLocator(800))
    iops.set_ylim(bottom=0, top=4800)

    title = title + "/" + filename
    fig.savefig(f"{title}.pdf", dpi=300)
    fig.savefig(f"{title}.png", dpi=300)


if __name__ == "__main__":
    res_dir = sys.argv[1]
    fig_dir = sys.argv[2]

    io_perfs = []
    for scheme in os.listdir(res_dir):
        io_perfs.extend(get_data(f"{res_dir}/{scheme}"))

    schemes, io_perfs_by_schemes = group_by("scheme", io_perfs)
    for scheme in schemes:
        io_perfs_by_schemes[scheme] = merge_by(
            "benchmark", merge_io_perf, io_perfs_by_schemes[scheme]
        )

    plot_result(fig_dir, schemes, io_perfs_by_schemes, "benchmark", "fig-16-evaluation-rocksdb-ops")

    plot_result_lat(fig_dir, schemes, io_perfs_by_schemes, "benchmark", "fig-17-evaluation-rocksdb-lat")
