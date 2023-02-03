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
        plt.set_ylim(bottom=0, top=2000)
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
        plt.set_ylim(bottom=0, top=9500)
        plt.set_xticks(ticks)
        plt.set_xticklabels(x, fontsize=20, color="black")
        plt.yaxis.set_major_locator(MultipleLocator(2000))
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
        # plt.set_ylim(bottom=0, top=150)
        plt.set_xticks(ticks)
        plt.yaxis.set_major_locator(MultipleLocator(40))
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
                b + 0.3,
                "%.1f" % float(b),
                ha="center",
                va="bottom",
                fontsize=20,
                rotation=90,
                clip_on=False,
            )
        # plt.set_ylim(bottom=0, top=180)
        # plt.tick_params(axis='x', pad=50)
        plt.yaxis.set_major_locator(MultipleLocator(1))
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
    normalized_iops,
):
    plt.rcParams.update({"font.size": 20})
    # 创建绘图

    # if(title == "cutil-iops" or title=="cutil-bw"):
    #     margin_left=0.09
    # else:
    #     margin_left=0.11

    # fig, (normalized_iops) = plt.subplots(nrows=1, ncols=1, figsize=(10, 4))
    # # fig.subplots_adjust(left=0.115, right=0.995, top=0.85, bottom=0.2)
    # fig.subplots_adjust(left=margin_left, right=0.995, top=0.85, bottom=0.2)

    plot_set_tick(normalized_iops)

    # 计算iops、bw、lat相对值
    # cal_relative_perf(names,io_perfs_iops)

    # 设置y轴名称
    if title == "IOPS":
        normalized_iops.set_ylabel("IOPS (K)", fontsize=20)
    elif title == "Bandwidth":
        normalized_iops.set_ylabel("Bandwidth (MB/s)", fontsize=20)

    elif title == "Latency":
        normalized_iops.set_ylabel("Normalized Latency", fontsize=20)

    elif title == "cutil-iops" or title == "cutil-bw":
        normalized_iops.set_ylabel("Target CPU Utilization  (%)", fontsize=20)

    if title == "cutil-iops":
        normalized_iops.set_ylim(bottom=0, top=3.5)
    elif title == "cutil-bw":
        normalized_iops.set_ylim(bottom=0, top=3.5)

    normalized_iops.set_xlabel(x_label, fontsize=20)
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
                    data,
                )
                offset += 1.0

            elif title == "Latency":
                plot_bar(
                    normalized_iops,
                    io_perfs_iops[name],
                    x_key,
                    "normalized_latency",
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


def plot_cumulative_lat(rw, plot, title, name_key, io_perfs):
    # for type in ORDERED_NAMES:
    print("---------")
    print(io_perfs)
    plot_grid(plot)
    plot.yaxis.set_major_locator(MultipleLocator(50))
    for io_perf in io_perfs:
        print(io_perf)
        # if(io_perf["type"]==type):
        # if(rw in ["randread\n4k-1-1", "seqread\n4k-1-1"]):
        lats = io_perf["rpercentile"]
        avg_lat = f"{io_perf['rlatency']:.3f}"
        # else:
        # lats = io_perf["wpercentile"]
        # avg_lat = (f"{io_perf['wlatency']:.3f}")
        percents_old = sorted(lats.keys(), key=lambda key: float(key))
        # 将纳秒转换为微秒
        latencies = [lats[percent] / 1000.0 for percent in percents_old]

        percents = [float(percent) for percent in percents_old]

        # per_list=[95.00, 99.00,99.50, 99.90, 99.95]
        per_list = [30.00, 50.00, 70.00, 90.00, 99.00]

        x, y = filter_lat(per_list, percents, latencies)
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
            # color=COLORS1[io_perf["type"]][io_perf["rw"]],
            linestyle=LINE_STYLES[io_perf["scheme"]],
            color="black",
            # linestyle="solid",
            linewidth=1.5,
            marker=MARKERS[io_perf["scheme"]],
            markersize=10,
            # markeredgecolor=COLORS1[io_perf["type"]][io_perf["rw"]],
            markerfacecolor="white",
            markeredgewidth=1.5,
        )
    plot.set_xticks(ticks)

    plot.set_xticklabels([float(percent) for percent in x], fontsize=24)


