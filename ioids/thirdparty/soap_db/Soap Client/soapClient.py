#!/usr/bin/env python

# ---------------------SOAP Client--------------------------
# Coder Name      : Konstantinos Xynos
# Contact(email)  : man0ai@yahoo.gr
# Commencing Date : 01 June 2005
# Submission Date : 30 September 2005
# Project Title   : A SOAP-XML interface which will interpret
#                   SQL commands for an IDS database
#
# Description     : A SOAP Client program that sends XML
#                   documents to a SOAP server and print the
#                   results on the screen.
# Program Status  : Prototype
#
# Supervisor(s)   : Dr. Andrew Blyth and Dr. Gaius Mulley
#

# Imported libraries

import sys
sys.path.insert(1, "..")
import string
from SOAPpy import *
from optparse import OptionParser

# Summary of Functions
#
# options_menu()
# writefile(XMLDoc,output_file,error_log)
# doRequest(user_options)
# main
#

# Function - Details
#
# options_menu() - The options arguments a user can specify.
#
# return options - returns the options used later for different options/flags.
#
#http://optik.sourceforge.net/doc/1.5/reference.html

def options_menu():

        global debugProg
        debugProg={}
        debugProg["flag"]=0

	usage= "usage: soapClient [options] [arguments]"
	parser = OptionParser(usage)
	parser.add_option("-a", "--address",dest="address",help="the address of the SOAP Server.")
        parser.add_option("-d", "--debuglevel",dest="debug_level",help="debug options are on.")
	parser.add_option("-i", "--input",dest="input_file",help="the XML document to be sent to the SOAP server.")
	parser.add_option("-o", "--output",dest="output_file",help="the file the ouput will be saved in.")
	parser.add_option("-p", "--port",dest="port",help="the port the SOAP Server is listening on.")
	
	(options,args)=parser.parse_args()

	if(len(args)!=0):
	   parser.error("Incorrect number of arguments")
	   
	if(options.address==None):
	   parser.error("Soap Server address is required.")
	# if uncommented then the program will not process files that are piped or streamed.   
	#if(options.input_file==None and len(args)==0):
	#   parser.error("XML input file required as an option or an argument.")
	
        #debug settings
        
	if (options.debug_level==None):
            debugProg["flag"]=0
        else:
            debugProg["flag"]=string.atoi(options.debug_level)
            
	return options
#------ def end
    
# Function - Details
#
# writefile(XMLDoc,output_file,error_log) - write the XMLDoc to the file specified.
#              

def writefile(XMLDoc,output_file,error_log):
	try:
	 xml_file=open(output_file,"w")
	 xml_file.write(XMLDoc)
	 xml_file.close()
	 if (error_log=="err_true"): print "Error has been logged: SOAP Server/Client error output has been written to " + output_file + "\n"
	 if (error_log=="err_false"): print "SOAP Client: Output has been written to " + output_file + "\n"
	except:
	 typ, value = sys.exc_info()[:2]
	 if(debugProg["flag"]==1): print "Error:", typ, "->", value	
#------ def end
	 
# Function - Details
#
# doRequest(user_options) - sets the SOAP server settings based on the arguments given
#			    and reads the XML document and sends it.
#
# user_options - passing of the options
#              
def doRequest(user_options):
	# ask for returned SOAP responses to be converted to basic python types
	Config.simplify_objects = 1

    	# Get the users arguments to connect to the server
	
	if (user_options.address==None):
	   address="localhost"
	else:
	   address=user_options.address
	   
	if (user_options.port==None):
	   port="9900"
	else:
	   port=user_options.port
	serverSettings="http://" + address + ":" + port
	try:
                server = SOAPProxy(serverSettings)
        	if(debugProg["flag"]==1): print "Sending XML document to the SOAP server: http://" + address + ":" + port 
                XMLDoc=""
	# Read the standard input if a file is not specified.
		if (user_options.input_file==None):
		  theDoc=""
		  for line in sys.stdin.readlines():
		     theDoc+= line
		  if (theDoc!=""):
                      XMLDoc= server.getDocument(theDoc)
                      if(debugProg["flag"]==1): print "Document sent:\n"+theDoc + "\n"
		else:
		  theDoc=""
		  for line in open(user_options.input_file,"r").readlines():
		     theDoc+= line
		  if (theDoc!=""):
                      XMLDoc = server.getDocument(theDoc)
                      if(debugProg["flag"]==1): print "Document sent:\n"+theDoc + "\n"
                      
		if(user_options.output_file==None):
                    print XMLDoc
                else:
                    writefile(XMLDoc,user_options.output_file,"err_false")
                    if(debugProg["flag"]==1): print "Reply from server:\n"+XMLDoc + "\n"
	
	except Exception, e:
    		err_msg="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    		err_msg=err_msg + "<RELATIONS name=\"ERROR\">\n\t<REL name=\"ERROR_1\">\n\t\t<ATT name=\"error_message\">" + str(e)
    		err_msg=err_msg + "</ATT>\n\t</REL>\n</RELATIONS>\n"
    		if(user_options.output_file==None):
                    print err_msg
                else:
                    writefile(err_msg,user_options.output_file,"err_true")
#------ def end

# Function - Details
#                    
# main function - The options given by the user are retirived and passed on to the doRequest function.
#
options=options_menu() 
doRequest(options)
#------ main end
