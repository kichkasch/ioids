#!/usr/bin/python

# ------------------XML Database Schema---------------------
# Coder Name      : Konstantinos Xynos
# Contact(email)  : man0ai@yahoo.gr
# Commencing Date : 01 June 2005
# Submission Date : 30 September 2005
# Project Title   : A SOAP-XML interface which will interpret
#                   SQL commands for an IDS database
#
# Description     : This program produces CREATE statements
#                   with the help of a offline database schema
#                   fully describing a database.
# Program Status  : Prototype
#
# Supervisor(s)   : Dr. Andrew Blyth and Dr. Gaius Mulley
#

# Imported libraries

import xml.dom.minidom # XML parser
import os,sys 
from optparse import OptionParser
import string

# Summary of Functions
#
# check_elements(doc)
# find_if_before(root,item_before,the_item)
# check_all_references(doc)
# reorder_xml(doc)
# get_type(sql_type,datatype,datatype_file)
# append_alter_grant_seq(tableNode,create_statement,objectName)
# writefile(create_statement,out_file)
# make_SQL_create_statement(doc,out_file,datatype,datatype_file)
# read_xml(user_options)
# options_menu()
# main

# Function - Details
# 
# check_elements(doc) - This function checks if the XML document
#                       provided has the correct values and that these
#                       values exist
# returns - do_exit for checking and should return 0 if there is no error

def check_elements(doc):
	do_exit=0 # if there is a problem then this should be set to 1
	cust_error_msg="" # a custom error message
	found_pk=0 # if at least one instance of a primary key is found then check passes
	
	for databaseNode in doc.getElementsByTagName("DATABASE"):
	   if (databaseNode.getAttribute("name")==""): #chech that the database name exists
	     do_exit=1
	     cust_error_msg= cust_error_msg + "The database element has no name."
	     break
	if (do_exit==0):
	 for tableNode in doc.getElementsByTagName("TABLE"):
	  found_pk=0
	  if (tableNode.getAttribute("name")==""): #chech that table name exists
	    do_exit=1
            cust_error_msg= cust_error_msg + "The table element has no name."
	    break
	    
	  for nodeColumns in tableNode.getElementsByTagName("COLUMN"):
	    if (nodeColumns.getAttribute("type")==""): #chech that column's types exist
	      do_exit=1
	      cust_error_msg= cust_error_msg + tableNode.getAttribute("name") + ": A column element has no type."
	      break
	    if(found_pk==0):
	     if (nodeColumns.getAttribute("primary_key")=="true"): #chech that table's primary key exists
	      found_pk=1
	  if(found_pk==0):
	       do_exit=1
	       cust_error_msg= cust_error_msg + tableNode.getAttribute("name") + ": A table element has no primary key."
	       break
	     
	if(do_exit==1):
          print "There is a Fault:", cust_error_msg 
	  if(debugProg["flag"]==1): print "There is a Fault:", cust_error_msg            
	
        return do_exit
#------ def end
    
# Function - Details
# 
# find_if_before(root,item_before,the_item) - Helps in the reordering of the XML tree. It 
#                    checks that the element is not already above the element.
#
# returns - returns 1 if the table was found after the_item. Other wise 0 is returned.
#           this is done to find the refernced table and add it before the one
#           referencing it.

def find_if_before(root,item_before,the_item):
    #if agent_class before observer
    #if agent_class found and not observer then it is after
    previousNode=""
    found_item=0
    for tableNode in root.getElementsByTagName("TABLE"):
        if(tableNode.getAttribute("name")==item_before):
            if(debugProg["flag"]==1): print tableNode.getAttribute("name") + " : " + item_before + " found"
            found_item=1
            
        if(tableNode.getAttribute("name")==the_item and found_item==1):
            if(debugProg["flag"]==1): print  tableNode.getAttribute("name") + " : " + the_item + " found after " + item_before
            return 1
       # else:
       #     print tableNode.getAttribute("name") + " : " + the_item + " not found after " + item_before
            
    return 0
#------ def end

# Function - Details
# 
# check_all_references(doc) - Checks that all the referencing (primary - foreign key) tables exist within the tree
#
# returns - check_ref, if reference is not found then 0 is returned and processing must
#		      stop.
	  
