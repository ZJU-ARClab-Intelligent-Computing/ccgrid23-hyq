#!/usr/bin/python3

from tools import *


def plot_bar(plt, items, x_key, y_key, label, offset, width, edgecolor, data):
    x = [item[x_key] for item in items]
    y = [item[y_key] for item in items]
    ticks = [i for i in range(len(items))]
    data.append(y)

    container = plt.bar(
        [i + offset for i in ticks],
        y,
        width=width,
        color=edgecolor,
        label=label,
        edgecolor="black",
        linewidth=1,
        zorder=100,
    )

    if y_key == "iops":
        for a, b in zip([i + offset for i in ticks], y):
            plt.text(
                a + 0.005,
                b + 30.1,
                "%.1f" % float(b),
                ha="center",
                va="bottom",
                fontsize=18,
                rotation=90,
                clip_on=False,
            )
        plt.set_ylim(bottom=0, top=2200)
        plt.set_xticks(ticks)
        plt.set_xticklabels(x, fontsize=20, color="black")
        plt.yaxis.set_major_locator(MultipleLocator(400))

    elif y_key == "bandwidth":
        for a, b in zip([i + offset for i in ticks], y):
            plt.text(
                a + 0.005,
                b + 120,
                "%.1f" % float(b),
                ha="center",
                va="bottom",
                fontsize=18,
                rotation=90,
                clip_on=False,
            )
        plt.set_ylim(bottom=0, top=8500)
        plt.set_xticks(ticks)
        plt.set_xticklabels(x, fontsize=20, color="black")
        plt.yaxis.set_major_locator(MultipleLocator(1500))
    elif y_key == "latency":
        for a, b in zip([i + offset for i in ticks], y):
            plt.text(
                a,
                b + 2,
                "%.1f" % float(b),
                ha="center",
                va="bottom",
                fontsize=20,
                rotation=90,
                clip_on=False,
            )
        plt.set_ylim(bottom=0, top=2200)
        plt.set_xticks(ticks)
        plt.yaxis.set_major_locator(MultipleLocator(500))
        plt.set_xticklabels(x, fontsize=22)
    elif y_key == "normalized_latency":
        for a, b in zip([i + offset for i in ticks], y):
            plt.text(
                a,
                b + 0.06,
                "%.1f" % float(b) + "%",
                ha="center",
                va="bottom",
                fontsize=22,
                rotation=90,
                clip_on=False,
            )
        # plt.set_ylim(bottom=0, top=180)
        plt.tick_params(axis="x", pad=50)
    elif y_key == "cutil":
        for a, b in zip([i + offset for i in ticks], y):
            plt.text(
                a + 0.01,
                b + 0.2,
                "%.1f" % float(b),
                ha="center",
                va="bottom",
                fontsize=20,
                rotation=90,
                clip_on=False,
            )
        # plt.set_ylim(bottom=0, top=14.5)
        # plt.tick_params(axis='x', pad=50)
        # plt.yaxis.set_major_locator(MultipleLocator(3))
        plt.set_xticks(ticks)
        plt.set_xticklabels(x, fontsize=20, color="black")
    else:
        for a, b in zip([i + offset for i in ticks], y):
            plt.text(
                a,
                b + 0.06,
                "%.1f" % float(b) + "%",
                ha="center",
                va="bottom",
                fontsize=22,
                rotation=90,
                clip_on=False,
            )
        # plt.set_ylim(bottom=0, top=140)
        plt.tick_params(axis="x", pad=50)
        plt.set_xticks(ticks)
        plt.set_xticklabels(x, fontsize=25)
    # plt.tick_params(axis='y', pad=20)
    # plt.get_xaxis().set_visible(False)


# 绘制网格
def plot_grid(plt):
    plt.grid(axis="y", color="silver", linewidth=0.7, zorder=0)


def plot_result_single(
    title,
    names,
    cpu_loads_iops,
    io_perfs_iops,
    cpu_loads_bw,
    io_perfs_bw,
    x_key,
    x_label,
    resfile,
    suffix_name,
):
    plt.rcParams.update({"font.size": 20})
    # 创建绘图

    if title == "cutil-iops" or title == "cutil-bw":
        margin_left = 0.09
    else:
        margin_left = 0.11

    fig, (normalized_iops) = plt.subplots(nrows=1, ncols=1, figsize=(10, 4))
    # fig.subplots_adjust(left=0.115, right=0.995, top=0.85, bottom=0.2)
    fig.subplots_adjust(left=margin_left, right=0.995, top=0.85, bottom=0.2)

    plot_set_tick(normalized_iops)

    # 计算iops、bw、lat相对值
    # cal_relative_perf(names,io_perfs_iops)

    # 设置y轴名称
    if title == "IOPS":
        normalized_iops.set_ylabel("IOPS (K)", fontsize=20)
    elif title == "Bandwidth":
        normalized_iops.set_ylabel("Bandwidth (MB/s)", fontsize=20)

    elif title == "Latency":
        normalized_iops.set_ylabel("Latency(μs)", fontsize=20)

    elif title == "cutil-iops" or title == "cutil-bw":
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

    row = []
    col = []
    data = []
    cnt = 0
    for name in ORDERED_NAMES:
        if name in names:
            col.append(name)
            cnt = cnt + 1
            if cnt == 1:
                row = [item["rw"] for item in io_perfs_iops[name]]
            if title == "IOPS":
                # normalized_iops.legend()

                plot_bar(
                    normalized_iops,
                    io_perfs_iops[name],
                    x_key,
                    "iops",
                    name,
                    offset * width,
                    width,
                    BAR_COLORS[name],
                    data,
                )
                offset += 1.0
                # plt.legend()
            elif title == "Bandwidth":
                plot_bar(
                    normalized_iops,
                    io_perfs_iops[name],
                    x_key,
                    "bandwidth",
                    name,
                    offset * width,
                    width,
                    BAR_COLORS[name],
                    True,
                    data,
                )
                offset += 1.0

            elif title == "Latency":
                plot_bar(
                    normalized_iops,
                    io_perfs_iops[name],
                    x_key,
                    "latency",
                    name,
                    offset * width,
                    width,
                    BAR_COLORS[name],
                    data,
                )
                offset += 1.0
            elif title == "cutil-iops" or title == "cutil-bw":
                plot_bar(
                    normalized_iops,
                    cpu_loads_iops[name],
                    x_key,
                    "cutil",
                    name,
                    offset * width,
                    width,
                    BAR_COLORS[name],
                    data,
                )
                offset += 1.0
                # normalized_iops.set_ylim(bottom=0, top=150)
    # normalized_iops.legend(ncol=4,fontsize="small",columnspacing=0.7,handletextpad=0.1,bbox_to_anchor=(0.9,1.25),edgecolor="black",borderpad=0.3)
    # write_excel(title,row,col,data)
    normalized_iops.legend(
        ncol=5,
        fontsize=19,
        frameon=True,
        handletextpad=0.1,
        handlelength=1,
        borderpad=0.3,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.25),
        edgecolor="black",
        shadow=False,
        fancybox=False,
    )

    res = resfile + "/" + title + "_iops_rate" + suffix_name
    fig.savefig(f"{res}.png", dpi=300)
    fig.savefig(f"{res}.pdf", format="pdf")