def plot_iops_with_complex(cpu_loads, fio_perfs, fig_path, postfix):

    fig, (bw, cutil) = plt.subplots(nrows=1, ncols=2, figsize=(10, 4.5))
    fig.subplots_adjust(
        left=0.12, right=0.97, top=0.85, bottom=0.2, hspace=0.15, wspace=0.30
    )

    iops_requirements = {
        "blocksize": {"128k"},
        "numcores": {48},
        "numjobs": {8},
        "iodepth": {64},
        "rw": {"randread"},
        "blockalign": {"4k", "128k"},
    }
    fio_perfs_iops = filter_results(fio_perfs, iops_requirements)
    cpu_loads_iops = filter_results(cpu_loads, iops_requirements)

    # fio_perfs_iops = combine_key(fio_perfs_iops, "scheme_rate", "scheme", "rate")
    # cpu_loads_iops = combine_key(cpu_loads_iops, "scheme_rate", "scheme", "rate")

    schemes_iops, fio_perfs_iops_by_schemes = group_by("scheme", fio_perfs_iops)
    schemes_iops, cpu_loads_iops_by_schemes = group_by("scheme", cpu_loads_iops)

    for scheme in schemes_iops:
        fio_perfs_iops_by_schemes[scheme].sort(
            key=lambda item: item["blockalign"], reverse=True
        )
        cpu_loads_iops_by_schemes[scheme].sort(
            key=lambda item: item["blockalign"], reverse=True
        )

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
        bw,
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
        cutil,
    )
    cutil.legend(
        loc="upper center",
        ncol=5,
        fontsize=19,
        frameon=True,
        handletextpad=0.1,
        handlelength=1,
        borderpad=0.3,
        edgecolor="black",
        shadow=False,
        fancybox=False,
        columnspacing=0.8,
        bbox_to_anchor=(-0.25, 1.27),
    )

    res = fig_path + "/ssd" + postfix
    fig.savefig(f"{res}.png", dpi=300)
    fig.savefig(f"{res}.pdf", format="pdf")
    plt.close()

    fig, (lat1, lat2) = plt.subplots(nrows=1, ncols=2, figsize=(10, 4.5))
    fig.subplots_adjust(
        left=0.10, right=0.97, top=0.85, bottom=0.18, hspace=0.15, wspace=0.30
    )

    # ---------lat1-------------
    iops_requirements = {
        "blocksize": {"128k"},
        "numcores": {48},
        "numjobs": {1},
        "iodepth": {1},
        "rw": {"randread"},
        "blockalign": {"4k"},
    }
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
            scheme, lat1, f"{scheme}", "scheme", fio_perfs_iops_by_schemes[scheme]
        )
    handles, labels = lat1.get_legend_handles_labels()
    labels, handles = zip(
        *sorted(
            zip(labels, handles),
            key=lambda t: (
                1 if "Non-offloading" in t[0] else (2 if "Offloading" in t[0] else 3)
            ),
        )
    )
    # lat1.legend(handles=handles,labels=labels,loc="upper center",ncol=5,fontsize=19,frameon=True,handletextpad=0.1,handlelength=1,borderpad=0.3,edgecolor="black",shadow=False,fancybox=False,columnspacing=0.8,bbox_to_anchor=(0.5,1.27))

    lat1.set_xlabel("Latency percentile (%) - 4k aligned")
    lat1.set_ylabel("Latency (μs)")
    # lat1.set_ylim( top=600)
    # lat1.yaxis.set_major_locator(MultipleLocator(75))

    # ---------lat2-------------
    iops_requirements = {
        "blocksize": {"128k"},
        "numcores": {48},
        "numjobs": {1},
        "iodepth": {1},
        "rw": {"randread"},
        "blockalign": {"128k"},
    }
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
            scheme, lat2, f"{scheme}", "scheme", fio_perfs_iops_by_schemes[scheme]
        )
    handles, labels = lat1.get_legend_handles_labels()
    labels, handles = zip(
        *sorted(
            zip(labels, handles),
            key=lambda t: (
                1 if "Non-offloading" in t[0] else (2 if "Offloading" in t[0] else 3)
            ),
        )
    )
    lat2.legend(
        handles=handles,
        labels=labels,
        loc="upper center",
        ncol=5,
        fontsize=19,
        frameon=True,
        handletextpad=0.1,
        handlelength=1,
        borderpad=0.3,
        edgecolor="black",
        shadow=False,
        fancybox=False,
        columnspacing=0.8,
        bbox_to_anchor=(-0.25, 1.27),
    )

    lat2.set_xlabel("Latency percentile (%) - 128k aligned")
    lat2.set_ylabel("Latency (μs)")
    # lat2.set_ylim(top=1300)
    # lat2.yaxis.set_major_locator(MultipleLocator(250))

    res = fig_path + "/ssd_lat" + postfix
    fig.savefig(f"{res}.png", dpi=300)
    fig.savefig(f"{res}.pdf", format="pdf")