def check_all_references(doc):
	root = doc.documentElement # get the root element of the XML document (exlcudes headers)
        found_ref=0
        check_ref=1
        if(debugProg["flag"]==1): print "Check if all the referenced tables are correct:\n"
        for tableNode in root.getElementsByTagName("TABLE"):
	  if(debugProg["flag"]==1): print tableNode.getAttribute("name")
	  for columnsNode in tableNode.getElementsByTagName("COLUMN"):
	    if (columnsNode.getAttribute("foreign_key")=="true"): #check that column's types exist
	      if(debugProg["flag"]==1): print columnsNode.getAttribute("foreign_key")	      	      	
              found_ref=0
	      for refNode in root.getElementsByTagName("TABLE"):
	        # check if the table name is that of the columns refering table
	   	if(refNode.getAttribute("name")==columnsNode.getAttribute("refTable")):
                    if(debugProg["flag"]==1): print "Found " + columnsNode.getAttribute("refTable")
                    found_ref=1                    
              if(found_ref==0):
                 print "Did not find referencing table " + columnsNode.getAttribute("refTable") + " at table: " + tableNode.getAttribute("name")
                 check_ref=0

        return check_ref         
#------ def end
    
# Function - Details
# 
# reorder_xml(doc) - Reorders the XML document putting the all the tables that do not have
#                    foreign keys on top of the ones that do. 
	  
def reorder_xml(doc):
	root = doc.documentElement # get the root element of the XML document (exlcudes headers)
        if(debugProg["flag"]==1): print "The reordering of the XML document.\n"
        for tableNode in root.getElementsByTagName("TABLE"):
	  if(debugProg["flag"]==1): print tableNode.getAttribute("name")
	  for columnsNode in tableNode.getElementsByTagName("COLUMN"):
	    if (columnsNode.getAttribute("foreign_key")=="true"): #check that column's types exist
	      if(debugProg["flag"]==1): print columnsNode.getAttribute("foreign_key")
	      	      	
	      for refNode in root.getElementsByTagName("TABLE"):
	        # check if the table name is that of the columns refering table
	   	if(refNode.getAttribute("name")==columnsNode.getAttribute("refTable")):
		 if(find_if_before(root,columnsNode.getAttribute("refTable"),tableNode.getAttribute("name"))==0):
	          childNode=refNode
	      	  root.insertBefore(childNode,tableNode)
		  found_ref=1;
#------ def end    

# Function - Details
# 
# get_type(sql_type,datatype,datatype_file) - Converts the SQL99 type into a type defined 
#			  the datatype_file. The datatype is found and the corespponding
#                         types are converted.
#			  Types that are not found are not converted.
#
# return - sql_type, the type is then returned 
  
def get_type(sql_type,datatype,datatype_file):
	#Convert SQL statements to a different datatype
    
	doc_datatp=xml.dom.minidom.parse(datatype_file)
	root = doc_datatp.documentElement # get the root element of the XML document (exlcudes headers)
	
	for datatypeNode in root.getElementsByTagName("DATATYPE"):
            if (datatypeNode.getAttribute("type")==datatype):
                for convertNode in datatypeNode.getElementsByTagName("CONVERT"):
                    if (convertNode.getAttribute("from")==sql_type):
                      return sql_type.replace(sql_type,convertNode.getAttribute("to"))
                    elif (sql_type.find(convertNode.getAttribute("from"))!=-1):
                      if (convertNode.getAttribute("replace")=="true"):
                         return sql_type.replace(sql_type,convertNode.getAttribute("to"))
                      else:  
                         return sql_type.replace(convertNode.getAttribute("from"),convertNode.getAttribute("to"))
	#if no type is found return the same type
        if(debugProg["flag"]==1): print "The SQL type returned is: " + sql_type + "\n"
	return sql_type
#------ def end
    
# Function - Details
# 
# append_alter_grant_seq(tableNode,create_statement) - Adds the Grant text to the statement
#           based on the user. The alter and sequence parts have been commented out and
#           can be used if required.
#
# returns - create_statement, the appended text with the GRANT statement for each user of the table

def append_alter_grant_seq(tableNode,create_statement,objectName):

	for usersNode in tableNode.getElementsByTagName("USERS"):
            	for userNode in usersNode.getElementsByTagName("USER"):
                    if(userNode.getAttribute("grant")!=""):
                        create_statement = create_statement + "GRANT " + userNode.getAttribute("grant") + " ON TABLE " + objectName + " TO " + userNode.firstChild.data + ";\n"

                # Alter table - deprecated, not used by all the databases.
		#if(usersNode.getAttribute("alter")=="true"):
		#   if (usersNode.firstChild.nodeType == usersNode.firstChild.TEXT_NODE):
		#      alter_user=usersNode.firstChild.data
		#      create_statement = create_statement + "ALTER TABLE " + tableNode.getAttribute("name") + " OWNER TO " + usersNode.firstChild.data + ";\n"   

	# Sequence code project was deprecated, it can be uncommented if the user wants a custom sequence
	# or if the database does not provide one.  
	#if(alter_user!=""):
	#   create_statement = create_statement + "\nCREATE SEQUENCE " + tableNode.getAttribute("name") + "_pkey_seq\n"
	#   create_statemdecimalent = create_statement + "INCREMENT 1\n"
	#   create_statement = create_statement + "MINVALUE 1\n"
	#   create_statement = create_statement + "MAXVALUE 9223372036854775807\n"
	#   create_statement = create_statement + "START 1\n"
	#   create_statement = create_statement + "CACHE 1\n"
	#   create_statement = create_statement + "ALTER TABLE " + tableNode.getAttribute("name") + "_pkey_seq OWNER TO " + alter_user + ";\n"
	return create_statement
