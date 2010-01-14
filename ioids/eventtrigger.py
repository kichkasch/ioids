"""
Check for new events in the database.

Inter-Organisational Intrusion Detection System (IOIDS)

This module is supposed to emulate trigger functionality of the database. Somehow, IOIDS must be
able to know about new events, reaching the central database (from other sub-systems). Since it
is quite complicated, to trigger from the database a function within this system, the following workaround
has been put in place:

This module runs a background thread, which in certain frequencies checks the event database for new
events. (configurable via main configuration file for IOIDS). New events are reported to the data engine,
which will then take further action.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

class EventTrigger:
    """
    Connect against the database frequently in order to receive latest events.
    """

    def __init__(self):
        """
        Yet empty constructor.
        """
        self._running = 0
        
    def startup(self):
        """
        Puts the trigger in the background thread and makes it waiting until it's shutdown.
        """
        from config import DB_POLL_INTERVAL
        self._interval = DB_POLL_INTERVAL
        self._running = 1
        import thread
        thread.start_new_thread(self.runUntilShutdown, ())
        
        from ioidslogging import EVENTTRIGGER_STATUS, getDefaultLogger
        getDefaultLogger().newMessage(EVENTTRIGGER_STATUS, 'Event Trigger process started')
        
    def runUntilShutdown(self):
        """
        This is the function, running in the thread, which will initiate the event download frequently.
        """
        from ioidslogging import EVENTTRIGGER_UPDATE, getDefaultLogger
        
        import time
        time.sleep(self._interval)
        while self._running:
            getDefaultLogger().newMessage(EVENTTRIGGER_UPDATE, 'Event Trigger: Synchronise with event database.')
            self._triggerEventsNow()
            time.sleep(self._interval)
        
    def _triggerEventsNow(self):
        """
        Performs the actual event triggering.
        """
        from config import LOCATION_EVENT_ID_STATUS_FILE
        from errorhandling import IoidsFormatException
        from ioidslogging import getDefaultLogger, EVENTTRIGGER_UPDATE_DETAILS
        
        # in case, we cannot get any information from the status file - we will simply use 0 here 
        # (event ids are serials - can't be less than 0)
        line1 = '-1'
        line2 = '-1'
        try:
            file = open(LOCATION_EVENT_ID_STATUS_FILE, 'r')
            line1 = file.readline()
            line2 = file.readline()
            file.close()
        except Exception, msg:
            pass

        event_id = int(line1)
        ioids_event_id = int(line2)
        
        # get the events first
        from dbconnector import getDBConnector
        from dataengine import getDataEngine
        from dataengine_tools import getPreXMLDictCreator
        creator = getPreXMLDictCreator()
        
        events = getDBConnector().getEventsFromEventID(event_id + 1)
        counter = 0
        latestEventID = str(event_id)
        for result in events:
            for relation in result['relations']:
                if relation['name'] != 'event':
                    # here is something wrong
                    raise IoidsFormatException('Wrong relation name in result set.')
                dict = relation['attributes']
                
                restructured = creator.restructureEventEntry(dict)
                getDataEngine().newEventFromLocal(restructured)
                counter += 1
                latestEventID = dict['event_id']
        getDefaultLogger().newMessage(EVENTTRIGGER_UPDATE_DETAILS, '-- Event Trigger Details: %d events received.' %(counter))

        
        # and now the ioids events
        events = getDBConnector().getIoidsEventsFromEventID(ioids_event_id + 1)
        counter = 0
        latestIoidsEventID = str(ioids_event_id)
        for result in events:
            for relation in result['relations']:
                if relation['name'] != 'ioids_event':
                    # here is something wrong
                    raise IoidsFormatException('Wrong relation name in result set.')
                dict = relation['attributes']

                restructured = creator.restructureEventEntry(dict)
                getDataEngine().newIoidsEventFromLocal(restructured)
                counter += 1
                latestIoidsEventID = dict['ioids_event_id']
        getDefaultLogger().newMessage(EVENTTRIGGER_UPDATE_DETAILS, '-- Event Trigger Details: %d ioids events received.' %(counter))
        
        # ok, finally, let's put the new values for latest event ids into the file
        file = open(LOCATION_EVENT_ID_STATUS_FILE, 'w')
        file.write('%s\n' %(latestEventID))
        file.write('%s\n' %(latestIoidsEventID))
        
    def shutdown(self):
        """
        Shutdown the thread.
        """
        self._running = 0
        from ioidslogging import EVENTTRIGGER_STATUS, getDefaultLogger
        getDefaultLogger().newMessage(EVENTTRIGGER_STATUS, 'Event Trigger process stopped')
        
        
