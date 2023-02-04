#!/bin/bash

src_dir=./figures
dst_dir=$1

mkdir -p dst_dir

cp $src_dir/Bandwidth_nd_bw_without_HyQ.pdf $dst_dir/motivation-complex-io-patterns.pdf
cp $src_dir/Bandwidth_nd_bw.pdf $dst_dir/evaluation-complex-io-patterns.pdf
cp $src_dir/cutil-bw_nd_bw.pdf $dst_dir/evaluation-complex-io-patterns-cpu-util.pdf
cp $src_dir/cutil-iops_core_limited.pdf $dst_dir/evaluation-limited-cpu-resources-cpu-util.pdf
cp $src_dir/cutil-iops_iops_rate.pdf $dst_dir/evaluation-process-capability-cpu-util.pdf
cp $src_dir/IOPS_core_limited.pdf $dst_dir/evaluation-limited-cpu-resources.pdf
cp $src_dir/IOPS_iops_rate_without_HyQ.pdf $dst_dir/motivation-processing-capability.pdf
cp $src_dir/IOPS_iops_rate.pdf $dst_dir/evaluation-process-capability.pdf
cp $src_dir/ssd_lat.pdf $dst_dir/evaluation-device-specified-optimization-lat.pdf
cp $src_dir/ssd.pdf $dst_dir/evaluation-device-specified-optimization.pdf
cp $src_dir/ssd_without_HyQ.pdf $dst_dir/motivation-device-specified-optimization.pdf
cp $src_dir/Latency_iops_rate.pdf $dst_dir/evaluation-processing-capability-lat.pdf
