"""
Runtime controlling - job recovering and resuming.

Grid for Digital Security (G4DS)

How to use the JobDispatcher:

There is a job which might take some time due to e.g. the requirement of performing requests
to other nodes. You need to put your job into a seperate thread in order not to block the
remaining system from its work. However, your job has to be delayed until any reply has
been received in order to proceed. 

In detail, the following steps have to be performed:

    1. Call your (BIG) function in its seperate thread
    2. Create a L{JobLocker} instance from within your function.
    3. Register your function / joblocker with the JobDispatcher (L{JobDispatcher.addJob}. This will automatically lock your job.
    
As soon as a message arrives in G4DS, referencing your ID, the locker is notified (waken up) and your function
will proceed.

You may collect a message from the JobDispatcher, which was put there by the G4DS communiction engine.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)

@var _jobDispatcher: The only instance of an job dispatcher
@type _jobDispatcher: L{JobDispatcher}
"""

import threading

# "singleton"
_jobDispatcher = None
def getJobDispatcher():
    global _jobDispatcher
    if not _jobDispatcher:
        _jobDispatcher = JobDispatcher()
    return _jobDispatcher


class JobDispatcher:
    """
    Handles a list of jobs and locks as well as resumes there processing.
    """

    def __init__(self):
        """
        Local dictionary for jobs is initialised.
        """
        self._jobs = {}
        self._conditions = {}
        self._messages = {}
        

    def addJob(self, id, job, locknow = 1):
        """
        Adds a job to the local dictionary.
        
        Any job added here is delayed until an incoming message for this job is received.
        """
        self._jobs[id] = job
        self._conditions[id] = job.getCondition()
        if locknow:
            job.lock()
        
    def resumeJob(self, id, message = None, args = None, deleteFromDictionary = 1):
        """
        Unlocks the Thread; the calling function should resume.
        """
        job = self._jobs[id]
        cond = self._conditions[id]
        if deleteFromDictionary:
            del self._conditions[id]
            del self._jobs[id]
        if message or args:
            self._messages[id] = []
            self._messages[id].append(message)
            self._messages[id].append(args)
            
        cond.acquire()
        cond.notify()
        cond.release()
        
    def getMessage(self, id, deleteMessage = 1):
        """
        Gets a message from the queue for this paticular message id.
        """
        if not self._messages.has_key(id):
            raise ValueError('No message available for ref id ' + id)
        message = self._messages[id][0]
        args = self._messages[id][1]
        if deleteMessage:
            del self._messages[id]
        return message, args
        
        
class JobLocker:
    """
    Responsible for halting one particular job.
    """
    
    def __init__(self):
        """
        Initialises the condition.
        """
        self._condition = threading.Condition()

    def lock(self):
        self._condition.acquire()
        self._condition.wait()
        self._condition.release()
    
    def getCondition(self):
        """
        Returns the condition object for this locker.
        """
        return self._condition
        
JOB_UNINITIALISED = 0
JOB_INITIALISED = 1
JOB_FINISHED = 2
JOB_ABORTED = 3
JOB_FINISHED_WITH_ERROR = 4

class JobStatus:
    
    def __init__(self):
        self._status = JOB_UNINITIALISED
        self._errorcode = None
        self._errormessage = None
        self._message = None
        
    def __str__(self):
        if self._status == JOB_UNINITIALISED:
            st = 'uninitialised'
        elif self._status == JOB_INITIALISED:
            st = 'initialised'
        elif self._status == JOB_FINISHED:
            st = 'finished'
        elif self._status == JOB_ABORTED:
            st = 'aborted'
        return 'JobStatus: ' + st
        
    def setStatus(self, status):
        self._status = status
        
    def getStatus(self):
        return self._status
        
    def setError(self, code, message):
        self._errorcode = code
        self._errormessage = message
        
    def getError(self):
        return self._errorcode, self._errormessage
        
    def setMessage(self, message):
        self._message = message
        
    def getMessage(self):
        return self._message
