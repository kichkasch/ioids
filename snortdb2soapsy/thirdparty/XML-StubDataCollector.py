from pyPgSQL import libpq
import Console
import pywintypes
import thread
import time
import traceback
import win32event
import win32file
import win32pipe
import sys

def CreateConnection(notifQueue):
    tupleNo=0
    try:
        connection=libpq.PQconnectdb("dbname='snort-sensordb' hostaddr='193.63.129.185' user='xmlstub'")
        opflag='Ok'
        print "Connection established succesfuly..."
        queryString='LISTEN newInsert'
        #connection.setnonblocking(1)
        result=connection.query(queryString)
        if result.resultStatus!=libpq.COMMAND_OK:
            print "LISTEN operation failed..."
            result.clear()
        else:
            print "LISTEN '%s' dispatched succesfully..."%queryString.split(' ')[1]
            result.clear()

        
        
        

##          
##            while tupleNo<totalAnswers.ntuples:
##                attrNo=0
##                while attrNo<totalAnswers.nfields:
##                    initialValue=totalAnswers.getvalue(tupleNo,attrNo)
##                    notifQueue.append(initialValue)
##                    attrNo=attrNo+1
##                tupleNo=tupleNo+1
##            totalAnswers.clear()

    
       
        try:
            result2=connection.sendQuery('SELECT max(stub_event_id) FROM stub_Event;')            

        except libpq.InternalError, msg:
            print msg
            print "Initial stub_event_id could not be obtained..."
##            return 'Fatal' 
##
        except libpq.InterfaceError,msg:
            print msg
            print "Initial stub_event_id could not be obtained..."
##            return 'Fatal'
##
        except TypeError, msg:
            print msg
            print "Initial stub_event_id could not be obtained..."
##            return 'Fatal'            
        
     
        else:
            attrNo=0
            totalAnswers=connection.getResult()
            while totalAnswers!=None:
                initialStub_event_id=totalAnswers.getvalue(tupleNo,attrNo)
                totalAnswers=connection.getResult()
            print initialStub_event_id
            #totalAnswers.clear()

        
        #connection.reset()

        try:
            result=connection.sendQuery('SELECT count(stub_event_id)FROM stub_Event;')            

        except libpq.InternalError, msg:
            print msg
            print "Initial count of stub events could not be obtained."
            return 'Fatal' 

        except libpq.InterfaceError,msg:
            print msg
            print "Initial count of stub events could not be obtained.."
            return 'Fatal'

        except TypeError, msg:
            print msg
            print "Initial count of stub events could not be obtained..."
            return 'Fatal'

        else:
            attrNo=0  
            totalAnswers=connection.getResult()
            while totalAnswers!=None:
                initialValue=totalAnswers.getvalue(tupleNo,attrNo)
                totalAnswers=connection.getResult()
            notifQueue.append(initialValue)
            #totalAnswers.clear()


        return connection, notifQueue[0], initialStub_event_id
    
    except libpq.CONNECTION_BAD, msg:
        print "Connection to the database could not be established. %s"%msg
        return 'Error'    

    except libpq.DatabaseError, msg2:
        print msg2
        return 'Error'
   


def Reporter(conn, theQueue, h2mutex):
    while 1:

        answer=win32event.WaitForSingleObject(h2mutex,win32event.INFINITE)
        
        if answer==win32event.WAIT_OBJECT_0:

            conn.consumeInput()

            notification=conn.notifies()

            while (notification!=None):

                print "Asynchronous Notification of %s received..."%notification.relname

                theQueue[0]=theQueue[0]+1

                notification=conn.notifies()

            else:

                win32event.ReleaseMutex(h2mutex)

                print "no Notifications yet..."

                time.sleep(1)            
        else:
            pass
    

