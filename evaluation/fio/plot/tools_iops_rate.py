#!/usr/bin/python3

import os
import sys
import json
import math
import re
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import xlwt

plt.rcParams.update({'font.size': 22, 'font.family': 'Times New Roman'})
# plt.rcParams.update({'font.size': 22})

ORDERED_NAMES = ["Non-offloading", "Offloading","Virtio","HyQ"]


# 柱状图颜色
COLORS = {
    "host-ssd": "#404040",
    "native": "#404040",
    "native-0": "#404040",
    "HyQ": "#8F8F8F",
    "Offloading": "#D5D5D5",
     "Non-offloading": "#FFFFFF",
    "Virtio": "#BEBEBE",
}

# 柱状图内条纹类型
HATCHS = {
    # "HyQ": "/",
    # "Non-offloading": "",
    # "Virtio": "-",
    # "Offloading": "\\"
    "HyQ": "",
    "Non-offloading": "",
    "Virtio": "",
    "Offloading": ""
}


MARKERS = {
    "HyQ": "s",
    "Non-offloading": "D",
    "Offloading": "^",
    "Vhost-C1": "D",
    "Vhost-C4": "^",
    "Vhost-C8": "v",
    "Virtio": "o",
}

LINESTYLE = {
    # "rr": "-",
    # "rw": "-",
    # "sw": "-",
    # "sr": "-"
    "randread": "-",
    "randwrite": "-",
    "seqwrite": "-",
    "seqread": "-",
    "Non-offloading":"dashdot",
    "HyQ":"solid",
    "Offloading":"dotted",
    "Virtio":"dashed"
}


COLORS1 = {
    "HyQ": {
        "randread": "#FE5F05",
        "randwrite": "#FE5F05",
        "seqwrite": "#FE5F05",
        "seqread": "#FE5F05",
    },
    "native": {
        "randread": "#006FBF",
        "randwrite": "#006FBF",
        "seqwrite": "#006FBF",
        "seqread": "#006FBF",
    },
    "Virtio": {
        "randread": "#F5B201",
        "randwrite": "#F5B201",
        "seqwrite": "#F5B201",
        "seqread": "#F5B201",
    },
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
    }
}


def write_excel(title,columns,rows,data):
    book = xlwt.Workbook(encoding='utf-8',style_compression=0)

    sheet = book.add_sheet(f'{title}',cell_overwrite_ok=True)
    for index,item in enumerate(columns):
        sheet.write(0,index+1,item)
    
    for index,item in enumerate(rows):
        sheet.write(index*2+1,0,item)
    
    for index1,item1 in enumerate(data):
        for index2,item2 in enumerate(item1):
            sheet.write(index1*2+1,index2+1,float(item2))
    
    
    savepath = f'./excel/{title}.xls'
    book.save(savepath)