def plot_result_single_latency(
    title,
    names,
    cpu_loads_iops,
    io_perfs_iops,
    cpu_loads_bw,
    io_perfs_bw,
    x_key,
    x_label,
    resfile,
):
    plt.rcParams.update({"font.size": 20})
    # 创建绘图

    fig, (iops) = plt.subplots(nrows=1, ncols=1, figsize=(10, 4))
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

    row = []
    col = []
    data = []
    cnt = 0

    for name in ORDERED_NAMES:
        if name in names:
            col.append(name)
            cnt = cnt + 1
            if cnt == 1:
                row = [item["rw"] for item in io_perfs_iops[name]]
            plot_bar(
                iops,
                io_perfs_iops[name],
                x_key,
                "latency",
                name,
                offset * width,
                width,
                BAR_COLORS[name],
                True,
                data,
            )
            offset += 1.0
    # write_excel(title, row, col, data)
    # 绘制网格

    # iops.legend(loc="upper center",ncol=4,fontsize='small',columnspacing=0.7,handletextpad=0.1,bbox_to_anchor=(0.55,1.25),edgecolor="black",borderpad=0.3)
    iops.legend(
        loc="upper center",
        ncol=5,
        fontsize=19,
        frameon=True,
        handletextpad=0.1,
        handlelength=1,
        borderpad=0.3,
        edgecolor="black",
        bbox_to_anchor=(0.5, 1.27),
        fancybox=False,
    )

    res = resfile + "/" + title
    fig.savefig(f"{res}.png", dpi=300)
    fig.savefig(f"{res}.pdf", format="pdf")


def plot_iops_with_rate(
    cpu_loads, fio_perfs, fig_path, iops_requirements={}, suffix_name=""
):
    iops_requirements = {**iops_requirements, "blocksize": {"4k"}, "numcores": {48}}
    fio_perfs_iops = filter_results(fio_perfs, iops_requirements)
    cpu_loads_iops = filter_results(cpu_loads, iops_requirements)

    fio_perfs_iops = combine_key(fio_perfs_iops, "scheme_rate", "scheme", "rate")
    cpu_loads_iops = combine_key(cpu_loads_iops, "scheme_rate", "scheme", "rate")

    schemes_iops, fio_perfs_iops_by_schemes = group_by("scheme", fio_perfs_iops)
    schemes_iops, cpu_loads_iops_by_schemes = group_by("scheme", cpu_loads_iops)

    for scheme in schemes_iops:
        fio_perfs_iops_by_schemes[scheme] = merge_by(
            "scheme_rate", merge_io_perf, fio_perfs_iops_by_schemes[scheme]
        )
        fio_perfs_iops_by_schemes[scheme].sort(key=lambda item: item["rate"])

        cpu_loads_iops_by_schemes[scheme] = merge_by(
            "scheme_rate", merge_cpu_load, cpu_loads_iops_by_schemes[scheme]
        )
        cpu_loads_iops_by_schemes[scheme].sort(key=lambda item: item["rate"])

    plot_result_single(
        "IOPS",
        schemes_iops,
        cpu_loads_iops_by_schemes,
        fio_perfs_iops_by_schemes,
        None,
        None,
        "rate",
        "I/O workload pressure (K IOPS)",
        fig_path,
        suffix_name,
    )

    plot_result_single(
        "Latency",
        schemes_iops,
        cpu_loads_iops_by_schemes,
        fio_perfs_iops_by_schemes,
        None,
        None,
        "rate",
        "I/O workload pressure (K IOPS)",
        fig_path,
        suffix_name,
    )

    plot_result_single(
        "cutil-iops",
        schemes_iops,
        cpu_loads_iops_by_schemes,
        fio_perfs_iops_by_schemes,
        None,
        None,
        "rate",
        "I/O workload pressure (K IOPS)",
        fig_path,
        suffix_name,
    )


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
    plot_iops_with_rate(cpu_loads, fio_perfs, fig_path)
    plot_iops_with_rate(
        cpu_loads,
        fio_perfs,
        fig_path,
        {"scheme": {"Non-offloading", "Offloading"}},
        "_without_HyQ",
    )