def Selection(conn, theQueue, initialValue, initialStub_event_id, h2mutex, pipeName):
    bootstrap_stub_events=initialValue
    if initialStub_event_id==None:
        bootstrap_stub_event_id=1
    else:
        bootstrap_stub_event_id=initialStub_event_id
    #tupleNo=0
    attributes=[]
    while 1:
        tupleNo=0
        index=0
        answer=win32event.WaitForSingleObject(h2mutex,1000)
        if answer==win32event.WAIT_OBJECT_0:
            print "we have the mutex"
            #If this 2 quantities are not equal new events are present in the stub table
            print theQueue[0], bootstrap_stub_events
            if theQueue[0]!=bootstrap_stub_events:
                #calculate how many events are present in the table
                #since the last select
                newEventsPresent=theQueue[0]-bootstrap_stub_events
                print newEventsPresent
                win32event.ReleaseMutex(h2mutex)
                while index<newEventsPresent:
                    print "11111111111111111111"        
                    string4Query='SELECT * FROM stub_event WHERE stub_event_id=%s;'%(bootstrap_stub_event_id)
                    print string4Query    
                    bootstrap_stub_event_id=bootstrap_stub_event_id+1
                    bootstrap_stub_events=bootstrap_stub_events+1
                    try:
                        response=conn.sendQuery(string4Query)
                    except libpq.InternalError, msg:
                        print msg
                        print "List creation failed..."
                        print "Closing connection to the database..."
                        conn.finish()
                        return 'Fatal' 
                    except libpq.InterfaceError,msg:
                        print msg
                        print "List creation failed..."
                        print "Closing connection to the database..."
                        conn.finish()
                        return 'Fatal'
                    except TypeError, msg:
                        print msg
                        print "List creation failed..."
                        print "Closing connection to the database..."
                        conn.finish()
                        return 'Fatal'
                    #everything went ok so get the result
                    else:
                        try:
                            totalAnswers=conn.getResult()
                        except Exception, details:
                            print details
                        print "Obtaining answers"
                        print totalAnswers.ntuples
                        print tupleNo
                        while tupleNo<totalAnswers.ntuples:
                            attrNo=0
                            while attrNo<totalAnswers.nfields:
                                attributes.append(totalAnswers.getvalue(tupleNo, attrNo))
                                attrNo=attrNo+1
                            print "2222222222222222222222222222222222"
                            print attributes
                            xmlfile=CreateXML(attributes[0], attributes)
                            print xmlfile
                            if xmlfile!='Fatal':
                                try:
                                    thread.start_new_thread(TransactPipe, (pipeName, xmlfile))
                                except Exception, details:
                                    print "This is the exception", details
                            else:
                                pass
                            attributes=[]
                            tupleNo=tupleNo+1
                        totalAnswers.clear()
                        index=index+1
            
            else:
                
                print "No new events present..."
                win32event.ReleaseMutex(h2mutex)
                time.sleep(1)
                
               
        else:
            pass
            


def CreateXML(fileIndex, Attribute):
    filename="C:\\Notifications\\xml_event_%s.xml"%str(fileIndex)
    try:
        file=open(filename, 'w')
    except Exception, msg:
        
        return 'Fatal'    
    else:
         print "Creating XML file..."
         strings=["<?xml version=\"1.0\"?>\n",
         "<Reporter>\n",
         "<Reporter_Name>"+'Snort_Sensor'+"</Reporter_Name>\n",
         "<Hostname>"+str(Attribute[1])+"</Hostname>\n",
         "<Event>\n",
         "<Signature>\n",
         "<Sig_Id>"+str(Attribute[2])+"</Sig_Id>\n",
         "<Timestamp>"+str(Attribute[3])+"</Timestamp>\n",	
         "<Sig_Name>"+str(Attribute[4])+"</Sig_Name>\n",
         "<Sig_Rev>"+str(Attribute[5])+"</Sig_Rev>\n",
         "<Reference>\n",
         "<Ref_Tag>"+str(Attribute[6])+"</Ref_Tag>\n",
         "</Reference>\n",
         "<Sig_Class_Name>"+str(Attribute[7])+"</Sig_Class_Name>\n",	
         "</Signature>\n",
         "<Data_Payload>"+str(Attribute[8])+"</Data_Payload>\n",
         "<IP_Header>\n",
         "<IP_Src>"+str(Attribute[9])+"</IP_Src>\n",
         "<IP_Dst>"+str(Attribute[10])+"</IP_Dst>\n",
         "<IP_Ver>"+str(Attribute[11])+"</IP_Ver>\n",
         "<IP_Hlen>"+str(Attribute[12])+"</IP_Hlen>\n",
         "<IP_Tos>"+str(Attribute[13])+"</IP_Tos>\n",
         "<IP_Len>"+str(Attribute[14])+"</IP_Len>\n",
         "<IP_ID>"+str(Attribute[15])+"</IP_ID>\n",
         "<IP_Flags>"+str(Attribute[16])+"</IP_Flags>\n",
         "<IP_Off>"+str(Attribute[17])+"</IP_Off>\n",
         "<IP_TTL>"+str(Attribute[18])+"</IP_TTL>\n",
         "<IP_Proto>"+str(Attribute[19])+"</IP_Proto>\n",
         "<IP_Csum>"+str(Attribute[20])+"</IP_Csum>\n",
         "</IP_Header>\n",
         "<TCP_Header>\n",
         "<TCP_Sport>"+str(Attribute[21])+"</TCP_Sport>\n",
         "<TCP_Dport>"+str(Attribute[22])+"</TCP_Dport>\n",
         "<TCP_Seq>"+str(Attribute[23])+"</TCP_Seq>\n",
         "<TCP_Ack>"+str(Attribute[24])+"</TCP_Ack>\n",
         "<TCP_Off>"+str(Attribute[25])+"</TCP_Off>\n",
         "<TCP_Res>"+str(Attribute[26])+"</TCP_Res>\n",
         "<TCP_Flags>"+str(Attribute[27])+"</TCP_Flags>\n",
         "<TCP_Win>"+str(Attribute[28])+"</TCP_Win>\n",
         "<TCP_CSum>"+str(Attribute[29])+"</TCP_CSum>\n",
         "<TCP_Urp>"+str(Attribute[30])+"</TCP_Urp>\n",
         "</TCP_Header>\n",
         "<UDP_Header>\n",
         "<UDP_Sport>"+str(Attribute[31])+"</UDP_Sport>\n",
         "<UDP_Dport>"+str(Attribute[32])+"</UDP_Dport>\n",
         "<UDP_Len>"+str(Attribute[33])+"</UDP_Len>\n",
         "<UDP_CSum>"+str(Attribute[34])+"</UDP_CSum>\n",
         "</UDP_Header>\n",
         "<ICMP_Header>\n",
         "<ICMP_Type>"+str(Attribute[35])+"</ICMP_Type>\n",
         "<ICMP_Code>"+str(Attribute[36])+"</ICMP_Code>\n",
         "<ICMP_CSum>"+str(Attribute[37])+"</ICMP_CSum>\n",
         "<ICMP_ID>"+str(Attribute[38])+"</ICMP_ID>\n",
         "<ICMP_Seq>"+str(Attribute[39])+"</ICMP_Seq>\n",
         "</ICMP_Header>\n",
         "<OPT>\n",
         "<OPT_ID>"+str(Attribute[40])+"</OPT_ID>\n",
         "<OPT_Proto>"+str(Attribute[41])+"</OPT_Proto>\n",
         "<OPT_Code>"+str(Attribute[42])+"</OPT_Code>\n",
         "<OPT_Len>"+str(Attribute[43])+"</OPT_Len>\n",
         "<OPT_Data>"+str(Attribute[44])+"</OPT_Data>\n",
         "</OPT>\n",
         "</Event>\n",
         "</Reporter>\n"]
         for astring in strings:
             print astring    
             file.write(astring)
             print "done"
         file.close()
         return filename
   
    
