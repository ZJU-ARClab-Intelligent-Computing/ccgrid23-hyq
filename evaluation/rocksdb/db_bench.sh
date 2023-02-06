#!/bin/bash

SCRIPTDIR=$(dirname $(readlink -f "$0"))

# Script parameters
DEVICES=$1
BENCHMARK=$2
OUTPUT_DIR=$3

# Units
K=1024
M=$((1024 * $K))
G=$((1024 * $M))

# Benchmark parameters
BENCH_NUM_KEYS=$((1000 * 1000))
BENCH_CACHE_SIZE=$((32 * $M))
BENCH_NUM_THREADS=64
BENCH_DURATION=180
BENCH_KEY_SIZE=256
BENCH_VALUE_SIZE=4096
BENCH_BLOCK_SIZE=$((8 * $K))

# Mount filesystems
function mount_devices {
    for device in $DEVICES; do
        local mnt_point=$SCRIPTDIR/rocksdb_mnt/$(basename $device)
        mkdir -p $mnt_point
        umount $mnt_point > /dev/null 2>&1 || true
        sudo mkfs -t ext4 $device
        mount -t ext4 $device $mnt_point
    done
}

# Unmount filesystems
function umount_devices {
    for device in $DEVICES; do
        local mnt_point=$SCRIPTDIR/rocksdb_mnt/$(basename $device)
        umount $mnt_point
    done
}

# Prepare database for benchmark
function load_database {
    local job_pids=""

    for device in $DEVICES; do
        local mnt_point=$SCRIPTDIR/rocksdb_mnt/$(basename $device)

        cd $SCRIPTDIR/rocksdb/tools/ &&
            JOB_ID=$(basename $device) \
            DB_DIR=$mnt_point/db \
            WAL_DIR=$mnt_point/wal \
            NUM_KEYS=$BENCH_NUM_KEYS \
            NUM_THREADS=$BENCH_NUM_THREADS \
            KEY_SIZE=$BENCH_KEY_SIZE \
            VALUE_SIZE=$BENCH_VALUE_SIZE \
            CACHE_SIZE=$BENCH_CACHE_SIZE \
                ./benchmark.sh bulkload \
                --use_direct_reads=1 \
                --use_direct_io_for_flush_and_compaction=1 &

        job_pids="$job_pids $!"
    done

    wait $job_pids
}

# Run the benchmark
function run_benchmark {
    local job_pids=""

    # Run benchmark for each device parallelly
    for device in $DEVICES; do
        local mnt_point=$SCRIPTDIR/rocksdb_mnt/$(basename $device)

        cd $SCRIPTDIR/rocksdb/tools/ &&
            JOB_ID=$(basename $device) \
            DB_DIR=$mnt_point/db \
            WAL_DIR=$mnt_point/wal \
            NUM_KEYS=$BENCH_NUM_KEYS \
            DURATION=$BENCH_DURATION \
            NUM_THREADS=$BENCH_NUM_THREADS \
            OUTPUT_DIR=$OUTPUT_DIR \
            KEY_SIZE=$BENCH_KEY_SIZE \
            VALUE_SIZE=$BENCH_VALUE_SIZE \
            CACHE_SIZE=$BENCH_CACHE_SIZE \
                ./benchmark.sh $BENCHMARK \
                --use_direct_reads=1 \
                --use_direct_io_for_flush_and_compaction=1 &
                
        job_pids="$job_pids $!"
    done

    wait $job_pids
}

if [ ! -x $SCRIPTDIR/rocksdb/tools/db_bench ]; then
    cd $SCRIPTDIR/rocksdb && \
    git checkout hyq && make db_bench DEBUG_LEVEL=0 -j8 && cp db_bench tools/
fi

mount_devices
load_database
run_benchmark
umount_devices
