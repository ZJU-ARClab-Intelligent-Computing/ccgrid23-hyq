#!/usr/bin/python3

from pickle import TRUE
import sys
# from typing import final
import matplotlib.pyplot as plt
import time
import os

from tools_mul import *
import numpy as np
import xlwt

# plt.rcParams.update({"hatch.linewidth": 5.0})
plt.rcParams.update({'font.size': 22, 'font.family': 'Times New Roman'})
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
# plt.rcParams.update({'font.size': 60, )



EDGE_COLORS = {

    "HyQ": "#8F8F8F",
    "Offloading": "#D5D5D5",
    "Non-offloading": "#FFFFFF",
}

HATCHS = {
    # "HyQ": "/",
    # "Non-offloading": "|||",
    # "spdk-vhost": '+',
    # "Vhost-1Core": '',
    # "Vhost-4Cores": '--',
    # "Vhost-8Cores": '...',
    # "Offloading": "\\",
    "HyQ": "",
    "Non-offloading": "",
    "spdk-vhost": '',
    "Vhost-1Core": '',
    "Vhost-4Cores": '',
    "Vhost-8Cores": '',
    "Offloading": "",
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
    
    
    savepath = f'./rocksdb_excel/{title}.xls'
    book.save(savepath)


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
def plot_bar(plt, items, x_key, y_key, label, offset, width, edgecolor, hatch, data):
    x = [item[x_key] for item in items]
    y = [item[y_key] for item in items]
    data.append(y)
    
    print(edgecolor)
    
    # if(y_key=="iops"):
    #     off=5
    # elif(y_key=="lat_avg"):
    #     off=0.1

    if(y_key=="iops"):
            off=1000
            y = [item*100 for item in y]
    elif(y_key=="lat_avg"):
        off=100
        
    x_lable = [item["pattern"] for item in items]
    ticks = [i for i in range(len(items))]
    container = plt.bar([i + offset for i in ticks], y, width=width,
                        label=label, color=edgecolor, edgecolor="black", linewidth=1,hatch=hatch,zorder=100)

    plt.set_xticks(ticks)
    plt.set_xticklabels(x,fontsize=22)
    for a, b in zip([i + offset for i in ticks], y):
        plt.text(a, b+off, '%.2f' % float(b), ha='center',
                 va='bottom', fontsize=20, rotation=90, clip_on=False)
        

def get_tail_lat(item):
    res=[]
    res.append(item['lat_p50']/1000)
    res.append(item['lat_p99']/1000)
    res.append(item['lat_p999']/1000)
    res.append(item['lat_p9999']/1000)
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
    "Non-offloading":"dashed",
    "HyQ":"solid",
    "SPDK-Vhost":"dotted",
    "Offloading":"dotted",
    "Vhost-1Core":"dashdot",
    "Vhost-4Cores":"dashdot",
    "Vhost-8Cores":"dashdot"
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
def plot_line(plt, items, x_key, y_key, label, edgecolor, hatch,pattern,abcd_index):
    x = [item[x_key] for item in items]
    # y = [item[y_key] for item in items]
    y=[]
    for index, item in enumerate(items):
        if(item["pattern"]==pattern):
            y=get_tail_lat(item)
            break
    # y=[]
    # y.append()
    
    x=range(1,len(y)+1)
    
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
                markerfacecolor='white',
                markeredgewidth=1.5,
            )
    plt.set_title(f"({abcd_index}){pattern}")
    plt.set_xticks(x)
    # plot.set_xticks(x)
    
    plt.set_xticklabels(["50","99.0","99.9","99.99"], fontsize=22)



# 绘制网格
def plot_grid(plt):
    plt.grid(axis="y", color="silver", linewidth=0.7,zorder=0)


# ORDERED_NAMES = ["static", "utility", "latency", "static-driver", "utility-driver", "latency-driver", "mixed", "Non-offloading", "offload", "dummy"]
ORDERED_NAMES = [ "Non-offloading", "Offloading","HyQ", ]


