#!/bin/bash

SCRIPTDIR=$(dirname $(readlink -f "$0"))

cd $SCRIPTDIR/ && \
mkdir -p ./fio_res/ ./cpu_res/ ./tgt_cpu_res/

# Test non-offloading scheme.
$SCRIPTDIR/test_non-offloading.sh

# Test offloading scheme.
$SCRIPTDIR/test_offloading.sh

# Test HyQ.
$SCRIPTDIR/test_hyq.sh