def TransactPipe(pipeName, string2Write):
    while 1:
		try:
			pipeHandle=win32file.CreateFile(pipeName,win32file.GENERIC_WRITE,0,None,win32file.OPEN_EXISTING,0,0)
		
			if pipeHandle!=win32file.INVALID_HANDLE_VALUE:

				break

			else:
				try:
					win32pipe.WaitNamedPipe(pipeName, 2000)

				except Exception, more:
					print more
				
					return 0				
			
		except win32pipe.error, details:

			return 0

		
    try:
		errCode, nBytesWritten=win32file.WriteFile(pipeHandle, string2Write, None)

		time.sleep(1)
    except Exception, details:
		print "This is the exception", details

		return 0
	
    win32file.CloseHandle(pipeHandle)

    return 1	




def Stop(hStopEvent):
    try:
        cons=Console.getconsole(0)
    except Exception, details:
        print "The following Error has been detected:%s..."%edetails
    while 1:
        peekResult=cons.peek()
        if (peekResult!=None):
            input_event=cons.get() 
            if input_event.type=="KeyPress":
                char_result=input_event.char
                if (char_result=='q'):
                    win32event.SetEvent(hStopEvent)
                    break
                else:
                    time.sleep(1)
        else:
            time.sleep(1)






if __name__=='__main__':
    global requestQueue
    requestQueue=[]
    hmutex=win32event.CreateMutex(None, 0, None)
    stopEvent=win32event.CreateEvent(None, 1, 0, None)
    pipeName="\\\\.\\pipe\\snortpipe"

    
    response=CreateConnection(requestQueue)

    if response!='Fatal' and response!='Error':
        thread.start_new_thread(Reporter, (response[0], requestQueue, hmutex))
        thread.start_new_thread(Selection, (response[0], requestQueue, response[1], response[2], hmutex, pipeName))
        thread.start_new_thread(Stop, (stopEvent,))

    elif response=='Fatal':
        print 'Closing connection to the database...'
        unresult=response[0].query('UNLISTEN newInsert')
        unresult.clear()
        response[0].finish()
        win32file.CloseHandle(pipeHandle)
        sys.exit(1)

    else:
        print "eeeeeeeeeeeeeeeee"
        win32file.CloseHandle(pipeHandle)
        sys.exit(1)
    #Everything is ok lets move on    

    while 1:
        answer=win32event.WaitForSingleObject(stopEvent,win32event.INFINITE)
        if answer==win32event.WAIT_OBJECT_0:
            time.sleep(0.5)#Be polite
            print 'Closing connection to the database...'
            unresult=response[0].query('UNLISTEN newInsert')
            unresult.clear()
            print "Terminating Application..."
            response[0].finish()
            print "Thanks for using..."
            sys.exit(0)
        else:
            pass
            
    