def filter_loads(cpu_loads, io_perfs, ALLOWED_NAMES, ALLOWED_RW, ALLOWED_QD, ALLOWED_JOBS, ALLOWED_BS, ALLOWED_CPU_NUM):
    cpu_loads_iops = filter(
        lambda item: item["scheme"] in ALLOWED_NAMES, cpu_loads)
    io_perfs_iops = filter(
        lambda item: item["scheme"] in ALLOWED_NAMES, io_perfs)

    cpu_loads_iops = filter(
        lambda item: item["rw"] in ALLOWED_RW, cpu_loads_iops)
    io_perfs_iops = filter(
        lambda item: item["rw"] in ALLOWED_RW, io_perfs_iops)

    cpu_loads_iops = filter(
        lambda item: item["iodepth"] in ALLOWED_QD, cpu_loads_iops)
    io_perfs_iops = filter(
        lambda item: item["iodepth"] in ALLOWED_QD, io_perfs_iops)

    cpu_loads_iops = filter(
        lambda item: item["numjobs"] in ALLOWED_JOBS, cpu_loads_iops)
    io_perfs_iops = filter(
        lambda item: item["numjobs"] in ALLOWED_JOBS, io_perfs_iops)

    cpu_loads_iops = filter(
        lambda item: item["blocksize"] in ALLOWED_BS, cpu_loads_iops)
    io_perfs_iops = filter(
        lambda item: item["blocksize"] in ALLOWED_BS, io_perfs_iops)

    cpu_loads_iops = filter(
        lambda item: item["cpunum"] in ALLOWED_CPU_NUM, cpu_loads_iops)
    io_perfs_iops = filter(
        lambda item: item["cpunum"] in ALLOWED_CPU_NUM, io_perfs_iops)

    cpu_loads_iops = combine_key(list(cpu_loads_iops), "filename",
                                 "scheme", "rate")
    io_perfs_iops = combine_key(list(io_perfs_iops), "filename",
                                "scheme", "rate",)
    # io_perfs_iops = combine_key(list(io_perfs_iops), "filename", "vmnum", "cycle_cnt")

    names_iops, cpu_loads_by_names_iops = group_by("scheme", cpu_loads_iops)  # 分成两大类，vmpt/VFIO
    names_iops, io_perfs_by_names_iops = group_by("scheme", io_perfs_iops)

    # for name in names_iops:
    #     print(name)
    #     # print(cpu_loads_by_names_iops[name])
    #     cpu_loads_by_names_iops[name] = merge_by(
    #         "filename", merge_cpu_load, cpu_loads_by_names_iops[name])
    #     cpu_loads_by_names_iops[name].sort(key=lambda item: item["filename"])

    for name in names_iops:
        # print(io_perfs_by_names_iops[name])
        io_perfs_by_names_iops[name] = merge_by(
            "filename", merge_io_perf, io_perfs_by_names_iops[name])
        # io_perfs_by_names_iops[name].sort(key=lambda item: item["filename"])
        #  io_perfs_by_names_iops[name].sort(
        # key=lambda item: item["blocksize"], reverse=True)
        io_perfs_by_names_iops[name].sort(
            key=lambda item: item["rate"])
    
    for name in names_iops:
        cpu_loads_by_names_iops[name] = merge_by(
            "filename", merge_cpu_load, cpu_loads_by_names_iops[name])
        cpu_loads_by_names_iops[name].sort(
            key=lambda item: item["rate"])

    return names_iops, cpu_loads_by_names_iops, io_perfs_by_names_iops


def filter_results(results, requirements):
    def check(item):
        for key, value in requirements.items():
            if item[key] not in value:
                return False
        return True

    results = filter(check, results)
    return list(results)


def cal_relative_perf(names,io_perfs_iops):
    # 计算iops、bw、lat相对值
    for name in ORDERED_NAMES:
        if name in names:
            for item in io_perfs_iops[name]:
                for base_item in io_perfs_iops["HyQ"]:
                    if base_item["casename"] in item["casename"]:
                        baseiops = base_item["iops"]
                        basebw = base_item["bandwidth"]
                        baselatency = base_item["latency"]
                        break
                normalized_iosp = round(item["iops"]/baseiops*100, 2)
                normalized_bw = round(item["bandwidth"]/basebw*100, 2)
                normalized_lat = round(item["latency"]/baselatency*100, 2)

                item["normalized_iops"] = normalized_iosp
                item["normalized_bw"] = normalized_bw
                item["normalized_latency"] = normalized_lat


def plot_set_tick(ax, top_bool):
    # if(top_bool):
    #     ax.spines['top'].set_visible(False)
    #     ax.spines['right'].set_visible(False)
    # else:
    #     ax.spines['bottom'].set_visible(False)
    #     ax.spines['right'].set_visible(False)
    # bwidth=1.7
    # ax.spines['left'].set_linewidth(bwidth)
    # ax.spines['right'].set_linewidth(bwidth)
    # ax.spines['bottom'].set_linewidth(bwidth)
    # ax.spines['top'].set_linewidth(bwidth)
    
    
    ax.tick_params("y", which='major',
                   length=7, 
                   colors="black")
    ax.tick_params("x",length=7, 
                   colors="black")


