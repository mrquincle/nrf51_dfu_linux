
Python nrf51822 Batch DFU OTA uploader
======================================

## How to use:

After installing the prerequisites, run scan.py as root (it uses hcitool, which needs root access). You can click on the adresses in the scan list
to move them to the OTA list. To remove you can click on them in the OTA list. This fills the ota_macs.config.

```
sudo python scan.py
```

With a configured ota_macs.config, run

```
python otaBatch.py -f 'path to hex file'
```

to update all the selected MAC adresses one by one automatically.

## Prerequisite:

Prior to running, install:

Python 2.7
pygame
Pexpect
Intelhex

```
sudo apt-get install python-pygame python-pip
sudo pip install pexpect
sudo pip install intelhex --allow-unverified intelhex
```

Bluez (tested on 5.21): 
From (http://stackoverflow.com/questions/24853597/ble-gatttool-cannot-connect-even-though-device-is-discoverable-with-hcitool-lesc)

Remove the Bluez installation and perform an update:

```
sudo apt-get --purge remove bluez
sudo apt-get update
```
Make sure you have the necessary libs:
```
sudo apt-get install libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev
```

Download and extract the newest Bluez version (at the time it's 5.21):
```
sudo wget https://www.kernel.org/pub/linux/bluetooth/bluez-5.21.tar.xz
sudo tar xvf bluez-5.21.tar.xz
```
Go to the Bluez folder, configure and install (The "sudo make" line takes some time to process):

```
cd bluez-5.21
sudo ./configure --disable-systemd
sudo make
sudo make install
sudo cp attrib/gatttool /usr/bin/
```

Python nrf51822 DFU uploader
============================

Wrapper for bluez gatttool using pexpect to achive DFU 
uploads to the nrf51822 (SDK 5.1.0 and S110 SoftDevice 6.0.0). 

The script does not handle any notifications given by the 
peer as it is strictly not needed for simple uploads.

Inspired by the gatttool wrapping solution by Michael 
Saunby (https://github.com/msaunby/ble-sensor-pi).

## System:

* Linux Mint 16 - kernel 3.11.0-12-generic (Ubuntu works as well)
* bluez - 4.101-0ubuntu8b1

## Prerequisite:

Prior to running, install:
 
    sudo pip install pexpect
    sudo pip install intelhex --allow-unverified intelhex

## Usage:

You'll need the .hex file (not the .bin file) to upload. Use objcopy to create it if you don't have it. Then run:

    python dfu.py -f <hex_file> -a <address>

To figure out the address of DfuTarg do a hcitool lescan:

    $ sudo hcitool -i hci0 lescan
    LE Scan ... 
    CD:E3:4A:47:1C:E4 DfuTarg
    CD:E3:4A:47:1C:E4 (unknown)

Copyrights:

Fork from: https://bitbucket.org/glennrub/nrf51_dfu_linux


