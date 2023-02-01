#!/bin/bash

SCRIPTDIR=$(dirname $(readlink -f "$0"))

cd $SCRIPTDIR/ && \
mkdir -p ./rocksdb_mnt ./rocksdb_res ./rocksdb_cpu ./rocksdb_tgt_cpu

# Test non-offloading scheme.
$SCRIPTDIR/test_non-offloading.sh

# Test offloading scheme.
$SCRIPTDIR/test_offloading.sh

# Test HyQ.
$SCRIPTDIR/test_hyq.sh
