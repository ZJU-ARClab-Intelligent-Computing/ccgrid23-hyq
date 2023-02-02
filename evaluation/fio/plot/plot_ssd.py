#!/usr/bin/python3

import json
import os
import re
import sys

from tools_ssd import *


SCHEME_NAME = {"kernel": "Non-offloading", "cx5": "Offloading", "hypath": "HyQ"}


# 解析一个fio生成的IO性能报告文件
# 输入：文件路径
# 输出：rbw, riops, rlatency,wbw, wiops, wlatency
def parse_fio_perf_file(filename):
    print(f"Parsing io perf: {filename}")
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
    print(f"Parsing cpu util: {filename}")
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
            bs,
            ba,
            numjobs,
            iodepth,
            rate,
            _,
            cpunum,
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
                "scheme": SCHEME_NAME[scheme],
                "rw": "randrw-50%" if rw == "randrw" else rw,
                "blockalign": ba,
                "blocksize": bs,
                "iodepth": int(iodepth),
                "numjobs": int(numjobs),
                "cycle_cnt": int(cycle_cnt),
                "rate": int(rate) * 16 / 1000,
                "cpunum": int(cpunum) * 2,
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
            bs,
            ba,
            numjobs,
            iodepth,
            rate,
            _,
            cpunum,
            cycle_cnt,
        ] = basename.split("_")

        us, sy, id, cutil = parse_cpu_load_file(f"{cpu_path}/{filename}")

        cpu_loads.append(
            {
                "scheme": SCHEME_NAME[scheme],
                "rw": "randrw-50%" if rw == "randrw" else rw,
                "blockalign": ba,
                "blocksize": bs,
                "iodepth": int(iodepth),
                "numjobs": int(numjobs),
                "cycle_cnt": int(cycle_cnt),
                "rate": int(rate) * 16 / 1000,
                "cpunum": int(cpunum) * 2,
                "us": us,
                "sy": sy,
                "id": id,
                "cutil": cutil,
                "casename": rw + "\n" + bs + "-" + numjobs + "-" + iodepth,
            }
        )
    return cpu_loads

    
