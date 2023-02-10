#!/usr/bin/python3

from tools import *


def plot_overhead(fig_path, title, fio_perfs, cpu_loads, tgt_cpu_loads):
    iops_requirements = {"blocksize": {"4k"}, "rate": {34359738.352}, "numcores": {48}}
    fio_perfs_iops = filter_results(fio_perfs, iops_requirements)
    cpu_loads_iops = filter_results(cpu_loads, iops_requirements)
    tgt_cpu_loads_iops = filter_results(tgt_cpu_loads, iops_requirements)

    schemes_iops, fio_perfs_iops_by_schemes = group_by("scheme", fio_perfs_iops)
    schemes_iops, cpu_loads_iops_by_schemes = group_by("scheme", cpu_loads_iops)
    schemes_iops, tgt_cpu_loads_iops_by_schemes = group_by("scheme", tgt_cpu_loads_iops)

    tex_file = open(f"{fig_path}/{title}.tex", "w")

    for scheme in ORDERED_NAMES:
        if scheme in schemes_iops:
            fio_perf = merge_by(
                "numjobs", merge_io_perf, fio_perfs_iops_by_schemes[scheme]
            )
            fio_perf.sort(key=lambda item: item["numjobs"])

            cpu_load = merge_by(
                "numjobs", merge_cpu_load, cpu_loads_iops_by_schemes[scheme]
            )
            cpu_load.sort(key=lambda item: item["numjobs"])

            tgt_cpu_load = merge_by(
                "numjobs", merge_cpu_load, tgt_cpu_loads_iops_by_schemes[scheme]
            )
            tgt_cpu_load.sort(key=lambda item: item["numjobs"])

            tex_file.write(
                f"{scheme} & {fio_perf[0]['rlatency'] / 1000 :.4f} & {fio_perf[0]['rpercentile']['95.000000'] / 1000 / 1000 :.4f} & {fio_perf[0]['rpercentile']['99.000000'] / 1000 / 1000 :.4f} & {fio_perf[0]['rpercentile']['99.990000'] / 1000 / 1000 :.4f} & {fio_perf[1]['rbandwidth'] / 1024 :.2f} & {tgt_cpu_load[1]['cutil'] * 100 / 48 :.2f} & {cpu_load[1]['cutil'] * 100 / 48 :.2f} \\\\\n"
            )

    tex_file.close()


if __name__ == "__main__":
    fio_path = sys.argv[1]
    cpu_path = sys.argv[2]
    tgt_cpu_path = sys.argv[3]
    fig_path = sys.argv[4]

    # --------获取数据---------
    fio_perfs = read_fio_perfs(fio_path)
    # print(fio_perfs)
    cpu_loads = read_cpu_loads(cpu_path)
    # print (cpu_loads)
    tgt_cpu_loads = read_cpu_loads(tgt_cpu_path)
    # print(tgt_cpu_loads)

    # #--------处理数据、作图----
    # print("begin to plot")
    plot_overhead(
        fig_path, "tab-1-evaluation-hyq-overhead", fio_perfs, cpu_loads, tgt_cpu_loads
    )