def isnumber(aString):
    try:
        float(aString)
        return True
    except:
        return False


# 预处理fio生成json文件，去除报错的信息
def prepare_file(filename):
    cnt = 0
    with open(filename, "r") as f:
        lines = f.readlines()
    with open(filename, "w") as f_w:
        for line in lines:
            if line.startswith("client"):
                continue
            if line.startswith("fio"):
                cnt = cnt+1
                continue
            f_w.write(line)
    return cnt

# 返回value所在的index




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
# def plot_bar(plt, title, items, x_key, y_key, y_percent_key, label, offset, width, edgecolor, hatch):
def plot_bar(plt,  items, x_key, y_key, label, offset, width, edgecolor, hatch, bool_top,data):
    x = [item[x_key] for item in items]
    y = [item[y_key] for item in items]
    ticks = [i for i in range(len(items))]
    data.append(y)

    # container = plt.bar([i + offset for i in ticks], y, width=width, label=label, fill=False, edgecolor=edgecolor, hatch=hatch)
    if(bool_top):
        container = plt.bar([i + offset for i in ticks], y, 
                            width=width,  color=edgecolor, label=label,edgecolor='black',linewidth=1,hatch=hatch,zorder=100)

        if(y_key == "iops"):
            for a, b in zip([i + offset for i in ticks], y):
                plt.text(a+0.005, b+30.1, '%.1f' % float(b), ha='center',
                         va='bottom', fontsize=18, rotation=90, clip_on=False)
            plt.set_ylim(bottom=0, top=2200)
            plt.set_xticks(ticks)
            plt.set_xticklabels(x, fontsize=20,color="black")
            plt.yaxis.set_major_locator(MultipleLocator(400))

        elif(y_key == "bandwidth"):
            for a, b in zip([i + offset for i in ticks], y):
                plt.text(a+0.005, b+120, '%.1f' % float(b), ha='center',
                         va='bottom', fontsize=18, rotation=90, clip_on=False)
            plt.set_ylim(bottom=0, top=8500)
            plt.set_xticks(ticks)
            plt.set_xticklabels(x, fontsize=20,color="black")
            plt.yaxis.set_major_locator(MultipleLocator(1500))
        elif(y_key == "latency"):
            for a, b in zip([i + offset for i in ticks], y):
                plt.text(a, b+2, '%.1f' % float(b), ha='center',
                         va='bottom', fontsize=20, rotation=90, clip_on=False)
            plt.set_ylim(bottom=0, top=2200)
            plt.set_xticks(ticks)
            plt.yaxis.set_major_locator(MultipleLocator(500))
            plt.set_xticklabels(x, fontsize=22)
        elif(y_key == "normalized_latency"):
            for a, b in zip([i + offset for i in ticks], y):
                plt.text(a, b+0.06, '%.1f' % float(b)+"%", ha='center',
                         va='bottom', fontsize=22, rotation=90, clip_on=False)
            # plt.set_ylim(bottom=0, top=180)
            plt.tick_params(axis='x', pad=50)
        elif(y_key == "cutil"):
            for a, b in zip([i + offset for i in ticks], y):
                plt.text(a+0.01, b+0.2, '%.1f' % float(b), ha='center',
                         va='bottom', fontsize=20, rotation=90, clip_on=False)
            # plt.set_ylim(bottom=0, top=14.5)
            # plt.tick_params(axis='x', pad=50)
            # plt.yaxis.set_major_locator(MultipleLocator(3))
            plt.set_xticks(ticks)
            plt.set_xticklabels(x, fontsize=20,color="black")
        else:
            for a, b in zip([i + offset for i in ticks], y):
                plt.text(a, b+0.06, '%.1f' % float(b)+"%", ha='center',
                         va='bottom', fontsize=22, rotation=90, clip_on=False)
            # plt.set_ylim(bottom=0, top=140)
            plt.tick_params(axis='x', pad=50)
            plt.set_xticks(ticks)
            plt.set_xticklabels(x, fontsize=25)
        # plt.tick_params(axis='y', pad=20)
        # plt.get_xaxis().set_visible(False)


    else:
        container = plt.bar([i + offset for i in ticks], y,
                            width=width, label=label, color=edgecolor)
        for a, b in zip([i + offset for i in ticks], y):
            plt.text(a, b-0.1, '%.1f' % float(b), ha='center',
                     va='top', fontsize=24, rotation=90, clip_on=False)
        plt.get_xaxis().set_visible(False)
        if(y_key == "iops"):
            plt.set_ylim(bottom=800, top=0)
        elif(y_key == "bandwidth"):
            plt.set_ylim(bottom=4000, top=0)
        # elif(y_key=="latency"):
            # plt.set_ylim(bottom=30, top=0)

    # plt.set_title(title)