def plot_result(title, names,  io_perfs,io_perfs_normalized , x_key, filename, bool_normalized):
    fig, (iops) = plt.subplots(nrows=1, ncols=1, figsize=(10, 4))
    fig.subplots_adjust(left=0.14, right=0.995, top=0.85, bottom=0.12)


    # 设置x轴名称
    # iops.set_xlabel("benchmark type")

    # 设置y轴名称
    iops.set_ylabel("OPS(Operations/second)")

    # 计算每一个条的宽度
    width = 0.75 / len(names)

    # 设置每一个条的偏移量
    offset = -((len(names) - 1) / 2.0)

    plot_set_tick(iops, True)
    row=[]
    col=[]
    data=[]
    cnt=0
    for name in ORDERED_NAMES:
        if name in names:
            col.append(name)
            cnt=cnt+1
            if(cnt==1):
                row = [item["pattern"] for item in io_perfs[name]]
            plot_bar(iops, io_perfs[name], x_key, "iops", name,
                     offset * width, width, EDGE_COLORS[name], HATCHS[name],data)
            offset += 1.0
            
    write_excel("mul_ops",row,col,data)
    
    # iops.legend(loc="upper right",ncol=2,fontsize="small",columnspacing=0.6,handletextpad=0.1)
    iops.legend(loc="upper center", ncol=5,fontsize='small',frameon=True,handletextpad=0.1,handlelength=1,bbox_to_anchor=(0.51,1.24),fancybox=False,columnspacing=1,edgecolor="black")
    iops.yaxis.set_major_locator(MultipleLocator(15000))

    iops.set_ylim(0,70000)

    # plt1.legend(loc="upper right",ncol=4,columnspacing=0.3,labelspacing=0.5,markerscale=0.01,handletextpad=0.3)

    # 绘制网格
    # plot_grid(iops)
    if (bool_normalized):
        title = title+ "/"+ filename + "_normalized"
        iops.set_ylim(bottom=0, top=130)
    else:
        title = title + "/"+filename

    print(title)

    fig.savefig(f"{title}_iops.pdf", dpi=300)
    fig.savefig(f"{title}_iops.png", dpi=300)


def plot_result_lat(title, names,  io_perfs,io_perfs_normalized , x_key, filename, bool_normalized):
    fig, (iops) = plt.subplots(nrows=1, ncols=1, figsize=(10, 4))
    fig.subplots_adjust(left=0.115, right=0.995, top=0.85, bottom=0.12)


    # 设置x轴名称
    # iops.set_xlabel("benchmark type")

    # 设置y轴名称
    iops.set_ylabel("Latency(μs)")

    # 计算每一个条的宽度
    width = 0.6 / len(names)

    # 设置每一个条的偏移量
    offset = -((len(names) - 1) / 2.0)

    plot_set_tick(iops, True)
    row=[]
    col=[]
    data=[]
    cnt=0

    for name in ORDERED_NAMES:
        if name in names:
            col.append(name)
            cnt=cnt+1
            if(cnt==1):
                row = [item["pattern"] for item in io_perfs[name]]
            plot_bar(iops, io_perfs[name], x_key, "lat_avg", name,
                     offset * width, width, EDGE_COLORS[name], HATCHS[name],data)
            offset += 1.0
    write_excel("mul_lat",row,col,data)

    iops.legend(loc="upper center", ncol=5,fontsize='small',frameon=True,handletextpad=0.1,handlelength=1,bbox_to_anchor=(0.51,1.24),fancybox=False,columnspacing=1,edgecolor="black")
    
    iops.yaxis.set_major_locator(MultipleLocator(800))
    iops.set_ylim(bottom=0, top=4800)

    # 绘制网格
    # plot_grid(iops)
    if (bool_normalized):
        title = title+ "/"+ filename + "_normalized"
        iops.set_ylim(bottom=0, top=130)
    else:
        title = title + "/"+filename

    print(title)

    fig.savefig(f"{title}_lat.pdf", dpi=300)
    fig.savefig(f"{title}_lat.png", dpi=300)
    