#------ def end
	
# Function - Details
# 
# writefile(create_statement,out_file) - The create_statement is written to the out_file specified.
#

def writefile(create_statement,out_file):
	try:
	 xml_file=open(out_file,"w")
	 xml_file.write(create_statement)
	 xml_file.close()
	 print "XDS: Output has been written to " + out_file
	except:
	 typ, value = sys.exc_info()[:2]
	 if(debugProg["flag"]==1): print "Error:", typ, "->", value	
#------ def end	

# Function - Details
#
# make_SQL_create_statement(doc,out_file,datatype,datatype_file) - The XML structure is   
#                   analysed and the SQL create statement is put together.
#                   This also includes: the adding of not null references, primary key
#                   and foreign key assosiactions, indexes and INSERTS of default values.
#                                  

def make_SQL_create_statement(doc,out_file,datatype,datatype_file):
	  root = doc.documentElement
	  comma_counter=0 # the comma_counter is used to set the comma after every second occurance of an element
	  create_statement = ""
	  
	  for tableNode in root.getElementsByTagName("TABLE"):
	     create_statement = create_statement + "\nCREATE TABLE " + tableNode.getAttribute("name") + "\n" +  "("
	     comma_counter=0
	     # add Table Columns, Types and find primary key to add NOT NULL restriction
	     for columnsNode in tableNode.getElementsByTagName("COLUMN"):
	        if (comma_counter==0):
		   create_statement = create_statement + " \n"
		   comma_counter=1
		else:
		   create_statement = create_statement + ", \n"
	     	if (columnsNode.firstChild.nodeType == columnsNode.firstChild.TEXT_NODE):
		  if (columnsNode.getAttribute("primary_key")=="true"):
                     if(datatype=="" and datatype_file==""):
                         create_statement = create_statement + columnsNode.firstChild.data + " " + columnsNode.getAttribute("type") + " NOT NULL"
		     else:
                         create_statement = create_statement + columnsNode.firstChild.data + " " + get_type(columnsNode.getAttribute("type"),datatype,datatype_file) + " NOT NULL"
		  else:
                     if(datatype=="" and datatype_file==""):
                         create_statement = create_statement + columnsNode.firstChild.data + " " + columnsNode.getAttribute("type")
		     else: 
                         create_statement = create_statement + columnsNode.firstChild.data + " " + get_type(columnsNode.getAttribute("type"),datatype,datatype_file)
		  # add the not null if the flag is set to true  
		  if (columnsNode.getAttribute("not_null")=="true" and not columnsNode.getAttribute("primary_key")):
		     create_statement = create_statement + " NOT NULL"
		
	     #  add all primary keys if the column has primary_key set to true
	     comma_counter=0
	     for columnsNode in tableNode.getElementsByTagName("COLUMN"):
	       if (columnsNode.firstChild.nodeType == columnsNode.firstChild.TEXT_NODE):
	        if (columnsNode.getAttribute("primary_key")=="true"):
		 if (comma_counter==0):
		   create_statement = create_statement + ", \nPRIMARY KEY (" + columnsNode.firstChild.data
		   comma_counter=1
		 else:
		   create_statement = create_statement + ", " + columnsNode.firstChild.data
		  
	     create_statement =create_statement + ")"

	     #  add all forgeign keys if the column has foreign_key set to true
	     for columnsNode in tableNode.getElementsByTagName("COLUMN"):
	       if (columnsNode.firstChild.nodeType == columnsNode.firstChild.TEXT_NODE):
		if (columnsNode.getAttribute("foreign_key")=="true"):
		   create_statement =create_statement + ", \n" + "FOREIGN KEY (" + columnsNode.firstChild.data + ") REFERENCES " + columnsNode.getAttribute("refTable") + " (" + columnsNode.getAttribute("refColumn") + ")"
	     create_statement = create_statement + "\n);\n" # close CREATE TABLE
	     
	     create_statement = append_alter_grant_seq(tableNode,create_statement,tableNode.getAttribute("name"))
	     
	     # add all the indexs if the column has index set to true
	     for columnsNode in tableNode.getElementsByTagName("COLUMN"):
	       if (columnsNode.firstChild.nodeType == columnsNode.firstChild.TEXT_NODE):
		if (columnsNode.getAttribute("index")=="true"):
		   create_statement =create_statement + "CREATE UNIQUE INDEX " + columnsNode.firstChild.data + "_idx ON "+ tableNode.getAttribute("name") + " (" + columnsNode.firstChild.data + "); \n"

	     create_statement =append_alter_grant_seq(tableNode,create_statement,tableNode.getAttribute("name") +"_"+ tableNode.getAttribute("name") + "_id_seq")

	     # add all the default values given by the user.
	     for rowsNode in tableNode.getElementsByTagName("ROWS"):
	      comma_counter=0
	      create_statement =create_statement + "INSERT INTO " + tableNode.getAttribute("name")
	      for rowDataNode in rowsNode.getElementsByTagName("ROWDATA"):
	       if (comma_counter==0):
		  create_statement =create_statement + " (" + rowDataNode.getAttribute("name")
		  comma_counter=1
	       else: 
	  	  create_statement = create_statement + ", " + rowDataNode.getAttribute("name")
	      create_statement =create_statement + ") VALUES ("	   
	      
	      comma_counter=0
	      for rowDataNode in rowsNode.getElementsByTagName("ROWDATA"):
	       if (rowDataNode.firstChild.nodeType == rowDataNode.firstChild.TEXT_NODE):
		if (comma_counter==0):
		   create_statement =create_statement + rowDataNode.firstChild.data 
		   comma_counter=1
		else:
	  	   create_statement = create_statement + ", " + rowDataNode.firstChild.data
	      create_statement =create_statement + "); \n"   

          # if redirected to a file the user will know where to find and cut the statement out.
	  if(debugProg["flag"]==1):
              print "The final CREATE statement is: " + create_statement + "\n"
              print "CREATE STATEMENT \n"
              print "----------------------CUT HERE-------------------------\n"

	  # if no file is given, the statement is printed.
	  if(out_file==None):
	     print create_statement
	     if(debugProg["flag"]==1): print "----------------------CUT UNTIL HERE-------------------------\n"
	  else:
	     writefile(create_statement,out_file)
