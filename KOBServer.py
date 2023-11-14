#!/usr/bin/env python3

"""KOBServer.py

MorseKOB server.

Command line parameters:
    webroot - path for web root directory
    port - port for server to listen on (default: 7890)

Whenever a station connects or disconnects, the program updates an activity
web page, index.html, in the root directory. It also maintains a log file,
log.html, in the <webroot>/logs subdirectory.

Usage examples:
    python KOBServer.py /var/www
    python KOBServer.py C:/www 7891

History:
6.1.0  added private wire feature
"""

from __future__ import print_function  # for Python 2.7 compatibility
import sys
import socket
import struct
import threading
import time
from pins import pins  # dictionary mapping wire nos. to PIN codes

# constants
VERSION = '6.1.0'
PORT = 7890
TIMEOUT = 90.0  # to accommodate NewsBot's 30 second heartbeat timer
NEWSBOTIP = '70.167.219.231'

# command codes
DIS = 2  # Disconnect
DAT = 3  # Code or ID
CON = 4  # Connect
ACK = 5  # Ack

# packet formats
longRecord = struct.Struct('<H2x 128s 20x 204x I 128s 8x')
shortRecord = struct.Struct('<HH')
ackRecord = struct.Struct('<H')

# get parameters
nargs = len(sys.argv)
webroot = sys.argv[1]
port = int(sys.argv[2]) if nargs > 2 else 7890

# station class
class Station:
    def __init__(self, stnAddr):
        self.addr = stnAddr  # remote IP address + port no.
        self.wire = 0  # current wire no.
        self.id = ''  # station ID
        self.pin = ''  # PIN code
        self.version = ''  # version of client software
        self.time = time.time()  # time last heard from

    def updateWireNo(self, wireNo):
        global statusChanged
        if self.wire != wireNo:
            self.wire = wireNo
            if self.version:
                log('Chan\t' + stationString(self))
                statusChanged = True

    def updateIDPINandVersion(self, stnID, stnPIN, stnVersion):
        global statusChanged
        if self.id != stnID:
            self.id = stnID
            if self.version:
                log('Idnt\t' + stationString(self))
                statusChanged = True
        self.pin = stnPIN
        if stnVersion and self.version != stnVersion:
            self.version = stnVersion
            log('Conn\t' + stationString(self))
            statusChanged = True

# look up a station in the station list
def findStation(stnAddr):
    if stnAddr not in stations:
        stations[stnAddr] = Station(stnAddr)
    return stations[stnAddr]

# periodically purge stations that have timed out and post changes
def updateStationList():
    global statusChanged
    while True:
        for stn in list(stations.values()):
            if time.time() - stn.time > TIMEOUT:
                del stations[stn.addr]
                log('Time\t' + stationString(stn))
                statusChanged = True
                break
        updateWebPage()
        time.sleep(1.0)  # update again after one second

# format station data as a string
def stationString(stn):
    ip, port = stn.addr
    return '{}\t{}:{}\t{}\t{}'.format(stn.wire, ip, port, stn.version, stn.id)

# post a new web page if station status has changed

HTMLHEAD = '''\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN">
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=ISO-8859-1">
<meta http-equiv="pragma" content="no-cache">
<meta http-equiv="refresh" content="30">
<title>KOBServer</title>
</head>
<body style="background-color:white; color:black; text-align:center; font:80% sans-serif">
<p style="font-family:times new roman, serif; font-size:200%; font-weight:bold">K O B S<span style="font-size:80%"> E R V E R</span></p>
<table cellspacing="1" border="2" cellpadding="4" align="center">
<tr style="font-weight:bold"><td>Wire</td><td>ID</td></tr>
'''

HTMLEND = '''\
</table>
<p style="">[&nbsp;<a href="info.html">Server&nbsp;Info</a>&nbsp;]</p>
</body>
</html>
'''

def updateWebPage():
    global statusChanged
    if statusChanged:
        statusChanged = False
        activityPage = open(webroot + '/index.html', mode='w')
        print(HTMLHEAD, end='', file=activityPage)
        for stn in sorted(stations.values(), key=lambda s: s.wire):
            print('<tr><td>', stn.wire, '</td><td style="text-align:left">',
                  stn.id, '</td></tr>', sep='', file=activityPage)
        print(HTMLEND, end='', file=activityPage)
        activityPage.close()

# post message to log file
def log(msg):
    t = time.strftime('%Y-%m-%d %H:%M:%S\t%z')
    # %Z deprecated, %z not always supported
    # print('{}\t{}<br>'.format(t, msg), file=logPage, flush=True)  # Python3 only
    print('{}\t{}<br>'.format(t, msg), file=logPage)
    logPage.flush()

# main program

print('')
print(time.asctime())
print('KOBServer ' + VERSION)
sys.stdout.flush()
logPage = open(webroot + '/logs/log.html', mode='a')
log('Started KOBServer ' + VERSION)
stations = {}  # dictionary mapping IP+port to station instance
statusChanged = True
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', PORT))
updateThread = threading.Thread(target=updateStationList)
updateThread.daemon = True
updateThread.start()

while True:
    try:
        buf, stnAddr = sock.recvfrom(500)
        stnIP, stnPort = stnAddr
        nBytes = len(buf)
        station = findStation(stnAddr)
        station.time = time.time()
        if nBytes == 4:
            command, wireNo = shortRecord.unpack(buf)
            if command == CON:  # connect
                sock.sendto(ackRecord.pack(ACK), stnAddr)
                station.updateWireNo(wireNo)
            elif command == DIS and stnAddr in stations:  # disconnect
                del stations[stnAddr]
                statusChanged = True
                log('Disc\t{}'.format(stationString

(station)))
            else:
                log('Unrecognized command code: {}'.format(command))
        elif nBytes == 496:
            command, stnID, nCodeElements, stnVersion = longRecord.unpack(buf)
            stnID, sep, fill = stnID.decode(encoding='ascii',
                                            errors='ignore').partition('\x00')
            if stnID[-5:-4] == '#':
                stnPIN = stnID[-4:]
                stnID = stnID[:-5]
                pinLoc = 4 + len(stnID)
                buf = buf[:pinLoc] + 5 * b'\x00' + buf[pinLoc + 5:]
            else:
                stnPIN = ''
            stnVersion, sep, fill = stnVersion.decode(encoding='ascii',
                                                      errors='ignore').partition('\x00')
            if stnIP == NEWSBOTIP:
                stnVersion = 'NewsBot'
            if nCodeElements > 0:
                stnVersion = ''
            if command == DAT:
                station.updateIDPINandVersion(stnID, stnPIN, stnVersion)
                sw = station.wire
                if sw and (not sw in pins or stnPIN == pins[sw]) and \
                        station.id and station.version:
                    for addr in stations:
                        stn = stations[addr]
                        if stn.wire == sw and \
                                (not sw in pins or stn.pin == pins[sw]) \
                                and stn.id and stn.version and stn != station:
                            sock.sendto(buf, addr)
            else:
                log('Unrecognized command code: {}'.format(command))
        else:
            log('Invalid record length: {}'.format(nBytes))
    except Exception as e:
        sys.stderr.write('{0} KOBServer error: {1}\n'
                         .format(time.asctime(), e))
        sys.stderr.flush()