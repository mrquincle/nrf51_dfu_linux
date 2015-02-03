#!/usr/bin/python

from lib.scanner import *
from lib.interface import *
import sys,getopt,os

global configContent;

# read the config file
def readConfig():
    configContent = []
    if not os.path.exists("ota_macs.config"):
        return configContent
    f = open("ota_macs.config",'r')
    content = f.read()
    lines = content.split("\r\n");
    for line in lines:
        if line != '':
            data = line.split(",")
            configContent.append({'mac':data[0], 'name':data[1]})
    f.close();
    return configContent

# update the config file with the configContent
def updateFile():
    global configContent;
    f = open("ota_macs.config",'w')
    for config in configContent:
        f.write(config['mac'] + "," + config['name'] + "\r\n")
    f.close();

# check if a MAC address exists in the datasource
def alreadyIn(MACaddress, datasource):
    for config in datasource:
        if config['mac'] == MACaddress:
            return True
    return False

# Add a MAC address and name to the config file
def addToConfig(MACaddress,name):
    global configContent;
    if alreadyIn(MACaddress, configContent) == False:
        configContent.append({'mac':MACaddress, 'name':name})

# Remove a MAC address entree from the config file
def removeFromConfig(MACaddress):
    global configContent;
    newConfig = []
    for config in configContent:
        if config['mac'] != MACaddress:
            newConfig.append(config)
    configContent = newConfig

def updateInConfig(MACaddress,name):
    global configContent;
    updated = False
    if name != "(unknown)":
        for index,config in enumerate(configContent):
            if config['mac'] == MACaddress:
                updated = True
                configContent[index]['name'] = name

    if updated:
        updateFile()


# this inherits from a GUI interface
class gui(interface):

    # init, call super init too
    def initGUI(self):
        interface.initGUI(self)

    # create the GUI elements visible on screen
    def createGUIElements(self):

        # get the nodes found by the scanner
        availableNodes = scanner.get();

        # set the background and write the headers
        self.screen.fill((20,20,20))
        self.writetext("Scanning: ", 6,10,10);
        self.writetext("OTA list: ", 6,300,10);

        # write the available node list.
        for i,value in enumerate(availableNodes):
            # update name in file if it is not unknown
            updateInConfig(value['mac'], value['name'])

            self.writetext(value['mac'] + ' ' + value['name'],4,10,30 + 20*i,False,False,self.getColor(value['mac'],False,configContent))
            # screenspace is a rectangle to which a callback can be bound when clicked on.
            self.screenspace['scanning__' + value['mac'] + '_' + value['name']] = ((10,25 + 20*i),(280,45 + 20*i))

        # write the OTA node list.
        for i,value in enumerate(configContent):
            self.writetext(value['mac'] + ' ' + value['name'],4,300,30 + 20*i,False,False,self.getColor(value['mac'],True,availableNodes))
            self.screenspace['otalist__' + value['mac'] + '_' + value['name']] = ((300,25 + 20*i),(600,45 + 20*i))

    # this handles the screenspace events
    def handleEvent(self,key):
        if 'scanning__' in key:
            data = key.split("__")
            keyData = data[1].split("_")
            addToConfig(keyData[0],keyData[1])
            updateFile()
        elif 'otalist__' in key:
            data = key.split("__")
            keyData = data[1].split("_")
            removeFromConfig(keyData[0])
            updateFile()

        # call super handle
        interface.handleEvent(self,key)

    # get a color for the text depending if it is present in a defined list
    def getColor(self,MACaddress, list, datasource):
        if list == True:
            if alreadyIn(MACaddress, datasource):
                return (0,255,0)
            else:
                return (165,195,255)
        else:
            if alreadyIn(MACaddress, datasource):
                return (0,255,0)
            else:
                return (200,200,200)


# when run
def main(argv):
    interface = "hci0"
    try:
      opts, args = getopt.getopt(argv,"hi:",["interface="])
    except getopt.GetoptError:
      print 'scan.py -i <hci device>'
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print 'scan.py -i <hci device>'
         sys.exit()
      elif opt in ("-i", "--interface"):
         interface = arg

    print "Use interface", interface
    
    # start the thread that scans the ble devices (using hcitool lescan)
    scanner.setInterface(interface)
    scanner.setDaemon(True)
    scanner.start()

    # read the config file
    global configContent
    configContent = readConfig()

    # create, init and run the gui interface
    theGui = gui()
    theGui.initGUI()
    theGui.run()

if __name__ == '__main__':
    scanner = scanner()
    main(sys.argv[1:]);

