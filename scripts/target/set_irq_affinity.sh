#!/bin/bash

irqs=$(cat /proc/interrupts | grep $1 | awk -F '[ :]' '{print $2}')
nr_cpus=$(cat /sys/devices/system/cpu/online | tr "-" " " | awk '{print $2}')
nr_cpus=$(($nr_cpus + 1))

cpu=0
for irq in $irqs; do
    sudo tuna -q $irq -c $cpu -m
    cpu=$(echo "($cpu + 1) % $nr_cpus" | bc)
done
