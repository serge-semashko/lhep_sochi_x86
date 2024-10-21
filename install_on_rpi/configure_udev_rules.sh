#!/bin/bash


function set_udev_rules() {

    rules_path=/etc/udev/rules.d/arducam-usb.rules

    rules_content='SUBSYSTEM=="usb",ENV{DEVTYPE}=="usb_device",ATTRS{idVendor}=="52cb",MODE="0666"\nSUBSYSTEM=="usb",ENV{DEVTYPE}=="usb_device",ATTRS{idVendor}=="04b4",MODE="0666"'

    echo -e $rules_content | sudo tee $rules_path
    sudo udevadm control --reload-rules && sudo udevadm trigger
    echo "udev rules set successfully!"
}

set_udev_rules
