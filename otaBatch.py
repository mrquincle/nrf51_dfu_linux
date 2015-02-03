__author__ = 'alex'

import sys, optparse
from dfu import *
from scan import readConfig
from lib.scanner import resetHCI

if __name__ == '__main__':
    try:
        parser = optparse.OptionParser(usage='%prog -f <hex_file> \n\nExample:\n\tpython otaBatch.py -f blinky.hex -i hciX',
                                       version='0.1')

        parser.add_option('-f', '--file',
                          action='store',
                          dest="hex_file",
                          type="string",
                          default=None,
                          help='Hex file to be uploaded.'
        )
        parser.add_option('-i', '--interface',
                  action='store',
                  dest="interface",
                  type="string",
                  default="hci0",
                  help='HCI interface to be used.'
        )

        options, args = parser.parse_args()

    except Exception, e:
        print e
        print "For help use --help"
        sys.exit(2)

    # read the config file to obtain mac adresses
    configContent = readConfig()
    resetHCI()

    if (not options.hex_file):
        parser.print_help()
        exit(2)

    if not os.path.isfile(options.hex_file):
        print "Error: Hex file not found!"
        exit(2)

    # if we have mac adresses
    if len(configContent) > 0:
        for entree in configContent:
            timeStart = time.time()
            print 'Attempting ' + entree['mac'] + " (" + entree['name'] + ")"
            ble_dfu = BleDfuUploader(entree['mac'].upper(), options.hex_file, options.interface)

            # Connect to peer device.
            status = ble_dfu.scan_and_connect()

            if status:
                # Transmit the hex image to peer device.
                status = ble_dfu.dfu_send_image()
                if status:
                    # wait a second to be able to recieve the disconnect event from peer device.
                    time.sleep(1)

                    # Disconnect from peer device if not done already and clean up.
                    ble_dfu.disconnect()
                else:
                    print "Firmware could not be updated."
            else:
                print "Could not connect.. Aborting. Is node " + entree['mac'] + " still online?"
            print "Node process took:", time.time() - timeStart
    else:
        print "No MAC addresses supplied."
        print "Add them manually to the ota_macs.config file or run:"
        print "\tsudo python scan.py to populate the list."
