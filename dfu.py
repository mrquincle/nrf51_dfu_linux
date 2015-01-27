#!/usr/bin/env python

import os, re
import pexpect
import optparse
import time
from intelhex import IntelHex

# DFU Opcodes
class Commands:
    START_DFU = 1
    INITIALIZE_DFU = 2
    RECEIVE_FIRMWARE_IMAGE = 3
    VALIDATE_FIRMWARE_IMAGE = 4
    ACTIVATE_FIRMWARE_AND_RESET = 5
    SYSTEM_RESET = 6

# different CHUNK_SIZE does not work somehow
# CHUNK_SIZE = 15
CHUNK_SIZE = 20

def convert_uint32_to_array(value):
    """ Convert a number into an array of 4 bytes (LSB). """
    return [
        (value >> 0 & 0xFF),
        (value >> 8 & 0xFF),
        (value >> 16 & 0xFF),
        (value >> 24 & 0xFF)
    ]

def convert_uint16_to_array(value):
    """ Convert a number into an array of 2 bytes (LSB). """
    return [
        (value >> 0 & 0xFF),
        (value >> 8 & 0xFF)
    ]

def convert_array_to_hex_string(arr):
    hex_str = ""
    for val in arr:
        if val > 255:
            raise Exception("Value is greater than it is possible to represent with one byte")
        hex_str += "%02x" % val
    return hex_str