def plot_table(plt, names, items, x_key, y_key, row_name, col_name):
    print("enter")
    columns = []
    rows = []
    data = []
    cnt = 0
    for name in ORDERED_NAMES:
        if name in names:
            # print(name)
            # print(items[name])
            in_list = []
            for in_item in items[name]:
                in_list.append('%.1f' % float(in_item[y_key]))
                print(in_item["rw"])
                if cnt == 0:
                    columns.append(in_item[row_name])
            data.append(in_list)
            rows.append(items[name][0][col_name])
            cnt = cnt+1
            # print(name)
            # print(data)
            

    # x = [item[x_key] for item in items]
    # y = [item[y_key] for item in items]
    # ticks = [i for i in range(len(items))]

    # # 创建画布
    # # 案例数据
    # data = [[150, 200,  50, 100,  75],
    #         [300, 125,  80,  75, 100],
    #         ]
    # # 列与行
    # columns = ('', '2', '3', '4', '5') #列坐标名
    # rows = ['2', '1'] #行坐标名

    # 作图参数
    columns = tuple(columns)

    index = np.arange(len(columns))-0.1
    bar_width = 0.4

    # 设置柱状图颜色
    colors = ['red', 'blue', 'red', 'blue']

    # print("---------------")
    # print(data)

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
        cellDict[(0, i)].set_height(0.8)
        # cellDict[(0, i)].set_width(4)
        for j in range(1, len(rows)+1):
            cellDict[(j, i)].set_height(0.4)

    # # 设置图表table中行名单元格的高度
    cellDict[(1, -1)].set_height(0.4)
    # cellDict[(2, -1)].set_height(0.4)
    # cellDict[(3, -1)].set_height(0.4)
    # cellDict[(4, -1)].set_height(0.4)

    cellDict[(1, -1)].set_width(0.1)
    # cellDict[(2, -1)].set_width(0.1)
    # cellDict[(3, -1)].set_width(0.1)
    # cellDict[(4, -1)].set_width(0.1)

    # 设置图表table单元格文本字体
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(100)

    # 设置图表table单元格边框
    for key, cell in the_table.get_celld().items():
        cell.set_linewidth(0.3)
    # 1111


# 绘制网格
def plot_grid(plt):
    plt.grid(axis="y", color="silver", linewidth=0.7,zorder=0)


# 绘图