#------ def end


# Function - Details
#
# read_xml() - Read the XML document and make the correct checks and reordering. Includes error
#              reporting.

def read_xml(user_options):
    try:
        global debugProg
        debugProg={}
        debugProg["flag"]=0

        #debug settings
        
	if (user_options.debug_level==None):
            debugProg["flag"]=0
        else:
            debugProg["flag"]=string.atoi(user_options.debug_level)
 
	if (user_options.input_file==None):
	   doc=xml.dom.minidom.parse(sys.stdin)
	else:
	   doc=xml.dom.minidom.parse(user_options.input_file)

	if (check_elements(doc)==0): # if all the elements are in order reorder the tree
         if(check_all_references(doc)==1): #if all the references are correct 1 is returned
	   reorder_xml(doc)  
           if (options.datatype==None): # 'None' is the defualt value if the flag does not exist
              make_SQL_create_statement(doc,user_options.output_file,"","")
           else:
              if (options.datatype_file==None):
                print "Please specify a datatype file."
              else:
                make_SQL_create_statement(doc,user_options.output_file,options.datatype,options.datatype_file)

	if(debugProg["flag"]==1): print doc.toxml() # add to debug mode

    except:
      typ, value = sys.exc_info()[:2]
      if(debugProg["flag"]==1): print "Error:", typ, "->", value
#------ def end
      
# Function - Details
#
# options_menu() - Sets the options the user can use and any help messages to assist him
#           in his selection.
#              
#http://optik.sourceforge.net/doc/1.5/reference.html

def options_menu():
	usage= "usage: XDS [options] [arguments]"
	parser = OptionParser(usage)
	parser.add_option("-i", "--input",dest="input_file",help="the XML document defining the database schema.")
	parser.add_option("-o", "--output",dest="output_file",help="the output file to write the SQL statement(s).")
        parser.add_option("-t", "--datatype",dest="datatype",help="A different datatype is used.")
	parser.add_option("-f", "--datatype_file",dest="datatype_file",help="The datatype XML document.")
	parser.add_option("-d", "--debuglevel",dest="debug_level",help="Reports debugging information in console.")
	(options,args)=parser.parse_args()
	
	if(len(args)!=0):
	   parser.error("Incorrect number of arguments")

	# if this code is uncommented then the program will not work with redirects   
	#if(options.input_file==None and len(args)==0):
	 #  parser.error("XML input file required as an option or an argument.")
	   
	return options
#------ def end
    
# Function - Details
#
# main function - Calls the options menu, which loads the users options and calls the read_xml
#        function passing the user options.
#              

options=options_menu()

read_xml(options)
   
#------ main end
