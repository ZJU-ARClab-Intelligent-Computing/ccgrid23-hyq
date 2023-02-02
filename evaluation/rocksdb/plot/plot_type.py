#!/usr/bin/python3

from pickle import TRUE
import sys
# from typing import final
import matplotlib.pyplot as plt
import time
import os

from tools_type import *
import numpy as np

# plt.rcParams.update({"hatch.linewidth": 5.0})
plt.rcParams.update({'font.size': 84, 'font.family': 'Times New Roman'})
# plt.rcParams.update({'font.size': 60, )

# 柱状图颜色
EDGE_COLORS = {
    # 区分不同的方案
    # "dummy": "crimson",
    "kernel": "#1F77B4",
    "offload": "#FF7F0E",
    "scheduler-cx5": "#9467BD",
    "scheduler-cx6": "#9467BD",
    "mixed": "purple",
    # "utility": "purple",
    "utility-driver": "blue",
    # "latency": "darkcyan",
    "latency-driver": "dodgerblue",
    # "static": "skyblue",
    "static-driver": "steelblue",
}

EDGE_COLORS = {
    "native": "#404040",
    "native-0": "#404040",
    "qp-pt": "#7F7F7F",
    "spdk-vhost": "#FFFFFF",
    "kernel": "#C0C0C0",
    "cx5-blk": "#C0C0C0",
}

HATCHS = {
    "native": "-",
    "kernel": "/",
    "qp-pt": "+",
    "spdk-vhost": "|",
    "cx5-blk": "\\"
}

def plot_table(plt, names, items, x_key, y_key, row_name, col_name):
    print("enter")
    columns = []  # 列坐标名
    rows = []  # 行坐标名
    data = []
    cnt = 0
    for name in ORDERED_NAMES:
        if name in names:
            # print(name)
            # print(items[name])
            in_list = []
            for in_item in items[name]:
                in_list.append('%.1f' % float(in_item[y_key]))
                if cnt == 0:
                    columns.append(in_item[row_name])
            data.append(in_list)
            rows.append(items[name][0][col_name])
            cnt = cnt+1

    # x = [item[x_key] for item in items]
    # y = [item[y_key] for item in items]
    # ticks = [i for i in range(len(items))]

    # # 创建画布
    # # 案例数据
    # data = [[150, 200,  50, 100,  75],
    #         [300, 125,  80,  75, 100],
    #         ]
    # # 列与行
    # columns = ('', '2', '3', '4', '5')
    # rows = ['2', '1'] #行坐标名

    # 作图参数
    columns = tuple(columns)

    index = np.arange(len(columns))-0.1
    bar_width = 0.4

    # 设置柱状图颜色
    colors = ['red', 'blue', 'red', 'blue']

    the_table = plt.table(cellText=data,
                          rowLabels=rows,
                          rowLoc='center',
                          # rowColours=colors,
                          colLabels=columns,
                          cellLoc='center',
                          loc="bottom",
                          # cellColours={'r','b'},
                          bbox=[0, -0.46, 1, 0.46]  # x，上下高度，缩放比例，上下比例
                          )

    # 设置单元格高度
    cellDict = the_table.get_celld()
    for i in range(0, len(columns)):
        cellDict[(0, i)].set_height(0.4)
        # cellDict[(0, i)].set_width(4)
        for j in range(1, len(rows)+1):
            cellDict[(j, i)].set_height(0.4)

    # # 设置图表table中行名单元格的高度
    cellDict[(1, -1)].set_height(0.4)
    cellDict[(2, -1)].set_height(0.4)
    cellDict[(3, -1)].set_height(0.4)
    cellDict[(4, -1)].set_height(0.4)

    cellDict[(1, -1)].set_width(0.15)
    cellDict[(2, -1)].set_width(0.15)
    cellDict[(3, -1)].set_width(0.15)
    cellDict[(4, -1)].set_width(0.15)

    # 设置图表table单元格文本字体
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(100)

    # 设置图表table单元格边框
    for key, cell in the_table.get_celld().items():
        cell.set_linewidth(0.3)
    # 1111


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
    x_lable = [item["pattern"] for item in items]
    ticks = [i for i in range(len(items))]
    container = plt.bar([i + offset for i in ticks], y, width=width,
                        label=label, color=edgecolor, edgecolor="black", linewidth=3,hatch=hatch)

    # plt.set_xticks(ticks)
    # plt.set_xticklabels(x_lable)
    
    plt.get_xaxis().set_visible(False)
    # if bar_label:
    #     plt.bar_label(container, labels=["%.4f" % y[0], ""], padding=20, rotation=-90)

    for a, b in zip([i + offset for i in ticks], y):
        plt.text(a, b+0.06, '%.1f' % float(b), ha='center',
                 va='bottom', fontsize=80, rotation=90, clip_on=False)
       
# 绘制网格
def plot_grid(plt):
    plt.grid(axis="y", color="silver", linewidth=0.7)


# ORDERED_NAMES = ["static", "utility", "latency", "static-driver", "utility-driver", "latency-driver", "mixed", "kernel", "offload", "dummy"]
ORDERED_NAMES = ["native", "qp-pt", "kernel", "spdk-vhost","cx5-blk"]