def plot_result_iops(title, names, cpu_loads_iops, io_perfs_iops, cpu_loads_bw, io_perfs_bw, x_key, x_label, resfile):
    plt.rcParams.update({'font.size': 80})
    # 创建绘图

    fig, (normalized_iops, iops) = plt.subplots(
        nrows=2, ncols=1, figsize=(64, 48))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.95, bottom=0.05)

    plot_set_tick(normalized_iops, True)
    plot_set_tick(iops, False)

    # 设置y轴名称
    if(title == "IOPS"):
        normalized_iops.set_ylabel("Normalized IOPS(%)", fontsize=24)
        iops.set_ylabel("IOPS (K)", fontsize=24)
    elif(title == "Bandwidth"):
        normalized_iops.set_ylabel("Normalized Bandwidth(%)", fontsize=24)
        iops.set_ylabel("Bandwidth(MB/s)", fontsize=24)
        # iops.xaxis.labelpad = 10

    # 调整y轴的方向
    iops.invert_yaxis()

    # 计算每一个条的宽度
    width = 0.75 / len(names)
    # width = 0.75 / 4

    # 设置每一个条的偏移量
    offset = -((len(names) - 1) / 2.0)

    # 计算iops相对值
    cal_relative_perf(names,io_perfs_iops)
 
    for name in ORDERED_NAMES:
        if name in names:
            if(title == "IOPS"):
                plot_bar(normalized_iops, io_perfs_iops[name], x_key, "normalized_iops",
                         name, offset * width, width, COLORS[name], HATCHS[name], True)
                plot_bar(iops,  io_perfs_iops[name], x_key, "iops",
                         name, offset * width, width, COLORS[name], HATCHS[name], False)
                offset += 1.0
                iops.legend(loc="lower right")
            else:
                plot_bar(normalized_iops,  io_perfs_iops[name], x_key, "normalized_bw",
                         name, offset * width, width, COLORS[name], HATCHS[name], True)
                plot_bar(iops,  io_perfs_iops[name], x_key, "bandwidth",
                         name, offset * width, width, COLORS[name], HATCHS[name], False)
                offset += 1.0
                iops.legend()

    # iops.legend(loc="lower right")
    # normalized_iops.legend()
    res = resfile+"/"+title
    fig.savefig(f"{res}.png", dpi=300)
    fig.savefig(f"{res}.pdf", format="pdf")


def plot_result_single(title, names, cpu_loads_iops, io_perfs_iops, cpu_loads_bw, io_perfs_bw, x_key, x_label, resfile, suffix_name):
    plt.rcParams.update({'font.size': 20})
    # 创建绘图

    if(title == "cutil-iops" or title=="cutil-bw"):
        margin_left=0.09
    else:
        margin_left=0.11
    
    fig, (normalized_iops) = plt.subplots(nrows=1, ncols=1, figsize=(10, 4))
    # fig.subplots_adjust(left=0.115, right=0.995, top=0.85, bottom=0.2)
    fig.subplots_adjust(left=margin_left, right=0.995, top=0.85, bottom=0.2)


    plot_set_tick(normalized_iops, True)

    # 计算iops、bw、lat相对值
    # cal_relative_perf(names,io_perfs_iops)

    
    # 设置y轴名称
    if(title == "IOPS"):
        normalized_iops.set_ylabel("IOPS (K)", fontsize=20)
    elif(title == "Bandwidth"):
        normalized_iops.set_ylabel(
            "Bandwidth (MB/s)", fontsize=20)

    elif(title == "Latency"):
        normalized_iops.set_ylabel("Latency(μs)", fontsize=20)
    
    elif(title == "cutil-iops" or title== "cutil-bw"):
        normalized_iops.set_ylabel("Target CPU Consumption", fontsize=20)
        normalized_iops.set_ylim(bottom=0, top=7)
        normalized_iops.yaxis.set_major_locator(MultipleLocator(1))
        
        
    # if(title == "cutil-iops"):
    #     normalized_iops.set_ylim(bottom=0,top=13)
    # elif(title== "cutil-bw"):
    #     normalized_iops.set_ylim(bottom=0,top=13)

    normalized_iops.set_xlabel("I/O workload pressure (K IOPS)", fontsize=20)
    # 计算每一个条的宽度
    width = 0.6 / len(names)

    # 设置每一个条的偏移量
    offset = -((len(names) - 1) / 2.0)

    row=[]
    col=[]
    data=[]
    cnt=0
    for name in ORDERED_NAMES:
        if name in names:
            col.append(name)
            cnt=cnt+1
            if(cnt==1):
                row = [item["rw"] for item in io_perfs_iops[name]]
            if(title == "IOPS"):
                # normalized_iops.legend()
                
                plot_bar(normalized_iops, io_perfs_iops[name], x_key, "iops",   name, offset * width, width, COLORS[name], HATCHS[name], True,data)
                offset += 1.0
                # plt.legend()
            elif(title == "Bandwidth"):
                plot_bar(normalized_iops,  io_perfs_iops[name], x_key, "bandwidth",name, offset * width, width, COLORS[name], HATCHS[name], True,data)
                offset += 1.0
                
            elif(title == "Latency"):
                plot_bar(normalized_iops,  io_perfs_iops[name], x_key, "latency", name, offset * width, width, COLORS[name], HATCHS[name], True,data)
                offset += 1.0
            elif(title == "cutil-iops" or title=="cutil-bw"):
                plot_bar(normalized_iops,  cpu_loads_iops[name], x_key, "cutil",
                         name, offset * width, width, COLORS[name], HATCHS[name], True,data)
                offset += 1.0
                # normalized_iops.set_ylim(bottom=0, top=150)
    # normalized_iops.legend(ncol=4,fontsize="small",columnspacing=0.7,handletextpad=0.1,bbox_to_anchor=(0.9,1.25),edgecolor="black",borderpad=0.3)
    # write_excel(title,row,col,data)
    normalized_iops.legend(ncol=5,fontsize=19,frameon=True,handletextpad=0.1,handlelength=1,borderpad=0.3,loc="upper center",bbox_to_anchor=(0.5,1.25),edgecolor="black",shadow=False,fancybox=False)

    res = resfile+"/"+title+"_iops_rate"+suffix_name
    fig.savefig(f"{res}.png", dpi=300)
    fig.savefig(f"{res}.pdf", format="pdf")


