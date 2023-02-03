#!/bin/bash

fio_dir="../fio_res"
tgt_cpu_dir="../tgt_cpu_res"
dst_fig_dir="./figures"

mkdir -p $dst_fig_dir

python3 ./plot_device_optim.py $fio_dir $tgt_cpu_dir $dst_fig_dir
python3 ./plot_rwmixed.py $fio_dir $tgt_cpu_dir $dst_fig_dir
python3 ./plot_iops_rate.py $fio_dir $tgt_cpu_dir $dst_fig_dir
python3 ./plot_limited_cores.py $fio_dir $tgt_cpu_dir $dst_fig_dir
