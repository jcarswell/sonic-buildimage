#!/bin/bash


OPTS=""
if [ "$2" == "--force"]; then
    OPTS+="-f"
fi

if [ "$1" == "init"]; then
    modprobe i2c_dev
    modprobe i2c_i801
    modprobe i2c_ismt
    modprobe i2c_mux_pca954x force_deselect_on_exit=1
    modprobe accton_as5822_54x_cpld
    modprobe ym2651y
    modprobe accton_as5822_54x_fan
    modprobe accton_as5822_54x_leds
    modprobe accton_as5822_54x_psu
    #running platform init
    accton_as5822-54x_util.py $OPTS install
    #start services
    systemctl enable as5822-platform-monitor-fan.service
    systemctl start as5822-platform-monitor-fan.service
    systemctl enable as5822-platform-monitor-psu.service
    systemctl start as5822-platform-monitor-psu.service
    systemctl enable as5822-platform-monitor.service
    systemctl start as5822-platform-monitor.service

elif [ "$1" == "deinit" ]; then
    systemctl stop as5822-platform-monitor-fan.service
    systemctl stop as5822-platform-monitor-psu.service
    systemctl stop as5822-platform-monitor.service
    systemctl disable as5822-platform-monitor-fan.service
    systemctl disable as5822-platform-monitor-psu.service
    systemctl disable as5822-platform-monitor.service
    
    accton_as5822-54x_util.py $OPTS clean

    modprobe -r accton_as5822_54x_psu
    modprobe -r accton_as5822_54x_fan
    modprobe -r accton_as5822_54x_leds
    modprobe -r ym2651y
    modprobe -r accton_as5822_54x_cpld
    modprobe -r i2c_mux_pca954x
    modprobe -r i2c-dev

else
    echo "${0}: Invalid option"
fi