def plot_result_single_latency(title, names, cpu_loads_iops, io_perfs_iops, cpu_loads_bw, io_perfs_bw, x_key, x_label, resfile):
    plt.rcParams.update({'font.size': 20})
    # 创建绘图

    fig, (iops) = plt.subplots(
        nrows=1, ncols=1, figsize=(10, 4))
    # fig.subplots_adjust(left=0.10, right=0.995, top=0.85, bottom=0.2)
    fig.subplots_adjust(left=0.10, right=0.995, top=0.85, bottom=0.2)
    
    
        # fig, (normalized_iops) = plt.subplots(nrows=1, ncols=1, figsize=(10, 4))
    # fig.subplots_adjust(left=0.10, right=0.995, top=0.95, bottom=0.15)

    plot_set_tick(iops, True)

    # 设置y轴名称

    iops.set_ylabel("Average Latency(μs)")
    # iops.set_xlabel("Various Test Cases")
    # plot_grid(iops)

    # 计算每一个条的宽度
    width = 0.6 / len(names)

    # 设置每一个条的偏移量
    offset = -((len(names) - 1) / 2.0)

    # 计算iops相对值
    cal_relative_perf(names,io_perfs_iops)

    row=[]
    col=[]
    data=[]
    cnt=0
    
    for name in ORDERED_NAMES:
        if name in names:
            col.append(name)
            cnt=cnt+1
            if(cnt==1):
                row = [item["rw"] for item in io_perfs_iops[name]]
            plot_bar(iops,  io_perfs_iops[name], x_key, "latency",
                         name, offset * width, width, COLORS[name], HATCHS[name], True,data)
            offset += 1.0
    write_excel(title,row,col,data)
    # 绘制网格

    # iops.legend(loc="upper center",ncol=4,fontsize='small',columnspacing=0.7,handletextpad=0.1,bbox_to_anchor=(0.55,1.25),edgecolor="black",borderpad=0.3)
    iops.legend(loc="upper center", ncol=5,fontsize=19,frameon=True,handletextpad=0.1,handlelength=1,borderpad=0.3,edgecolor="black",bbox_to_anchor=(0.5,1.27),fancybox=False)

    res = resfile+"/"+title
    fig.savefig(f"{res}.png", dpi=300)
    fig.savefig(f"{res}.pdf", format="pdf")