def plot_iops_with_complex(cpu_loads, fio_perfs, fig_path, postfix):
    
    fig, (bw, cutil) = plt.subplots(
        nrows=1, ncols=2, figsize=(10, 4.5))
    fig.subplots_adjust(left=0.12, right=0.97, top=0.85, bottom=0.2,hspace=0.15, wspace=0.30)
    
    
    iops_requirements = {"blocksize": {"128k"}, "cpunum": {96},"numjobs":{8},"iodepth":{64},"rw":{"randread"},"blockalign":{"4k","128k"}}
    fio_perfs_iops = filter_results(fio_perfs, iops_requirements)
    cpu_loads_iops = filter_results(cpu_loads, iops_requirements)

    # fio_perfs_iops = combine_key(fio_perfs_iops, "scheme_rate", "scheme", "rate")
    # cpu_loads_iops = combine_key(cpu_loads_iops, "scheme_rate", "scheme", "rate")

    schemes_iops, fio_perfs_iops_by_schemes = group_by("scheme", fio_perfs_iops)
    schemes_iops, cpu_loads_iops_by_schemes = group_by("scheme", cpu_loads_iops)

    for scheme in schemes_iops:
        fio_perfs_iops_by_schemes[scheme].sort(key=lambda item: item["blockalign"],reverse=True)
        cpu_loads_iops_by_schemes[scheme].sort(key=lambda item: item["blockalign"],reverse=True)

    
    
    plot_result_single(
        "Bandwidth",
        schemes_iops,
        cpu_loads_iops_by_schemes,
        fio_perfs_iops_by_schemes,
        None,
        None,
        "blockalign",
        "I/O block alignment",
        fig_path,
        bw
    )
    # bw.legend(loc="upper center",ncol=5,fontsize=19,frameon=True,handletextpad=0.1,handlelength=1,borderpad=0.3,edgecolor="black",shadow=False,fancybox=False,columnspacing=0.8,bbox_to_anchor=(0.5,1.27))

    plot_result_single(
        "cutil-bw",
        schemes_iops,
        cpu_loads_iops_by_schemes,
        fio_perfs_iops_by_schemes,
        None,
        None,
        "blockalign",
        "I/O block alignment",
        fig_path,
        cutil
    )
    cutil.legend(loc="upper center",ncol=5,fontsize=19,frameon=True,handletextpad=0.1,handlelength=1,borderpad=0.3,edgecolor="black",shadow=False,fancybox=False,columnspacing=0.8,bbox_to_anchor=(-0.25,1.27))

    res = fig_path+"/ssd"+postfix
    fig.savefig(f"{res}.png", dpi=300)
    fig.savefig(f"{res}.pdf", format="pdf")
    plt.close()

    fig, (lat1, lat2) = plt.subplots(
        nrows=1, ncols=2, figsize=(10, 4.5))
    fig.subplots_adjust(left=0.10, right=0.97, top=0.85, bottom=0.18,hspace=0.15, wspace=0.30)

    # ---------lat1-------------
    iops_requirements = {"blocksize": {"128k"}, "cpunum": {96},"numjobs":{1},"iodepth":{1},"rw":{"randread"},"blockalign":{"4k"}}
    fio_perfs_iops = filter_results(fio_perfs, iops_requirements)
    cpu_loads_iops = filter_results(cpu_loads, iops_requirements)

    # fio_perfs_iops = combine_key(fio_perfs_iops, "scheme_rate", "scheme", "rate")
    # cpu_loads_iops = combine_key(cpu_loads_iops, "scheme_rate", "scheme", "rate")

    schemes_iops, fio_perfs_iops_by_schemes = group_by("scheme", fio_perfs_iops)
    schemes_iops, cpu_loads_iops_by_schemes = group_by("scheme", cpu_loads_iops)

    for scheme in schemes_iops:
        fio_perfs_iops_by_schemes[scheme].sort(key=lambda item: item["iodepth"])
        cpu_loads_iops_by_schemes[scheme].sort(key=lambda item: item["iodepth"])

    for scheme in schemes_iops:
        plot_cumulative_lat(
            scheme, lat1, f"{scheme}", "scheme", fio_perfs_iops_by_schemes[scheme])
    handles, labels = lat1.get_legend_handles_labels()
    labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: (1 if "Non-offloading" in t[0] else (2 if "Offloading" in t[0] else 3))))
    # lat1.legend(handles=handles,labels=labels,loc="upper center",ncol=5,fontsize=19,frameon=True,handletextpad=0.1,handlelength=1,borderpad=0.3,edgecolor="black",shadow=False,fancybox=False,columnspacing=0.8,bbox_to_anchor=(0.5,1.27))
    
    lat1.set_xlabel("Latency percentile (%) - 4k aligned")
    lat1.set_ylabel("Latency (μs)")
    # lat1.set_ylim( top=600)
    # lat1.yaxis.set_major_locator(MultipleLocator(75))
    
      
    # ---------lat2-------------
    iops_requirements = {"blocksize": {"128k"}, "cpunum": {96},"numjobs":{1},"iodepth":{1},"rw":{"randread"},"blockalign":{"128k"}}
    fio_perfs_iops = filter_results(fio_perfs, iops_requirements)
    cpu_loads_iops = filter_results(cpu_loads, iops_requirements)

    # fio_perfs_iops = combine_key(fio_perfs_iops, "scheme_rate", "scheme", "rate")
    # cpu_loads_iops = combine_key(cpu_loads_iops, "scheme_rate", "scheme", "rate")

    schemes_iops, fio_perfs_iops_by_schemes = group_by("scheme", fio_perfs_iops)
    schemes_iops, cpu_loads_iops_by_schemes = group_by("scheme", cpu_loads_iops)

    for scheme in schemes_iops:
        fio_perfs_iops_by_schemes[scheme].sort(key=lambda item: item["iodepth"])
        cpu_loads_iops_by_schemes[scheme].sort(key=lambda item: item["iodepth"])

    for scheme in schemes_iops:
        plot_cumulative_lat(
            scheme, lat2, f"{scheme}", "scheme", fio_perfs_iops_by_schemes[scheme])
    handles, labels = lat1.get_legend_handles_labels()
    labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: (1 if "Non-offloading" in t[0] else (2 if "Offloading" in t[0] else 3))))
    lat2.legend(handles=handles,labels=labels,loc="upper center",ncol=5,fontsize=19,frameon=True,handletextpad=0.1,handlelength=1,borderpad=0.3,edgecolor="black",shadow=False,fancybox=False,columnspacing=0.8,bbox_to_anchor=(-0.25,1.27))
    
    lat2.set_xlabel("Latency percentile (%) - 128k aligned")
    lat2.set_ylabel("Latency (μs)")
    # lat2.set_ylim(top=1300)
    # lat2.yaxis.set_major_locator(MultipleLocator(250))

    
    res = fig_path+"/ssd_lat"+postfix
    fig.savefig(f"{res}.png", dpi=300)
    fig.savefig(f"{res}.pdf", format="pdf")


