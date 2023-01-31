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

limit_cpu_to $1