def plot_result_latency(title, names, cpu_loads_iops, io_perfs_iops, cpu_loads_bw, io_perfs_bw, x_key, x_label, resfile):
    plt.rcParams.update({'font.size': 80})
    # 创建绘图

    fig, (normalized_iops, iops) = plt.subplots(
        nrows=2, ncols=1, figsize=(48, 48))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.95, bottom=0.05)
    # plt.suptitle(title, fontsize=24, fontweight='bold')

    # 设置y轴名称
    normalized_iops.set_ylabel("Normalized Latency(%)", fontsize=24)
    iops.set_ylabel("Latency (μs)", fontsize=24)

    plot_set_tick(normalized_iops, True)
    plot_set_tick(iops, False)

    # 调整y轴的方向
    iops.invert_yaxis()

    # 计算每一个条的宽度
    width = 0.75 / len(names)

    # 设置每一个条的偏移量
    offset = -((len(names) - 1) / 2.0)

    for name in ORDERED_NAMES:
        if name in names:
            # print(name)
            for item in io_perfs_iops[name]:
                for base_item in io_perfs_iops["Non-offloading"]:
                    if base_item["casename"] in item["casename"]:
                        baseiops = base_item["latency"]
                        # basebw = base_item["bandwidth"]
                        break
                normalized_iosp = round(item["latency"]/baseiops*100, 2)
                # normalized_bw = round(item["bandwidth"]/basebw*100, 2)

                item["normalized_latency"] = normalized_iosp

    for name in ORDERED_NAMES:
        if name in names:
            plot_bar(normalized_iops,  io_perfs_iops[name], x_key, "normalized_latency",
                     name, offset * width, width, COLORS[name], HATCHS[name], True)
            plot_bar(iops,  io_perfs_iops[name], x_key, "latency",
                     name, offset * width, width, COLORS[name], HATCHS[name], False)
            offset += 1.0
            iops.legend()

    # 绘制网格
    # plot_grid(iops)
    # plot_grid(normalized_iops)

    res = resfile+"/"+title
    fig.savefig(f"{res}.png", dpi=300)
    fig.savefig(f"{res}.pdf", format="pdf")


def statistics(items, val_func):
    values = [val_func(item) for item in items]
    mean = sum(values) / len(values)
    std_dev = math.sqrt(
        sum([(value - mean) ** 2 for value in values]) / len(values))
    return mean, std_dev

# percentile


# plt.rcParams.update({'font.size': 84})

def filter_lat(per_list,percents,latencies):
    percents_res=[]
    latencies_res=[]
    for index, per in enumerate(percents):
        if per in per_list:
            percents_res.append(percents[index])
            latencies_res.append(latencies[index])
    return percents_res,latencies_res

def plot_cumulative_lat(rw, plot, title, name_key, io_perfs):
    
    for scheme in ORDERED_NAMES:
        for io_perf in io_perfs:
            if(io_perf["scheme"]==scheme):
                if(rw in ["randread\n128k-1-1", "seqread\n128k-1-1"]):
                    lats = io_perf["rpercentile"]
                    avg_lat = (f"{io_perf['rlatency']:.3f}")
                else:
                    lats = io_perf["wpercentile"]
                    avg_lat = (f"{io_perf['wlatency']:.3f}")
                percents_old = sorted(lats.keys(), key=lambda key: float(key))
                    # 将纳秒转换为微秒
                latencies = [lats[percent] / 1000.0 for percent in percents_old]
                    
                percents=[float(percent) for percent in percents_old]

                          
                per_list=[10.00, 30.00, 50.00, 95.00, 99.00, 99.50]
                
                
                x,y=filter_lat(per_list,percents,latencies)
                # x,y=latencies,percents
                ticks = [i for i in range(len(x))]  
                    # plot.set_xlim(right=latencies[int(len(latencies)/2)])
                    # latencies = [lats[percent] / 1000.0 for percent in percents]
                    # avg_lat=(f"{io_perf['rlatency']:.3f}")[1:]
                    
                plot.plot(
                        ticks,
                        y,
                        # label=f"{io_perf[name_key][0]}-{io_perf[name_key][-1]}: avg {avg_lat}",
                        # label=f"{io_perf[name_key][0]}: avg {avg_lat}",
                        label=f"{io_perf[name_key]}",
                        # color=COLORS1[io_perf["scheme"]][io_perf["rw"]],
                        linestyle=LINESTYLE[io_perf["scheme"]],
                        color="black", 
                        # linestyle="solid",
                        linewidth=1.5,
                        marker=MARKERS[io_perf["scheme"]],
                        markersize=13,
                        # markeredgecolor=COLORS1[io_perf["scheme"]][io_perf["rw"]],
                        markerfacecolor='white',
                        markeredgewidth=1.5,
                    )
    plot.set_xticks(ticks)
    # plot.set_xticks(x)
    
    plot.set_xticklabels([float(percent) for percent in x], fontsize=24)
    # plot.set_title(title, x=0.3, y=0.7)
    # title=title.replace('\n', '-')
    # plot.set_title(title,fontsize=24, y=-0.7)
    


    



