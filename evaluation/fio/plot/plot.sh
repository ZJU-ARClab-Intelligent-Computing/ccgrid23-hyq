#!/bin/bash

# nowdate=$(date "+%Y%m%d%H%M%S")
nowdate="20221204165152"

dst_fio_dir="./results/fio/$nowdate"
dst_cpu_dir="./results/cpu/$nowdate"
dst_tgt_cpu_dir="./results/tgt_cpu/$nowdate"
dst_fig_dir="./figures/$nowdate"

mkdir -p $dst_fio_dir
mkdir -p $dst_cpu_dir
mkdir -p $dst_tgt_cpu_dir
mkdir -p $dst_fig_dir

for tc in hypath kernel cx5; do
    cpu_dir="../$tc/cpu_res"
    cpu_res=$(ls $cpu_dir -rt | tail -n 1)

    tgt_cpu_dir="../$tc/cpu_res_target"
    tgt_cpu_res=$(ls $tgt_cpu_dir -rt | tail -n 1)

    fio_dir="../$tc/fio_res"
    fio_res=$(ls $fio_dir -rt | tail -n 1)

    cp -rf $cpu_dir/$cpu_res/* $dst_cpu_dir
    cp -rf $tgt_cpu_dir/$tgt_cpu_res/* $dst_tgt_cpu_dir
    cp -rf $fio_dir/$fio_res/* $dst_fio_dir
done

python3 ./plot_ssd.py $dst_fio_dir $dst_tgt_cpu_dir $dst_fig_dir
python3 ./plot_nd_bw.py $dst_fio_dir $dst_tgt_cpu_dir $dst_fig_dir
python3 ./plot_iops_rate.py $dst_fio_dir $dst_tgt_cpu_dir $dst_fig_dir
python3 ./plot_core_limited.py $dst_fio_dir $dst_tgt_cpu_dir $dst_fig_dir