def plot_result(title, names,  io_perfs,io_perfs_normalized , x_key, filename, bool_normalized):

  

    fig, (iops) = plt.subplots(nrows=1, ncols=1, figsize=(48, 36))
    fig.subplots_adjust(left=0.16, right=0.97, top=0.95, bottom=0.35)


    # 设置x轴名称
    # iops.set_xlabel("benchmark type")

    # 设置y轴名称
    iops.set_ylabel("Normalied Throughput(%)")

    # 计算每一个条的宽度
    width = 0.6 / len(names)

    # 设置每一个条的偏移量
    offset = -((len(names) - 1) / 2.0)

    plot_set_tick(iops, True)

    for name in ORDERED_NAMES:
        if name in names:
            plot_bar(iops, io_perfs_normalized[name], x_key, "iops", name,
                     offset * width, width, EDGE_COLORS[name], HATCHS[name])
            # plot_bar(iops, "IOPS", io_perfs[name], x_key, "iops", name, offset * width, width, EDGE_COLORS[name], HATCHS[name])
            # plot_bar(bw, "Bandwidth", io_perfs[name], x_key, "bandwidth", name, offset * width, width, EDGE_COLORS[name], HATCHS[name])

            offset += 1.0

    iops.legend(loc="upper center",ncol=4)

    plot_table(iops, names, io_perfs,
                   x_key, "iops", "pattern", "type")
    # plt1.legend(loc="upper right",ncol=4,columnspacing=0.3,labelspacing=0.5,markerscale=0.01,handletextpad=0.3)

    # 绘制网格
    # plot_grid(iops)
    if (bool_normalized):
        title = title+ "/"+ filename + "_normalized"
        iops.set_ylim(bottom=0, top=130)
    else:
        title = title + filename

    print(title)

    fig.savefig(f"{title}.pdf", dpi=300)
    fig.savefig(f"{title}.png", dpi=300)


thread_num=32
ALLOWED_NAMES = {"native", "qp-pt", "spdk-vhost", "kernel","cx5-blk"}
ALLOWED_THREADS = {thread_num}


if __name__ == "__main__":
    # nowdate=time.strftime("%Y%m%d%H%M%S", time.localtime())
    # nowdate = "20220913163122"
    # res_dir = "/home/jinzhen/backup/dragonball/plot_rocksdb/result/"+nowdate
    # res_dir = "./fio_res/"+nowdate
    # os.makedirs(res_dir)
    
    io_dir=sys.argv[1]
    res_dir=sys.argv[2]
    
    
    # ,"mergerandom"

    pattern_list = ["readrandom", "overwrite", "readwhilewriting"]

    io_perfs = []
    for pattern in pattern_list:
        # io_dir = "/home/jinzhen/backup/binary/rocksdb_results/"
        type_list = os.listdir(io_dir)

        for type in type_list:  # native,qp-pt,spdk-vhost
            type_dir = io_dir + "/"+type
        
            # date_list = os.listdir(type_dir)
            # data_dir = type_dir + '/'+date_list[-1]
            
            date_list = os.listdir(type_dir)
            data_dir = type_dir
            
            print("data_dir:",data_dir)
            
            # print("data_dir",data_dir)
            # /home/jinzhen/backup/binary/rocksdb_results/qp-pt/20220725131811/10"
            vm_list = os.listdir(data_dir)
            # io_perfs = io_perfs.extend(get_data(data_dir)) # 每一个虚拟机的数据，还需要汇总
            io_perfs = get_data(io_perfs, data_dir,
                                pattern)  # 每一个虚拟机的数据，还需要汇总


            # io_perfs = filter(lambda item: item["type"] in ALLOWED_NAMES and item["benchmark"] != "bulkload", io_perfs)


    io_perfs = filter(lambda item: item["type"] in ALLOWED_NAMES, io_perfs)
    io_perfs = filter(lambda item: item["vm_num"] in ALLOWED_THREADS, io_perfs)

    io_perfs = list(io_perfs)

    names, io_perfs_by_names = group_by(
        "type", io_perfs)  # 分为native，qp-pt,spdk-vhost三类
    print("---------mhh")
    print(io_perfs_by_names)
    for name in names:
        # io_perfs_by_names[name] = merge_by(
        #     "vm_num", merge_io_perf, io_perfs_by_names[name])

        # io_perfs_by_names[name] = merge_by(
            # "vm_num", merge_io_perf, io_perfs_by_names[name])
        io_perfs_by_names[name] = merge_by(
            "pattern", merge_io_perf, io_perfs_by_names[name])
        # io_perfs_by_names[name].sort(
        #     key=lambda item: item["vm_num"])

    normalize_io_perfs_res = []
    for name in names:
        # print(name)
        # print(io_perfs_by_names["native"])


        test = normalize_io_perfs(
            io_perfs_by_names["native"], io_perfs_by_names[name])
        print("--------test")
        print(test)
        normalize_io_perfs_res.extend(test)

    names, io_perfs_by_names_normalized = group_by(
        "type", normalize_io_perfs_res)  # 分为native，qp-pt,spdk-vhost三类
    print("-----------jzzzz")
    print(io_perfs_by_names_normalized)
    # print(names)
    # print(io_perfs_by_names)

    plot_result(res_dir, names, io_perfs_by_names,io_perfs_by_names_normalized,
                "pattern", str(thread_num), True)

    # plot_result(res_dir, names, io_perfs_by_names,io_perfs_by_names_normalized,
    #             "pattern", str(thread_num), False)

    #  plot_result(sys.argv[2], names, cpu_loads_by_names, io_perfs_by_names, host_cpu_loads_by_names, "benchmark", "Benchmarks")
    # plot_result(sys.argv[2], names, norm_cpu_loads, norm_io_perfs, norm_host_cpu_loads, "benchmark", "Benchmarks")