def plot_iops_with_complex_without_HyQ(cpu_loads, fio_perfs, fig_path, postfix):
    
    fig, (bw,lat1,lat2) = plt.subplots(
        nrows=1, ncols=3, figsize=(18, 4))
    fig.subplots_adjust(left=0.07, right=0.97, top=0.85, bottom=0.18,hspace=0.15, wspace=0.25)
    
    
    iops_requirements = {"blocksize": {"128k"}, "cpunum": {96},"numjobs":{8},"iodepth":{64},"rw":{"randread"},"blockalign":{"4k","128k"}}
    fio_perfs_iops = filter_results(fio_perfs, iops_requirements)
    cpu_loads_iops = filter_results(cpu_loads, iops_requirements)

    # fio_perfs_iops = combine_key(fio_perfs_iops, "scheme_rate", "scheme", "rate")
    # cpu_loads_iops = combine_key(cpu_loads_iops, "scheme_rate", "scheme", "rate")

    schemes_iops, fio_perfs_iops_by_schemes = group_by("scheme", fio_perfs_iops)
    schemes_iops, cpu_loads_iops_by_schemes = group_by("scheme", cpu_loads_iops)

    for scheme in schemes_iops:
        fio_perfs_iops_by_schemes[scheme].sort(key=lambda item: item["blockalign"],reverse=True)
        cpu_loads_iops_by_schemes[scheme].sort(key=lambda item: item["blockalign"],reverse=True)

    
    
    plot_result_single(
        "Bandwidth",
        schemes_iops,
        cpu_loads_iops_by_schemes,
        fio_perfs_iops_by_schemes,
        None,
        None,
        "blockalign",
        "I/O block alignment",
        fig_path,
        bw
    )
    bw.legend(loc="upper center",ncol=5,fontsize=19,frameon=True,handletextpad=0.1,handlelength=1,borderpad=0.3,edgecolor="black",shadow=False,fancybox=False,columnspacing=0.8,bbox_to_anchor=(0.5,1.27))
    
    # ---------lat1-------------
    iops_requirements = {"blocksize": {"128k"}, "cpunum": {96},"numjobs":{1},"iodepth":{1},"rw":{"randread"},"blockalign":{"4k"}}
    fio_perfs_iops = filter_results(fio_perfs, iops_requirements)
    cpu_loads_iops = filter_results(cpu_loads, iops_requirements)

    # fio_perfs_iops = combine_key(fio_perfs_iops, "scheme_rate", "scheme", "rate")
    # cpu_loads_iops = combine_key(cpu_loads_iops, "scheme_rate", "scheme", "rate")

    schemes_iops, fio_perfs_iops_by_schemes = group_by("scheme", fio_perfs_iops)
    schemes_iops, cpu_loads_iops_by_schemes = group_by("scheme", cpu_loads_iops)

    for scheme in schemes_iops:
        fio_perfs_iops_by_schemes[scheme].sort(key=lambda item: item["iodepth"])
        cpu_loads_iops_by_schemes[scheme].sort(key=lambda item: item["iodepth"])

    for scheme in schemes_iops:
        plot_cumulative_lat(
            scheme, lat1, f"{scheme}", "scheme", fio_perfs_iops_by_schemes[scheme])
    handles, labels = lat1.get_legend_handles_labels()
    labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: (1 if "Non-offloading" in t[0] else (2 if "Offloading" in t[0] else 3))))
    lat1.legend(handles=handles,labels=labels,loc="upper center",ncol=5,fontsize=19,frameon=True,handletextpad=0.1,handlelength=1,borderpad=0.3,edgecolor="black",shadow=False,fancybox=False,columnspacing=0.8,bbox_to_anchor=(0.5,1.27))
    
    lat1.set_xlabel("Latency percentile (%) - 4k aligned")
    lat1.set_ylabel("Latency (μs)")
    # lat1.set_ylim( top=600)
    # lat1.yaxis.set_major_locator(MultipleLocator(75))
    
      
    # ---------lat2-------------
    iops_requirements = {"blocksize": {"128k"}, "cpunum": {96},"numjobs":{1},"iodepth":{1},"rw":{"randread"},"blockalign":{"128k"}}
    fio_perfs_iops = filter_results(fio_perfs, iops_requirements)
    cpu_loads_iops = filter_results(cpu_loads, iops_requirements)

    # fio_perfs_iops = combine_key(fio_perfs_iops, "scheme_rate", "scheme", "rate")
    # cpu_loads_iops = combine_key(cpu_loads_iops, "scheme_rate", "scheme", "rate")

    schemes_iops, fio_perfs_iops_by_schemes = group_by("scheme", fio_perfs_iops)
    schemes_iops, cpu_loads_iops_by_schemes = group_by("scheme", cpu_loads_iops)

    for scheme in schemes_iops:
        fio_perfs_iops_by_schemes[scheme].sort(key=lambda item: item["iodepth"])
        cpu_loads_iops_by_schemes[scheme].sort(key=lambda item: item["iodepth"])

    for scheme in schemes_iops:
        plot_cumulative_lat(
            scheme, lat2, f"{scheme}", "scheme", fio_perfs_iops_by_schemes[scheme])
    handles, labels = lat1.get_legend_handles_labels()
    labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: (1 if "Non-offloading" in t[0] else (2 if "Offloading" in t[0] else 3))))
    lat2.legend(handles=handles,labels=labels,loc="upper center",ncol=5,fontsize=19,frameon=True,handletextpad=0.1,handlelength=1,borderpad=0.3,edgecolor="black",shadow=False,fancybox=False,columnspacing=0.8,bbox_to_anchor=(0.5,1.27))
    
    lat2.set_xlabel("Latency percentile (%) - 128k aligned")
    lat2.set_ylabel("Latency (μs)")
    # lat2.set_ylim(top=1300)
    # lat2.yaxis.set_major_locator(MultipleLocator(250))

    
    res = fig_path+"/ssd"+postfix
    fig.savefig(f"{res}.png", dpi=300)
    fig.savefig(f"{res}.pdf", format="pdf")



