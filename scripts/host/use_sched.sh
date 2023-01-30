#!/bin/bash

if [ ! $# -eq 1 ]; then
    echo "usage: $0 <scheduler>"
    exit -1
fi

num_nvme_disks=$(ls /sys/block/ | grep "nvme[0-9]\+n1" | wc -l)
for ((disk=0;disk<${num_nvme_disks};disk++)); do
    if [ -e "/dev/nvme${disk}-scheduler" ]; then
        echo $1 | sudo tee "/dev/nvme${disk}-scheduler"
    fi
done