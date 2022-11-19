#!/usr/bin/env python3
#
# Copyright (C) 2019 Accton Networks, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Usage: %(scriptName)s [options] command object
options:
    -h | --help     : this help message
    -d | --debug    : run with debug mode
    -f | --force    : ignore error during installation or clean
command:
    install     : install drivers and generate related sysfs nodes
    clean       : uninstall drivers and remove related sysfs nodes    
"""

import subprocess
import getopt
import sys
import logging
import time
import os


PROJECT_NAME = "as5822_54x"
version = "0.1.0"
verbose = False
DEBUG = False
args = []
ALL_DEVICE = {}
FORCE = 0
PLATFORM_ROOT_PATH = "/usr/share/sonic/device"
PLATFORM_API2_WHL_FILE_PY3 ="sonic_platform-1.0-py3-none-any.whl"

kos = [
"modprobe i2c_dev",
"modprobe i2c_i801",
"modprobe i2c_ismt",
"modprobe i2c_mux_pca954x force_deselect_on_exit=1",
"modprobe accton_as5822_54x_cpld",
"modprobe ym2651y",
"modprobe accton_as5822_54x_fan",
"modprobe optoe",
"modprobe accton_as5822_54x_leds",
"modprobe accton_as5822_54x_psu" ]

i2c_prefix = "/sys/bus/i2c/devices/"
"""
i2c_bus = {"fan": ["3-0063"],
           "thermal": ["7-0048","8-0049", "9-004a", "9-004b"] ,
           "psu": ["3-0050","4-0051"],
           "sfp": ["-0050"]}
i2c_nodes = {"fan": ["present", "front_speed_rpm", "rear_speed_rpm"] ,
           "thermal": ["hwmon/hwmon*/temp1_input"] ,
           "psu": ["psu_present ", "psu_power_good"]    ,
           "sfp": ["module_present_", "module_tx_disable_"]}
