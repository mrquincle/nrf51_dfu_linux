__author__ = 'alex'
import pexpect
import time
import threading
import commands

# this is a fake file handler because the logging of pexpect needs a file or sys.stdout
class dummyfile(object):

    def __init__(self):
        self.list = []
        self.itemCounter = 0

    def write(self,argument):
        # we ignore the very first entry because this is a scanning notification, not a MAC address
        if self.itemCounter > 0:
            self.list.append(argument)
        else:
            if 'permitted' in argument:
                print argument, "Try using sudo python scan.py"
        self.itemCounter += 1

    def flush(self):
        pass

    # reset the list
    def clearList(self):
        self.list = []

# this thread starts the scanning using hcitool lescan.
# It allows the results to be read out asynchronously
class scanner(threading.Thread):

    # init vars
    def __init__(self):
        self.dummyFile = dummyfile();
        self.uniqueIdList = []
        self.timeoutThreshold = 10
        self.startedScanning = False;
        threading.Thread.__init__(self)

    # called on start() of a thread
    def run(self):
        self.init()
        self.scan()

    # reset the hcitool, we assume hci0 is the required device
    def init(self):
        commands.getoutput("hcitool dev")
        commands.getoutput('hciconfig hci0 down')
        commands.getoutput('hciconfig hci0 up')
        commands.getoutput("hcitool dev")
        commands.getoutput('killall hcitool')

    # run the hcitool scan for 200 seconds
    def scan(self):
        self.startedScanning = True;
        self.child = pexpect.run("hcitool lescan", timeout=200, logfile=self.dummyFile)

    # get the list asynchronously
    def get(self):
        if self.startedScanning == True:
            # process data
            content = self.dummyFile.list;
            self.uniqueIdList = self.process(content);

            #clear the temporary file
            self.dummyFile.clearList();
        return self.uniqueIdList

    # only put unique entrees in the list, also apply the timeout
    def process(self,content):
        for entree in content:
            data = entree.split(" ");
            exists = self.valueExists(data[0])
            if exists == -1:
                self.uniqueIdList.append({'mac': data[0], 'name': data[1].replace("\r\n",""), 'timestamp': time.time()})
            else:
                self.uniqueIdList[exists]['timestamp'] = time.time()
                if data[1] != "(unknown)\r\n":
                    self.uniqueIdList[exists]['name'] = data[1].replace("\r\n","")

        # remove old nodes from list
        updatedList = []
        for entree in self.uniqueIdList:
            if time.time() - entree['timestamp'] < self.timeoutThreshold:
                updatedList.append(entree)

        return updatedList;

    # check if a MAC address exists in the uniqueIdList
    def valueExists(self, referenceValue):
        for idx,value in enumerate(self.uniqueIdList):
            if value['mac'] == referenceValue:
                self.uniqueIdList[idx]
                return idx
        return -1