def plot_rw_qd(cpu_loads, fio_perfs, fig_path):

    # ---------iops-------------

    

    plot_iops_with_complex(cpu_loads, fio_perfs, fig_path, "")

    fio_perfs_without_HyQ = filter_results(fio_perfs, {"scheme": {"Non-offloading", "Offloading"}})
    cpu_loads_without_HyQ = filter_results(cpu_loads, {"scheme": {"Non-offloading", "Offloading"}})
    plot_iops_with_complex_without_HyQ(cpu_loads_without_HyQ, fio_perfs_without_HyQ, fig_path, "_without_HyQ")

    # ---------------bandwidth-------------------
    # ALLOWED_NAMES_BW = {"Non-offloading", "Naive-Offloading", "HyPath"}

    # ALLOWED_RW_BW = {"randrw-50%"}
    # ALLOWED_QD_BW = {4, 8, 16, 32, 64}
    # ALLOWED_JOBS_BW = {8}
    # ALLOWED_BS_BW = {"128k"}
    # ALLOWED_CPU_NUM = {96}
    # names_bw, cpu_loads_by_names_bw, io_perfs_by_names_bw = filter_loads(
    #     cpu_loads,
    #     io_perfs,
    #     ALLOWED_NAMES_BW,
    #     ALLOWED_RW_BW,
    #     ALLOWED_QD_BW,
    #     ALLOWED_JOBS_BW,
    #     ALLOWED_BS_BW,
    #     ALLOWED_CPU_NUM,
    # )

    # plot_result_single(
    #     "Bandwidth",
    #     names_iops,
    #     cpu_loads_by_names_iops,
    #     io_perfs_by_names_iops,
    #     None,
    #     None,
    #     "iodepth",
    #     "Various Test Case",
    #     fig_path,
    # )

    # # plot_result_single("IOPS", names_iops, cpu_loads_by_names_iops,
    # #                    io_perfs_by_names_iops, cpu_loads_by_names_bw,
    # #                    io_perfs_by_names_bw, "casename", "Various Test Case", resfile)
    # # plot_result_single("Bandwidth", names_iops, cpu_loads_by_names_bw,
    # #                    io_perfs_by_names_bw, cpu_loads_by_names_iops,
    # #                    io_perfs_by_names_iops, "casename", "Various Test Case", resfile)
    # # plot_result_single("Bandwidth", names_iops, cpu_loads_by_names_iops,
    # #                    io_perfs_by_names_iops, cpu_loads_by_names_bw,
    # #                    io_perfs_by_names_bw, "casename", "Various Test Case", resfile)

    # plot_result_single(
    #     "cutil-iops",
    #     names_iops,
    #     cpu_loads_by_names_iops,
    #     io_perfs_by_names_iops,
    #     cpu_loads_by_names_bw,
    #     io_perfs_by_names_bw,
    #     "casename",
    #     "Various Test Case",
    #     fig_path,
    # )

    # # plot_result_single("cutil-bw", names_iops, cpu_loads_by_names_bw,
    # #                    io_perfs_by_names_bw, cpu_loads_by_names_iops,
    # #                    io_perfs_by_names_iops, "casename", "Various Test Case", resfile)

    # # -------------latency-------------------
    # ALLOWED_NAMES_LAT = {"Non-offloading", "Naive-Offloading", "HyPath"}

    # # ALLOWED_RW_LAT = {"rw", "read", "write"}
    # ALLOWED_RW_LAT = {"randread", "randwrite", "seqread", "seqwrite"}
    # ALLOWED_QD_LAT = {1}
    # ALLOWED_JOBS_LAT = {1}
    # ALLOWED_BS_LAT = {"128k"}
    # names_lat, cpu_loads_by_names_lat, io_perfs_by_names_lat = filter_loads(
    #     cpu_loads,
    #     io_perfs,
    #     ALLOWED_NAMES_LAT,
    #     ALLOWED_RW_LAT,
    #     ALLOWED_QD_LAT,
    #     ALLOWED_JOBS_LAT,
    #     ALLOWED_BS_LAT,
    #     ALLOWED_CPU_NUM,
    # )

    # plot_result_single_latency(
    #     "Latency",
    #     names_lat,
    #     cpu_loads_by_names_lat,
    #     io_perfs_by_names_lat,
    #     cpu_loads_by_names_lat,
    #     io_perfs_by_names_lat,
    #     "casename",
    #     "Various Test Case",
    #     fig_path,
    # )
    # # plot_result_single("Latency", names_lat, cpu_loads_by_names_lat,
    # #                    io_perfs_by_names_lat, cpu_loads_by_names_lat,
    # #                    io_perfs_by_names_lat, "casename", "Various Test Case", resfile)
    # plt_clu(io_perfs, fig_path)


if __name__ == "__main__":
    fio_path = sys.argv[1]
    cpu_path = sys.argv[2]
    fig_path = sys.argv[3]

    # --------获取数据---------
    fio_perfs = read_fio_perfs(fio_path)
    # print(io_perfs)
    cpu_loads = read_cpu_loads(cpu_path)
    # print (cpu_loads)

    # #--------处理数据、作图----
    # print("begin to plot")
    plot_rw_qd(cpu_loads, fio_perfs, fig_path)
