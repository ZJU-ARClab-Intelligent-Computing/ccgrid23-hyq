#!/bin/bash

SCRIPTDIR=$(dirname $(readlink -f "$0"))

# Apply configurations.
source $SCRIPTDIR/../config.sh

generate_job() {
    jobname="${rw}_${rwmixwrite}_${bs}_${ba}_${numjobs}_${iodepth}_${rate_iops}_${numdisks}_${numcores}"
    jobfile="$SCRIPTDIR/fio-job/$jobname"

    echo "benchmark $jobname \$i"
    echo ""

    echo -n "" > $jobfile
    echo "[global]" >> $jobfile
    echo "norandommap" >> $jobfile
    echo "ioengine=libaio" >> $jobfile
    echo "group_reporting" >> $jobfile
    echo "direct=1" >> $jobfile
    echo "time_based=1" >> $jobfile
    echo "runtime=$runtime" >> $jobfile
    echo "rw=$rw" >> $jobfile
    echo "rwmixwrite=$rwmixwrite" >> $jobfile

    echo "bs=$bs" >> $jobfile
    echo "ba=$ba" >> $jobfile
    echo "numjobs=$numjobs" >> $jobfile
    echo "iodepth=$iodepth" >> $jobfile
    echo "rate_iops=$rate_iops" >> $jobfile

    cnt=0
    for device in $DEVICES; do
        echo "" >> $jobfile
        echo "[job$cnt]" >> $jobfile
        echo "filename=$device" >> $jobfile

        cnt=$(($cnt + 1))
        if [ $cnt -ge $numdisks ]; then
            break
        fi
    done
}

mkdir -p $SCRIPTDIR/fio-job

runtime=300

# Generate iops limited jobs.
rw=randread
rwmixwrite=0
bs=4k
ba=4k
numjobs=8
iodepth=64
numdisks=2
numcores=48
for rate_iops in 12500 37500 45000 62500 87500 112500; do
    generate_job
done

# Generate read/write mixed jobs with different write ratios.
rw=randrw
bs=128k
ba=128k
numjobs=8
iodepth=64
rate_iops=2147483647
numdisks=2
numcores=48
for rwmixwrite in 0 30 50 70 100; do
    generate_job
done

# Generate 4k-align/128k-align tpt jobs.
rw=randread
rwmixwrite=0
bs=128k
numjobs=8
iodepth=64
rate_iops=2147483647
numdisks=2
numcores=48
for ba in 4k 128k; do
    generate_job
done

# Generate 4k-align/128k-align lat jobs.
rw=randread
rwmixwrite=0
bs=128k
numjobs=1
iodepth=1
rate_iops=2147483647
numdisks=1
numcores=48
for ba in 4k 128k; do
    generate_job
done

# Generate different nr_cpu jobs.
rw=randread
rwmixwrite=0
bs=4k
ba=4k
numjobs=8
iodepth=64
rate_iops=2147483647
numdisks=2
for numcores in 2 4 6 8; do
    generate_job
done
