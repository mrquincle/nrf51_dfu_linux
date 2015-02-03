Python nrf51822 Batch DFU OTA uploader
======================================

## How to use:

After installing the prerequisites, run `scan.py` as root (it uses hcitool, which needs root access). You can click on 
the adresses in the scan list to move them to the OTA list. To remove you can click on them in the OTA list. This 
fills the `ota_macs.config` file. This also sets a device in DFU mode if it is not it already.
The software relies on the modified nordic bootloader on the target device. If the target device is in application mode
it only knows how to use the `Crownstone` firmware characteristic to put it into DFU mode.

```
sudo python scan.py
```

or, alternatively `sudo ./scan.py`.

With a configured `ota_macs.config`, run:

```
sudo python otaBatch.py -f 'path to hex file'
```

to update all the selected MAC adresses one by one automatically. Here `sudo` is required because we use `hcitools` 
beforehand. To do this manually, you can call

```
sudo python reset.py
```

If you have for example a separate Bluetooth Low-Energy dongle, you can use another hci device. Use `hciconfig` to
find out which device you need (by plugging out and plugging in).

Then all above scripts have an interface option, for example:

    ./scan.py -i hci1

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

### Optionally

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

Note: The above is not necessary on my system, perhaps this is because I follow <https://dobots.nl/2014/07/23/linux-and-ble/>,
especially:

    sudo hcitool -i hci1 lecc --random CF:72:4E:70:A6:DB

This gives me a proper connection handle. If I do not do this I cannot connect to the device.

## Todo

Make process less dependent on the interactive output of `gatttool`. The non-interactive mode is basically only
documented by `gatttool --help-all`, but it is probably wise to use. Interactive output can be different over versions.

There are several ways to approach this:

* First search a proper tool with pipe semantics. Such tools would not change their output format between versions.
* If this does not exist, check if there is a tool that implements services and characteristics as Unix files. To `echo` or `cat` something to a file descriptor removes a lot of the `(p)expect` ad hocery.
* Adjust the current `expect` routines so that they at least do not use the interactive mode of `gatttool`.
* Adapt `gatttool` itself to properly list and write characteristics.

# Copyrights

Originally from "glennrub" at <https://bitbucket.org/glennrub/nrf51_dfu_linux/> who was on his turn inspired by 
Michael Saunby <https://github.com/msaunby/ble-sensor-pi>.

Copyrights should be obtained from: <https://bitbucket.org/glennrub/nrf51_dfu_linux>. Adaptations are property of
DoBots (<https://dobots.nl>) and Almende B.V. (<http://almende.com>).


