#!/bin/bash

# Disable hyper-thread
echo off | sudo tee /sys/devices/system/cpu/smt/control

# Set CPUs to max performance
for cpu_id in $(cat /sys/devices/system/cpu/online | tr "-" " " | xargs seq); do
    echo performance | sudo tee /sys/devices/system/cpu/cpu$cpu_id/cpufreq/scaling_governor
done