def plt_clu(io_perfs, resfile):
    # fig, ((vm_1, vm_25), (vm_50, vm_100)) = plt.subplots(nrows=2, ncols=2, figsize=(48, 32))
    plt.rcParams.update({'font.size': 22})
    fig, (vm_1, vm_50) = plt.subplots(
        nrows=1, ncols=2, figsize=(10, 4))
    # fig.subplots_adjust(left=0.1, right=0.98, top=0.77,
                        # bottom=0.20, hspace=0.22, wspace=0.15)

    fig.subplots_adjust(left=0.1, right=0.98, top=0.85,
                        bottom=0.235, hspace=1.3, wspace=0.25)
    
    plot_set_tick(vm_1,True)
    plot_set_tick(vm_50,True)

    
    plot_grid(vm_1)
    plot_grid(vm_50)
   
    plots = {
        "randread\n128k-1-1": vm_1,
        # 25: vm_25,
        "randwrite\n128k-1-1": vm_50,
        # "seqread\n4k-1-1": vm_100,
        # "seqwrite\n4k-1-1": vm_250,
    }

    io_perfs = list(filter(lambda item: item["casename"] in [
                    "randread\n128k-1-1", "randwrite\n128k-1-1"], io_perfs))

    names_iops, io_perfs_by_names_iops = group_by("casename", io_perfs)

   
    for name in names_iops:
        
    # for name in ORDERED_NAMES:
    #     if name in names_iops:
        # print(io_perfs_by_names_iops[name])
        io_perfs_by_names_iops[name] = merge_by(
                "scheme", merge_io_perf, io_perfs_by_names_iops[name])



    
    for vm_index in names_iops:
        # rwmixreads, io_perfs_by_vmnum[vm_index] = group_by("rwmixread", io_perfs_by_vmnum[vm_index])
        # for rwmixread in rwmixreads:
        # io_perfs_by_vmnum[vm_index] = merge_by("name_rwmixread", merge_io_perf, io_perfs_by_vmnum[vm_index])
        # io_perfs_by_vmnum[vm_index].sort(key=lambda item: item["rwmixread"] + item["name"])
        plot_cumulative_lat(
            vm_index, plots[vm_index], f"{vm_index}", "scheme", io_perfs_by_names_iops[vm_index])

    vm_1.set_ylabel("Latency (μs)",fontsize=22)
    vm_1.legend(loc="lower right",fontsize="small",bbox_to_anchor=(2.05,1.0),ncol=4,edgecolor="black",fancybox=False)
    

    
    vm_1.set_title("(a) randread-128k-1-1",fontsize=28, y=-0.38)
    vm_50.set_title("(b) randwrite-128k-1-1",fontsize=28, y=-0.38)
    
    vm_1.yaxis.set_major_locator(MultipleLocator(20))
    vm_50.yaxis.set_major_locator(MultipleLocator(50))
    
    # vm_1.set_ylim(top=170)
    # vm_50.set_ylim(top=240)
    
    res = resfile+"/tail_latcncy"
    print(res)
    fig.savefig(f"{res}.png", dpi=300)
    fig.savefig(f"{res}.pdf", dpi=300)
    plt.close(fig)
