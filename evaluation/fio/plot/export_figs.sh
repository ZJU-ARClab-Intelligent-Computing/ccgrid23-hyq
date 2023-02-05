#!/bin/bash

src_dir=./figures
dst_dir=$1

mkdir -p dst_dir

mv $src_dir/ssd_without_HyQ.pdf $dst_dir/fig-3-motivation-device-specified-optimization.pdf
mv $src_dir/IOPS_iops_rate_without_HyQ.pdf $dst_dir/fig-4-motivation-processing-capability.pdf
mv $src_dir/Bandwidth_nd_bw_without_HyQ.pdf $dst_dir/fig-5-motivation-complex-io-patterns.pdf
mv $src_dir/IOPS_iops_rate.pdf $dst_dir/fig-9-evaluation-process-capability.pdf
mv $src_dir/Latency_iops_rate.pdf $dst_dir/fig-10-evaluation-processing-capability-lat.pdf
# mv $src_dir/cutil-bw_nd_bw.pdf $dst_dir/evaluation-complex-io-patterns-cpu-util.pdf
# mv $src_dir/cutil-iops_core_limited.pdf $dst_dir/evaluation-limited-cpu-resources-cpu-util.pdf
mv $src_dir/cutil-iops_iops_rate.pdf $dst_dir/fig-11-evaluation-process-capability-cpu-util.pdf
mv $src_dir/IOPS_core_limited.pdf $dst_dir/fig-12-evaluation-limited-cpu-resources.pdf
mv $src_dir/ssd.pdf $dst_dir/fig-13-evaluation-device-specified-optimization.pdf
mv $src_dir/ssd_lat.pdf $dst_dir/fig-14-evaluation-device-specified-optimization-lat.pdf
mv $src_dir/Bandwidth_nd_bw.pdf $dst_dir/fig-15-evaluation-complex-io-patterns.pdf
