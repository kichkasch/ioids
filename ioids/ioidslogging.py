"""
Provides Logging facilities.

Inter-Organisational Intrusion Detection System (IOIDS)

This is just a copy from the G4DS logging facilities with changes applied to make it suitable
for IOIDS use. (looks like, it should be extracted in a tools module ;))

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

EVENTTRIGGER_STATUS = 199
EVENTTRIGGER_UPDATE = 198
EVENTTRIGGER_UPDATE_DETAILS = 197

DATAENGINE_ERROR_GENERIC = 200
DATAENGINE_STATUS = 299
DATAENGINE_PROCESSING_DETAILS = 298
DATAENGINE_POLICY_STATUS = 290
DATAENGINE_POLICY_INFORMATION = 289

G4DS_CONNECTOR_STATUS = 299
G4DS_CONNECTOR_ERROR_GENERIC = 200
G4DS_CONNECTOR_INCOMING_MSG = 211
G4DS_CONNECTOR_INCOMING_MSG_DETAILS = 212
G4DS_CONNECTOR_OUTGOING_MSG = 221
G4DS_CONNECTOR_OUTGOING_MSG_DETAILS = 222

CLASS={}
CLASS[0] = [LOGSERVER_STATUS]
CLASS[1] = [EVENTTRIGGER_STATUS, DATAENGINE_STATUS, G4DS_CONNECTOR_STATUS, DATAENGINE_POLICY_STATUS]
CLASS[1].extend(CLASS[0])
CLASS[2] = [DATAENGINE_ERROR_GENERIC, G4DS_CONNECTOR_ERROR_GENERIC]
CLASS[2].extend(CLASS[1])
CLASS[3] = [EVENTTRIGGER_UPDATE, G4DS_CONNECTOR_INCOMING_MSG, G4DS_CONNECTOR_OUTGOING_MSG]
CLASS[3].extend(CLASS[2])
CLASS[4] = [G4DS_CONNECTOR_INCOMING_MSG_DETAILS, G4DS_CONNECTOR_OUTGOING_MSG_DETAILS]
CLASS[4].extend(CLASS[3])
CLASS[5] = [EVENTTRIGGER_UPDATE_DETAILS, DATAENGINE_PROCESSING_DETAILS, DATAENGINE_POLICY_INFORMATION] #everything - not used
    
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
        from config import LOGGING_FILENAME, LOGGING_LEVEL, ENABLE_SYSLOG, SYSLOG_IDENTIFIER 
        self._logfile = open(LOGGING_FILENAME, 'a')
        self._level = LOGGING_LEVEL
        
        self._syslogOn = ENABLE_SYSLOG
        
        if ENABLE_SYSLOG:
            syslog.openlog(SYSLOG_IDENTIFIER)
        
        self.newMessage(LOGSERVER_STATUS, 'IOIDS Logging started (level %d)' %(self._level))

    def closedown(self):
        """
        Shutdown logging.
        
        Put a log message in the log file for closing down g4ds logging and finally close the log file.
        """
        self.newMessage(LOGSERVER_STATUS, 'IOIDS Logging shut down')
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
                
        except ValueError:
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
