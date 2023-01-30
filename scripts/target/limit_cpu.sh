#!/bin/bash

MAX_CPU_ID=$(cat /sys/devices/system/cpu/possible | tr "-" " " | awk '{print $2}')

limit_cpu_to() {
    local nr_cores=$1

    for cpuid in $(seq 0 $(( $nr_cores - 1 ))); do
        echo 1 | sudo tee /sys/devices/system/cpu/cpu$cpuid/online 1> /dev/null
        echo performance | sudo tee /sys/devices/system/cpu/cpu$cpuid/cpufreq/scaling_governor 1> /dev/null
    done

    for cpuid in $(seq $nr_cores $MAX_CPU_ID); do
        echo 0 | sudo tee /sys/devices/system/cpu/cpu$cpuid/online 1> /dev/null
    done
}

# low=$1
# high=$2
# step=$3

# if [ $low -lt 2 ]; then
#     low=2
# fi

# if [ $high -gt $MAX_CPU_ID ]; then
#     high=$MAX_CPU_ID
# fi

# while true; do
#     for nr_cores in $(seq $low $step $high); do
#         limit_cpu_to $nr_cores
#         echo "Limited number of cpu cores to: $nr_cores"
#         sleep 30
#     done
# done

limit_cpu_to $1