"""
sfp_map =  list(range(1 + 17, 52 + 17))

qsfp_start = 48

#For sideband signals of SFP/QSFP modules.
cpld_of_module = {"10-0061": list(range(0, 38)),
                  "11-0062": list(range(38, 54)) }

mknod =[
"echo pca9548 0x72 > /sys/bus/i2c/devices/i2c-0/new_device",
"echo pca9548 0x71 > /sys/bus/i2c/devices/i2c-1/new_device" ,
"echo pca9548 0x71 > /sys/bus/i2c/devices/i2c-12/new_device" ,
"echo pca9548 0x72 > /sys/bus/i2c/devices/i2c-13/new_device" ,
"echo pca9548 0x73 > /sys/bus/i2c/devices/i2c-14/new_device",
"echo pca9548 0x74 > /sys/bus/i2c/devices/i2c-15/new_device",
"echo pca9548 0x75 > /sys/bus/i2c/devices/i2c-16/new_device",
"echo pca9548 0x76 > /sys/bus/i2c/devices/i2c-17/new_device",
"echo pca9548 0x71 > /sys/bus/i2c/devices/i2c-17/new_device",
#"*echo pca9548 0x75 > /sys/bus/i2c/devices/i2c-38/new_device",
#"*echo pca9548 0x76 > /sys/bus/i2c/devices/i2c-39/new_device",
"echo 24c02 0x57 > /sys/bus/i2c/devices/i2c-1/new_device",

#"*echo as5822_54x_fan 0x63 > /sys/bus/i2c/devices/i2c-3/new_device",
"echo lm75 0x48 > /sys/bus/i2c/devices/i2c-7/new_device",
"echo lm75 0x49 > /sys/bus/i2c/devices/i2c-8/new_device",
"echo lm75 0x4a > /sys/bus/i2c/devices/i2c-9/new_device",
"echo lm75 0x4b > /sys/bus/i2c/devices/i2c-9/new_device",
"echo as5822_54x_psu1 0x50 > /sys/bus/i2c/devices/i2c-3/new_device",
"echo ym2401 0x58 > /sys/bus/i2c/devices/i2c-3/new_device",
"echo as5822_54x_psu2 0x51 > /sys/bus/i2c/devices/i2c-4/new_device",
"echo ym2401 0x59 > /sys/bus/i2c/devices/i2c-4/new_device",
"echo as5822_54x_cpld1 0x60 > /sys/bus/i2c/devices/i2c-6/new_device",
"echo as5822_54x_cpld2 0x61 > /sys/bus/i2c/devices/i2c-10/new_device",
"echo as5822_54x_cpld3 0x62 > /sys/bus/i2c/devices/i2c-11/new_device"]

mknod2 =[
"echo pca9548 0x72 > /sys/bus/i2c/devices/i2c-0/new_device",
"echo pca9548 0x71 > /sys/bus/i2c/devices/i2c-1/new_device" ,
"echo pca9548 0x71 > /sys/bus/i2c/devices/i2c-12/new_device" ,
"echo pca9548 0x72 > /sys/bus/i2c/devices/i2c-13/new_device" ,
"echo pca9548 0x73 > /sys/bus/i2c/devices/i2c-14/new_device",
"echo pca9548 0x74 > /sys/bus/i2c/devices/i2c-15/new_device",
"echo pca9548 0x75 > /sys/bus/i2c/devices/i2c-16/new_device",
"echo pca9548 0x76 > /sys/bus/i2c/devices/i2c-17/new_device",
"echo pca9548 0x71 > /sys/bus/i2c/devices/i2c-17/new_device",
#"echo pca9548 0x75 > /sys/bus/i2c/devices/i2c-38/new_device",
#"echo pca9548 0x76 > /sys/bus/i2c/devices/i2c-39/new_device",
"echo 24c02 0x57 > /sys/bus/i2c/devices/i2c-0/new_device",

#"*echo as5822_54x_fan 0x63 > /sys/bus/i2c/devices/i2c-3/new_device",
"echo lm75 0x48 > /sys/bus/i2c/devices/i2c-7/new_device",
"echo lm75 0x49 > /sys/bus/i2c/devices/i2c-8/new_device",
"echo lm75 0x4a > /sys/bus/i2c/devices/i2c-9/new_device",
"echo lm75 0x4b > /sys/bus/i2c/devices/i2c-9/new_device",
"echo as5822_54x_psu1 0x50 > /sys/bus/i2c/devices/i2c-3/new_device",
"echo ym2401 0x58 > /sys/bus/i2c/devices/i2c-3/new_device",
"echo as5822_54x_psu2 0x51 > /sys/bus/i2c/devices/i2c-4/new_device",
"echo ym2401 0x59 > /sys/bus/i2c/devices/i2c-4/new_device",
"echo as5822_54x_cpld1 0x60 > /sys/bus/i2c/devices/i2c-6/new_device",
"echo as5822_54x_cpld2 0x61 > /sys/bus/i2c/devices/i2c-10/new_device",
"echo as5822_54x_cpld3 0x62 > /sys/bus/i2c/devices/i2c-11/new_device"]



if DEBUG == True:
    print(sys.argv[0])
    print("ARGV      :", sys.argv[1:])


def main():
    global DEBUG
    global args
    global FORCE

    if len(sys.argv)<2:
        show_help()

    options, args = getopt.getopt(sys.argv[1:], "hdf", ["help",
                                                       "debug",
                                                       "force",
                                                          ])
    if DEBUG == True:
        print(options)
        print(args)
        print(len(sys.argv))

    for opt, arg in options:
        if opt in ("-h", "--help"):
            show_help()
        elif opt in ("-d", "--debug"):
            DEBUG = True
            logging.basicConfig(level=logging.INFO)
        elif opt in ("-f", "--force"):
            FORCE = 1
        else:
            logging.info("no option")
    for arg in args:
        if arg == "install":
           do_install()
        elif arg == "clean":
           do_uninstall()
        elif arg == "api":
           do_sonic_platform_install()
        elif arg == "api_clean":   
           do_sonic_platform_clean()
        
        else:
            show_help()

    return 0


def show_help():
    print(__doc__ % {"scriptName" : sys.argv[0].split("/")[-1]})
    sys.exit(0)


def my_log(txt:str):
    if DEBUG == True:
        print("[Debug]" + txt)
    return


def log_os_system(cmd:str, show:bool):
    logging.info("Run :" + cmd)
    status, output = subprocess.getstatusoutput(cmd)
    my_log (cmd +"with result:" + str(status))
    my_log ("      output:" + output)
    if status:
        logging.info("Failed :" + cmd)
        if show:
            print("Failed :" + cmd)
    return status, output


def driver_check():
    ret, lsmod = log_os_system("ls /sys/module/*accton*", 0)
    logging.info("mods:" + lsmod)
    if ret :
        return False
    else :
        return True


def driver_install():
    global FORCE
    log_os_system("depmod", 1)
    for i in range(0,len(kos)):
        ret = log_os_system(kos[i], 1)
        if ret[0]:
            if FORCE == 0:
                return ret[0]
    print("Done driver_install")

    return 0


def driver_uninstall():
    global FORCE
    for i in range(0,len(kos)):
        rm = kos[-(i+1)].replace("modprobe", "modprobe -rq")
        rm = rm.replace("insmod", "rmmod")
        lst = rm.split(" ")
        if len(lst) > 3:
            del(lst[3])
        rm = " ".join(lst)
        ret = log_os_system(rm, 1)
        if ret[0]:
            if FORCE == 0:
                return ret[0]
    return 0


def i2c_order_check():
    # i2c bus 0 and 1 might be installed in different order.
    # Here check if 0x72 is exist @ i2c-1
    tmp = "i2cget -y -f 0 0x72"
    ret = log_os_system(tmp, 0)
    if not ret[0]:
        order = 1
    else:
        order = 0
    return order


def device_install():
    global FORCE

    order = i2c_order_check()

    # if 0x77 is not exist @i2c-1, use reversed bus order
    if order:
        for i in range(0,len(mknod2)):
            #for pca954x need times to built new i2c buses
            if mknod2[i].find("pca954") != -1:
               time.sleep(1)

            status, output = log_os_system(mknod2[i], 1)
            time.sleep(0.01)
            if status:
                print(output)
                if FORCE == 0:
                    return status
    else:
        for i in range(0,len(mknod)):
            #for pca954x need times to built new i2c buses
            if mknod[i].find("pca954") != -1:
               time.sleep(1)

            status, output = log_os_system(mknod[i], 1)
            if status:
                print(output)
                if FORCE == 0:
                    return status

    # set all pca954x idle_disconnect
    cmd = "echo -2 | tee /sys/bus/i2c/drivers/pca954x/*-00*/idle_state"
    status, output = log_os_system(cmd, 1)
    if status:
        print(output)
        if FORCE == 0:
            return status

    for i in range(49, 55): #Set qsfp port to normal state
        log_os_system("echo 0 > /sys/bus/i2c/devices/11-0062/module_reset_" + str(i), 1)
    for i in range(1, 39): #Set disable tx_disable to sfp port
        log_os_system("echo 0 > /sys/bus/i2c/devices/10-0061/module_tx_disable_" + str(i),
                      1)
    for i in range(39, 49): #Set disable tx_disable to sfp port
        log_os_system("echo 0 > /sys/bus/i2c/devices/11-0062/module_tx_disable_" + str(i),
                      1)

    for i in range(0,len(sfp_map)):
        if i < qsfp_start:
            status, output =log_os_system("echo optoe2 0x50 > /sys/bus/i2c/devices/i2c-" +
                                          str(sfp_map[i]) + "/new_device",
                                          1)
        else:
            status, output =log_os_system("echo optoe1 0x50 > /sys/bus/i2c/devices/i2c-" +
                                          str(sfp_map[i]) + "/new_device",
                                          1)
        if status:
            print(output)
            if FORCE == 0:
                return status
    print("Done device_install")

    return


def device_uninstall():
    global FORCE

    for i in range(0,len(sfp_map)):
        target = "/sys/bus/i2c/devices/i2c-" + str(sfp_map[i]) + "/delete_device"
        status, output =log_os_system("echo 0x50 > " + target, 1)
        if status:
            print(output)
            if FORCE == 0:
                return status

    order = i2c_order_check()
    if order:
        nodelist = mknod2
    else:
        nodelist = mknod

    for i in range(len(nodelist)):
        target = nodelist[-(i + 1)]
        temp = target.split()
        del temp[1]
        temp[-1] = temp[-1].replace("new_device", "delete_device")
        status, output = log_os_system(" ".join(temp), 1)
        if status:
            print(output)
            if FORCE == 0:
                return status

    return


def system_ready():
    if driver_check() == False:
        return False
    if not device_exist():
        return False
    return True


def do_sonic_platform_install():
    device_path = f"{PLATFORM_ROOT_PATH}/x86_64-accton_{PROJECT_NAME}-r0"
    SONIC_PLATFORM_BSP_WHL_PKG_PY3 = "/".join([device_path, PLATFORM_API2_WHL_FILE_PY3])

    #Check API2.0 on py whl file
    status, output = log_os_system("pip3 show sonic-platform > /dev/null 2>&1", 0)
    if status:
        if os.path.exists(SONIC_PLATFORM_BSP_WHL_PKG_PY3): 
            status, output = log_os_system("pip3 install " + 
                                           SONIC_PLATFORM_BSP_WHL_PKG_PY3,
                                           1)
            if status:
                print(f"Error: Failed to install {PLATFORM_API2_WHL_FILE_PY3}" )
                return status
            else:
                print(f"Successfully installed {PLATFORM_API2_WHL_FILE_PY3} package")
        else:
            print(f"{PLATFORM_API2_WHL_FILE_PY3} is not found")
    else:        
        print(f"{PLATFORM_API2_WHL_FILE_PY3} has installed")

    return 


def do_sonic_platform_clean():
    status, output = log_os_system("pip3 show sonic-platform > /dev/null 2>&1", 0)   
    if status:
        print(f"{PLATFORM_API2_WHL_FILE_PY3} does not install, not need to uninstall")

    else:        
        status, output = log_os_system("pip3 uninstall sonic-platform -y", 0)
        if status:
            print(f"Error: Failed to uninstall {PLATFORM_API2_WHL_FILE_PY3}")
            return status
        else:
            print("{PLATFORM_API2_WHL_FILE_PY3} is uninstalled")


def do_install():
    print("Checking system....")
    if driver_check() == False:
        print("No driver, installing....")
        status = driver_install()
        if status:
            if FORCE == 0:
                return  status
    else:
        print(PROJECT_NAME.upper()+" drivers detected....")
    if not device_exist():
        print("No device, installing....")
        status = device_install()
        if status:
            if FORCE == 0:
                return  status
    else:
        print(PROJECT_NAME.upper()+" devices detected....")

    do_sonic_platform_install()

    return


def do_uninstall():
    print("Checking system....")
    if not device_exist():
        print(PROJECT_NAME.upper() +" has no device installed....")
    else:
        print("Removing device....")
        status = device_uninstall()
        if status:
            if FORCE == 0:
                return  status

    if driver_check()== False :
        print(PROJECT_NAME.upper() +" has no driver installed....")
    else:
        print("Removing installed driver....")
        status = driver_uninstall()
        if status:
            if FORCE == 0:
                return  status

    do_sonic_platform_clean()

    return


def device_exist():
    ret1 = log_os_system("ls "+i2c_prefix+"*0077", 0)
    ret2 = log_os_system("ls "+i2c_prefix+"i2c-12", 0)
    return not(ret1[0] or ret2[0])


if __name__ == "__main__":
    main()