def plot_result_tail_lat(title, names,  io_perfs,io_perfs_normalized , x_key, filename, bool_normalized,pattern_list):
    fig, ((vm_1, vm_2),(vm_3, vm_4)) = plt.subplots(
        nrows=2, ncols=2, figsize=(10, 8))
    # fig, (vm_1, vm_50) = plt.subplots(nrows=1, ncols=2, figsize=(48, 32))
    fig.subplots_adjust(left=0.1, right=0.98, top=0.92,
                        bottom=0.11, hspace=0.38, wspace=0.2)


    # 设置y轴名称
    vm_1.set_ylabel("Latency(msec)")
    vm_3.set_ylabel("Latency(msec)")  
    
    plots = {
        "readrandom": vm_1,
        "readwhilewriting": vm_2,
        "overwrite":vm_3,
        "mergerandom":vm_4
    }
    
    abcd_index = {
        "readrandom": "a",
        "overwrite": "b",
        "readwhilewriting":"c",
        "mergerandom":"d"
    }

    plot_set_tick(vm_1, True)
    plot_set_tick(vm_2, True)
    plot_set_tick(vm_3, True)
    plot_set_tick(vm_4, True)

    for pattern in pattern_list:
        for name in ORDERED_NAMES:
            if name in names:
                plot_line(plots[pattern], io_perfs[name], x_key, "iops", name,
                    EDGE_COLORS[name], HATCHS[name],pattern,abcd_index[pattern])


    vm_1.legend(fontsize="small",bbox_to_anchor=(2.17,1.2),borderaxespad = 0.,ncol=5,columnspacing=0.6,handlelength=1.5,handletextpad=0.1,fancybox=False,edgecolor="black",)

    vm_1.set_title("(a) 100 Guests",y=-0.3,fontsize=26)
    vm_2.set_title("(b) 200 Guests",y=-0.3,fontsize=26)
    vm_3.set_title("(c) 300 Guests",y=-0.3,fontsize=26)
    vm_4.set_title("(c) 400 Guests",y=-0.3,fontsize=26)
        
    vm_1.yaxis.set_major_locator(MultipleLocator(3))
    vm_2.yaxis.set_major_locator(MultipleLocator(3))
    vm_3.yaxis.set_major_locator(MultipleLocator(3))
    vm_4.yaxis.set_major_locator(MultipleLocator(3))

    # 绘制网格
    plot_grid(vm_1)
    plot_grid(vm_2)
    plot_grid(vm_3)
    plot_grid(vm_4)
    if (bool_normalized):
        title = title+ "/"+ filename + "_normalized"
        vm_1.set_ylim(bottom=0, top=130)
    else:
        title = title + "/"+filename

    print(title)

    fig.savefig(f"{title}_tail_lat.pdf", dpi=300)
    fig.savefig(f"{title}_tail_lat.png", dpi=300)


thread_num=64
ALLOWED_NAMES = { "Non-offloading","HyQ","SPDK-Vhost", "Offloading","Vhost-1Core","Vhost-4Cores","Vhost-8Cores"}
#  "SPDK-Vhost", "Offloading",
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

    pattern_list = ["readrandom","readwhilewriting","overwrite","mergerandom"]

    io_perfs = []
    for pattern in pattern_list:
        # io_dir = "/home/jinzhen/backup/binary/rocksdb_results/"
        type_list = os.listdir(io_dir)

        for type in type_list:  # native,HyQ,SPDK-Vhost
            type_dir = io_dir + "/"+type
        
            # date_list = os.listdir(type_dir)
            # data_dir = type_dir + '/'+date_list[-1]
            
            date_list = os.listdir(type_dir)
            data_dir = type_dir
            
            # print("data_dir:",data_dir)
            
            # print("data_dir",data_dir)
            # /home/jinzhen/backup/binary/rocksdb_results/HyQ/20220725131811/10"
            vm_list = os.listdir(data_dir)
            # io_perfs = io_perfs.extend(get_data(data_dir)) # 每一个虚拟机的数据，还需要汇总
            io_perfs = get_data(io_perfs, data_dir,
                                pattern)  # 每一个虚拟机的数据，还需要汇总


            # io_perfs = filter(lambda item: item["type"] in ALLOWED_NAMES and item["benchmark"] != "bulkload", io_perfs)


    io_perfs = filter(lambda item: item["type"] in ALLOWED_NAMES, io_perfs)
    io_perfs = filter(lambda item: item["qd"] in ALLOWED_THREADS, io_perfs)

    io_perfs = list(io_perfs)
    print(io_perfs)

    names, io_perfs_by_names = group_by(
        "type", io_perfs)  # 分为native，HyQ,SPDK-Vhost三类
    # print(io_perfs_by_names)
    for name in names:
        print(name)
        io_perfs_by_names[name] = merge_by(
            "pattern", merge_io_perf, io_perfs_by_names[name])
        
    print(io_perfs_by_names)
    normalize_io_perfs_res = []
    for name in names:
        test = normalize_io_perfs(
            io_perfs_by_names["Non-offloading"], io_perfs_by_names[name])
        normalize_io_perfs_res.extend(test)

    names, io_perfs_by_names_normalized = group_by(
        "type", normalize_io_perfs_res)  # 分为native，HyQ,SPDK-Vhost三类

    # print(names)
    # print(io_perfs_by_names)

    plot_result(res_dir, names, io_perfs_by_names,io_perfs_by_names_normalized,
                "pattern", str(thread_num), False)
    
    plot_result_lat(res_dir, names, io_perfs_by_names,io_perfs_by_names_normalized,
                "pattern", str(thread_num), False)
    
    plot_result_tail_lat(res_dir, names, io_perfs_by_names,io_perfs_by_names_normalized,
                "pattern", str(thread_num), False,pattern_list)

