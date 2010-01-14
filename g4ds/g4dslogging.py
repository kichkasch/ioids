"""
Provides Logging facilities.

Grid for Digital Security (G4DS)

Currently, simple logging into files.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

from time import strftime
import string
import syslog

# "singleton"
_defaultLogger = None
def getDefaultLogger():
    """
    Singleton implementation.
    """
    global _defaultLogger
    if not _defaultLogger:
        _defaultLogger = FileLogger()
    return _defaultLogger

LOGSERVER_STATUS = 0    # boot up / shutdown of logging
COMMUNICATION_INCOMING_ERROR = 100
COMMUNICATION_INCOMING_NO_ENDPOINT = 101
COMMUNICATION_INCOMING_MSG = 199
COMMUNICATION_INCOMING_MSG_DETAILS = 198

COMMUNICATION_OUTGOING_ERROR = 200
COMMUNICATION_OUTGOING_NO_ENDPOINT = 201
COMMUNICATION_OUTGOING_ERROR_SERVICE = 202
COMMUNICATION_OUTGOING_MSG = 299
COMMUNICATION_OUTGOING_MSG_CTRL = 298
COMMUNICATION_OUTGOING_MSG_ROUTED = 297
COMMUNICATION_OUTGOING_MSG_DETAILS = 296
COMMUNICATION_OUTGOING_MSG_SERVICE_DETAILS = 295

CONTROL_SYSTEM_DETAILS = 399
CONTROL_SYSTEM_ERROR = 300

SERVICES_NEW_INCOMING = 999
SERVICES_CLIENT_CONNECT = 998
SERVICES_CLIENT_DISCONNECT = 997
SERVICES_CLIENT_SENDINGERROR = 900  

ROUTING_MESSAGE_PASSED = 899

ROUTING_TABLE_UPDATED = 799
ROUTING_TABLE_UPDATED_MANUALLY = 798
ROUTING_TABLE_UPDATED_PUHSHED = 797
ROUTING_TABLE_UPDATED_ERROR = 700

PERMISSION_MATRIX_RECALCULATED = 699
PERMISSION_MESSAGE_PASSED = 698
PERMISSION_MESSAGE_DROPPED = 601
PERMISSION_POLICY_ERROR = 602

CLASS={}
CLASS[0] = [LOGSERVER_STATUS, COMMUNICATION_INCOMING_ERROR, COMMUNICATION_OUTGOING_ERROR]
CLASS[1] = [COMMUNICATION_INCOMING_NO_ENDPOINT, COMMUNICATION_OUTGOING_NO_ENDPOINT, PERMISSION_MESSAGE_DROPPED]
CLASS[1].extend(CLASS[0])
CLASS[2] = [ROUTING_TABLE_UPDATED, PERMISSION_MATRIX_RECALCULATED, CONTROL_SYSTEM_DETAILS]
CLASS[2].extend(CLASS[1])
CLASS[3] = [PERMISSION_MESSAGE_PASSED]
CLASS[3].extend(CLASS[2])
CLASS[4] = []
CLASS[4].extend(CLASS[3])
CLASS[5] = [] #everything - not used
    
class FileLogger:
    """
    All messages are equipped with a timestamp and line wise written to a log file.
    
    Addtionally, this class supports logging into syslog facilities.
    
    @ivar _logfile: Reference to the file instance
    @type _logfile: C{File}
    @ivar _level: Log level to be used for the instance (defined in config file)
    @type _level: C{int}
    """
    
    def __init__(self):
        """
        Open the log file.
        
        Put a log message in the log file for brining up the g4ds log service.
        """
        import config
        from config import LOGGING_FILENAME, LOGGING_LEVEL, ENABLE_SYSLOG, SYSLOG_IDENTIFIER 
        self._logfile = open(LOGGING_FILENAME, 'a')
        self._level = LOGGING_LEVEL
        
        self._syslogOn = ENABLE_SYSLOG
        
        if ENABLE_SYSLOG:
            syslog.openlog(SYSLOG_IDENTIFIER)
        
        self.newMessage(LOGSERVER_STATUS, 'G4DS Logging started (level %d)' %(self._level))

    def closedown(self):
        """
        Shutdown logging.
        
        Put a log message in the log file for closing down g4ds logging and finally close the log file.
        """
        self.newMessage(LOGSERVER_STATUS, 'G4DS Logging shut down')
        self._logfile.close()
        
        if self._syslogOn:
            syslog.closelog()
        
    def newMessage(self, category, message):
        """
        New entry for the log system.
        
        A check is performed, whether the given category is to be logged in the activated log level. If so,
        a message is generated, made up by a time stamp, the category value and the message itself.
        """
        try:
            if self._level != 5:
                CLASS[self._level].index(category)
            st = strftime('%Y-%m-%d %H:%M:%S').ljust(17) + ' ' + string.zfill(category, 3) + ' ' + str(message) + '\n'
            self._logfile.write(st)
            self._logfile.flush()
            
            if self._syslogOn:
                syslog.syslog(string.zfill(category, 3) + ' ' + str(message))
                
        except KeyError:
            pass    # this log message is not in the class for the given log level - just ignore it
        
    def getLatestMessages(self, n):
        """
        Returns the last 'n' lines of the log file.
        
        @param n: Number of lines requested
        @type n: C{int}
        @return: The last lines - each line as a string - together in a list
        @rtype: C{List} of C{String}
        """
        from config import LOGGING_FILENAME, LOGGING_LEVEL
        logfile = open(LOGGING_FILENAME, 'r')
        lines = []
        s = logfile.readline().rstrip()
        i = -1
        while s != '':
            i = (i+1) % n
            if len(lines) > i:
                lines[i] = s
            else:
                lines.append(s)
            s = logfile.readline().rstrip()
        logfile.close()

        if len(lines) == i+1:
            return lines

        # put it in order
        back = []
        while len(back) < n:
            i = (i+1) % n
            back.append(lines[i])
        return back