class BleDfuUploader(object):
    # for S130
    #ctrlpt_handle = 0x10
    #ctrlpt_cccd_handle = 0x11
    #data_handle = 0x0E

    # for S110
    ctrlpt_handle = 0x0D
    ctrlpt_cccd_handle = 0x0E
    data_handle = 0x0B

    def __init__(self, target_mac, hexfile_path):
        self.hexfile_path = hexfile_path
        self.target_mac = target_mac
        # print "gatttool -b '%s' -t random --interactive" % target_mac
        self.ble_conn = pexpect.spawn("gatttool -b '%s' -t random --interactive" % target_mac)

    # Connect to peer device.
    def scan_and_connect(self):
        # print "Wait for scan result and connect"
        try:
            self.ble_conn.expect('\[LE\]>', timeout=10)
        except pexpect.TIMEOUT, e:
            print "timeout on scan for target"
            return False

        # print "Send: connect"
        self.ble_conn.sendline('connect')

        try:
            res = self.ble_conn.expect(['successful'], timeout=10)
        except pexpect.TIMEOUT, e:
            print "timeout on connect to target"
            return False

        print 'Connected.'
        return True

    def _dfu_toggle_mode(self):
        found_characteristic = True
        already_in_DFU = False

        #look for DFU switch characteristic
        self.ble_conn.sendline('characteristics')
        try:
            res = self.ble_conn.expect(['f5f90005-59f9-11e4-aa15-123b93f75cba'], timeout=5)
            resetHandle = self.ble_conn.before
        except pexpect.TIMEOUT, e:
            found_characteristic = False

        if not found_characteristic:
            # maybe it already is IN DFU mode
            self.ble_conn.sendline('characteristics')
            try:
                res = self.ble_conn.expect(['00001531-1212-efde-1523-785feabcd123'], timeout=5)
                already_in_DFU = True
            except pexpect.TIMEOUT, e:
                print "Not in DFU, nor has the toggle characteristic, aborting.."
                return False

        if found_characteristic or already_in_DFU:
            if not already_in_DFU:
                print "Switching device into DFU mode"
                handles = re.findall(r"char value handle: 0x..(..)", resetHandle)
                self.ble_conn.sendline('char-write-req 0x%02s %02x' % (handles[-1], 1))
                try:
                    res = self.ble_conn.expect('Characteristic value was written successfully', timeout=10)
                except pexpect.TIMEOUT, e:
                    print "timeout toggling to DFU mode"
                    return False

                print "Node is being restarted"
                self.ble_conn.sendline('exit')
                time.sleep(0.5)
                self.ble_conn.kill(0)

                time.sleep(5)
                print "Reconnecting"
                self.__init__(self.target_mac, self.hexfile_path)
                return self.scan_and_connect()
            else:
                print "Node already in DFU mode"
            return True
        else:

            return False


    def _dfu_state_set(self, opcode):
        # print "Send: char-write-req 0x%02x %02x" % (self.ctrlpt_handle, opcode)
        self.ble_conn.sendline('char-write-req 0x%02x %02x' % (self.ctrlpt_handle, opcode))        

        # Verify that command was successfully written
        try:
            res = self.ble_conn.expect('Characteristic value was written successfully', timeout=10)
        except pexpect.TIMEOUT, e:
            print "timeout on dfu state set"
            return False
        return True

    def _dfu_data_send(self, data_arr):
        hex_str = convert_array_to_hex_string(data_arr)

        self.ble_conn.sendline('char-write-req 0x%02x %s' % (self.data_handle, hex_str))

        # Verify that data was successfully written
        try:
            res = self.ble_conn.expect('Characteristic value was written successfully', timeout=4)
        except pexpect.TIMEOUT, e:
            print "timeout data send",e

    def _dfu_enable_cccd(self):
        cccd_enable_value_array_lsb = convert_uint16_to_array(0x0001)
        cccd_enable_value_hex_string = convert_array_to_hex_string(cccd_enable_value_array_lsb) 
        # print "Send: char-write-req 0x%02x %s" % (self.ctrlpt_cccd_handle, cccd_enable_value_hex_string)
        self.ble_conn.sendline('char-write-req 0x%02x %s' % (self.ctrlpt_cccd_handle, cccd_enable_value_hex_string))        

        # Verify that CCCD was successfully written
        try:
            res = self.ble_conn.expect('Characteristic value was written successfully', timeout=10)
        except pexpect.TIMEOUT, e:
            print "timeout on writing cccd to Characteristic",e
            return False

        # print "CCCD written"
        return True

    # Transmit the hex image to peer device.
    def dfu_send_image(self):
        # scan for characteristics:
        status = self._dfu_toggle_mode()

        if not status:
            return False

        # Enable Notifications - Setting the DFU Control Point CCCD to 0x0001
        status = self._dfu_enable_cccd()

        if not status:
            return False

        # Open the hex file to be sent
        ih = IntelHex(self.hexfile_path)
        bin_array = ih.tobinarray()

        hex_size = len(bin_array)
        # print "Hex file size: ", hex_size

        # Sending 'START DFU' Command
        self._dfu_state_set(Commands.START_DFU)

        # Transmit image size
        hex_size_array_lsb = convert_uint32_to_array(len(bin_array))
        self._dfu_data_send(hex_size_array_lsb)
        # print "Sending hex file size"

        # Send 'RECEIVE FIRMWARE IMAGE' command to set DFU in firmware receive state.
        self._dfu_state_set(Commands.RECEIVE_FIRMWARE_IMAGE)

        print "Start sending data"
        # Send hex file data packets
        timeStart = time.time()
        chunk = 1
        self.ble_conn.delaybeforesend = 0.0
        for i in range(0, hex_size, CHUNK_SIZE):
            data_to_send = bin_array[i:i + CHUNK_SIZE]
            self._dfu_data_send(data_to_send)

            if chunk % 100 == 0:
                print "Chunk #", chunk, "/" ,  hex_size / CHUNK_SIZE

            chunk += 1
        print "Firmware transferred in ", time.time() - timeStart
        self.ble_conn.delaybeforesend = 0.05

        time.sleep(1)

        # Send Validate Command
        print "Validating..."
        status = self._dfu_state_set(Commands.VALIDATE_FIRMWARE_IMAGE)

        if not status:
            print "Could not validate firmware."
            return False

        # Wait a bit for copy on the peer to be finished
        time.sleep(3)

        # Send Activate and Reset Command
        status = self._dfu_state_set(Commands.ACTIVATE_FIRMWARE_AND_RESET)
        if not status:
            print "Could not activate."
            return False

        print "Validated. Rebooting application."
        return True


    # Disconnect from peer device if not done already and clean up.
    def disconnect(self):
        self.ble_conn.sendline('exit')
        self.ble_conn.close()


if __name__ == '__main__':
    try:
        parser = optparse.OptionParser(usage='%prog -f <hex_file> -a <dfu_target_address>\n\nExample:\n\tdfu.py -f blinky.hex -a cd:e3:4a:47:1c:e4',
                                       version='0.1')

        parser.add_option('-a', '--address',
                  action='store',
                  dest="address",
                  type="string",
                  default=None,
                  help='DFU target address. (Can be found by running "hcitool lescan")'
                  )
        parser.add_option('-f', '--file',
                  action='store',
                  dest="hex_file",
                  type="string",
                  default=None,
                  help='Hex file to be uploaded.'
                  )

        options, args = parser.parse_args()

    except Exception, e:
        print e
        print "For help use --help"
        sys.exit(2)

    if (not options.hex_file) or (not options.address):
        parser.print_help()
        exit(2)

    if not os.path.isfile(options.hex_file):
        print "Error: Hex file not found!"
        exit(2)

    ble_dfu = BleDfuUploader(options.address.upper(), options.hex_file)

    # Connect to peer device.
    ble_dfu.scan_and_connect()

    # Transmit the hex image to peer device.
    ble_dfu.dfu_send_image()

    # wait a second to be able to recieve the disconnect event from peer device.
    time.sleep(1)

    # Disconnect from peer device if not done already and clean up.
    ble_dfu.disconnect()
