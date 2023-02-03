#!/bin/bash

dst_fio_dir="../fio_res"
dst_cpu_dir="../cpu_res"
dst_tgt_cpu_dir="../tgt_cpu_res"
dst_fig_dir="./figures"

mkdir -p $dst_fio_dir
mkdir -p $dst_cpu_dir
mkdir -p $dst_tgt_cpu_dir
mkdir -p $dst_fig_dir

# python3 ./plot_ssd.py $dst_fio_dir $dst_tgt_cpu_dir $dst_fig_dir
# python3 ./plot_nd_bw.py $dst_fio_dir $dst_tgt_cpu_dir $dst_fig_dir
python3 ./plot_iops_rate.py $dst_fio_dir $dst_tgt_cpu_dir $dst_fig_dir
# python3 ./plot_core_limited.py $dst_fio_dir $dst_tgt_cpu_dir $dst_fig_dir