def plot_iops_with_complex_without_HyQ(cpu_loads, fio_perfs, fig_path, postfix):

    fig, (bw, lat1, lat2) = plt.subplots(nrows=1, ncols=3, figsize=(18, 4))
    fig.subplots_adjust(
        left=0.07, right=0.97, top=0.85, bottom=0.18, hspace=0.15, wspace=0.25
    )

    iops_requirements = {
        "blocksize": {"128k"},
        "numcores": {48},
        "numjobs": {8},
        "iodepth": {64},
        "rw": {"randread"},
        "blockalign": {"4k", "128k"},
    }
    fio_perfs_iops = filter_results(fio_perfs, iops_requirements)
    cpu_loads_iops = filter_results(cpu_loads, iops_requirements)

    # fio_perfs_iops = combine_key(fio_perfs_iops, "scheme_rate", "scheme", "rate")
    # cpu_loads_iops = combine_key(cpu_loads_iops, "scheme_rate", "scheme", "rate")

    schemes_iops, fio_perfs_iops_by_schemes = group_by("scheme", fio_perfs_iops)
    schemes_iops, cpu_loads_iops_by_schemes = group_by("scheme", cpu_loads_iops)

    for scheme in schemes_iops:
        fio_perfs_iops_by_schemes[scheme].sort(
            key=lambda item: item["blockalign"], reverse=True
        )
        cpu_loads_iops_by_schemes[scheme].sort(
            key=lambda item: item["blockalign"], reverse=True
        )

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
        bw,
    )
    bw.legend(
        loc="upper center",
        ncol=5,
        fontsize=19,
        frameon=True,
        handletextpad=0.1,
        handlelength=1,
        borderpad=0.3,
        edgecolor="black",
        shadow=False,
        fancybox=False,
        columnspacing=0.8,
        bbox_to_anchor=(0.5, 1.27),
    )

    # ---------lat1-------------
    iops_requirements = {
        "blocksize": {"128k"},
        "numcores": {48},
        "numjobs": {1},
        "iodepth": {1},
        "rw": {"randread"},
        "blockalign": {"4k"},
    }
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
            scheme, lat1, f"{scheme}", "scheme", fio_perfs_iops_by_schemes[scheme]
        )
    handles, labels = lat1.get_legend_handles_labels()
    labels, handles = zip(
        *sorted(
            zip(labels, handles),
            key=lambda t: (
                1 if "Non-offloading" in t[0] else (2 if "Offloading" in t[0] else 3)
            ),
        )
    )
    lat1.legend(
        handles=handles,
        labels=labels,
        loc="upper center",
        ncol=5,
        fontsize=19,
        frameon=True,
        handletextpad=0.1,
        handlelength=1,
        borderpad=0.3,
        edgecolor="black",
        shadow=False,
        fancybox=False,
        columnspacing=0.8,
        bbox_to_anchor=(0.5, 1.27),
    )

    lat1.set_xlabel("Latency percentile (%) - 4k aligned")
    lat1.set_ylabel("Latency (μs)")
    # lat1.set_ylim( top=600)
    # lat1.yaxis.set_major_locator(MultipleLocator(75))

    # ---------lat2-------------
    iops_requirements = {
        "blocksize": {"128k"},
        "numcores": {48},
        "numjobs": {1},
        "iodepth": {1},
        "rw": {"randread"},
        "blockalign": {"128k"},
    }
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
            scheme, lat2, f"{scheme}", "scheme", fio_perfs_iops_by_schemes[scheme]
        )
    handles, labels = lat1.get_legend_handles_labels()
    labels, handles = zip(
        *sorted(
            zip(labels, handles),
            key=lambda t: (
                1 if "Non-offloading" in t[0] else (2 if "Offloading" in t[0] else 3)
            ),
        )
    )
    lat2.legend(
        handles=handles,
        labels=labels,
        loc="upper center",
        ncol=5,
        fontsize=19,
        frameon=True,
        handletextpad=0.1,
        handlelength=1,
        borderpad=0.3,
        edgecolor="black",
        shadow=False,
        fancybox=False,
        columnspacing=0.8,
        bbox_to_anchor=(0.5, 1.27),
    )

    lat2.set_xlabel("Latency percentile (%) - 128k aligned")
    lat2.set_ylabel("Latency (μs)")
    # lat2.set_ylim(top=1300)
    # lat2.yaxis.set_major_locator(MultipleLocator(250))

    res = fig_path + "/ssd" + postfix
    fig.savefig(f"{res}.png", dpi=300)
    fig.savefig(f"{res}.pdf", format="pdf")


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
    plot_iops_with_complex(cpu_loads, fio_perfs, fig_path, "")

    fio_perfs_without_HyQ = filter_results(
        fio_perfs, {"scheme": {"Non-offloading", "Offloading"}}
    )
    cpu_loads_without_HyQ = filter_results(
        cpu_loads, {"scheme": {"Non-offloading", "Offloading"}}
    )
    plot_iops_with_complex_without_HyQ(
        cpu_loads_without_HyQ, fio_perfs_without_HyQ, fig_path, "_without_HyQ"
    )
