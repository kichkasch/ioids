#!/usr/bin/python

# ---------------------SOAP Server-------------------------
# Coder Name      : Konstantinos Xynos
# Contact(email)  : man0ai@yahoo.gr
# Commencing Date : 01 June 2005
# Submission Date : 30 September 2005
# Project Title   : A SOAP-XML interface which will
#                   interpret SQL commands for an IDS
#                   database
#
# Description     : A SOAP Server that accepts XML documents
#                   containing Insert or Select statements.
#                   After the SQL statements have been
#                   executed against the database the 
#                   results are formatted and sent back to
#                   the client.
# Program Status  : Prototype
#
# Supervisor(s)   : Dr. Andrew Blyth and Dr. Gaius Mulley
#

# Imported libraries

import sys # system library
import string # string manipulation
import cElementTree as ElementTree # xml document parser / Fast C implementation
from SOAPpy import * # SOAP server library
from StringIO import StringIO # required to read and manipulate a stream
from time import gmtime, strftime # time library

import pgdb # new PostgreSQL adapter - Pygresql - DB API v2.0
sys.path.insert(1, "..")


LOGFILE = '/tmp/xsm.log'
CONF_FILE = '/etc/XSM-configuration.xml'

# Summary of Functions
#
# writefile(incom_data,output_file)
# getSettings()
# valueConcat(aValue,connStr,nodeValue)
# getPrimaryKey(dbTable)
# dbChecker(dbTable,dbWhere)
# insertToDatabase(aQuery,dbTable)
# selectDatabase(aQuery)
# doInsert(dbTable,dbCell,dbValues,idExistsStr)
# dbSchemaChecker(XMLFile)
# columnChecker(dbTable,tableColumn,columnType)
# finder(doc)
# makeXMLReply(tableIdDesc,results,dbtable)
# goInsert(doc)
# goSelect(doc)
# finderSelect(doc)
# getOperator(strOp,comparisonValue)
# getTableFields(dbTable)
# getTableRec(fieldsDB,recs,dbtable)
# makeTheSelect(dbtable,rowWhere)
# getDocument(s)
# startSoapServer()
#

    
# Function - Details
#
# writefile(incom_data,output_file) - write the incom_data into the file specified.
#              

def writefile(incom_data,output_file):
	try:
	 debug_file=open(output_file,"a")
	 debug_file.write(incom_data)
	 debug_file.close()
	except:
	 typ, value = sys.exc_info()[:2]
	 print "Error:", typ, "->", value	
#------ def end

# Function - Details
# 
# getSettings() - Gets the settings from the file specified. 
# 
#
global debugProg
global db_Settings
global Soap_Server_Settings
db_settings = None
Soap_Server_Settings = None
debugProg = None

def getSettings():
    global debugProg
    global db_Settings
    global Soap_Server_Settings

    if not debugProg:
        debugProg={}
        debugProg["flag"]=0
        debugProg["file"]=""
        debugProg["print"]=0
        db_Settings={}
        Soap_Server_Settings={}
        
    ##    aXMLfile='XSM-configuration.xml'
        aXMLfile=CONF_FILE
        
        doc = ElementTree.parse(aXMLfile).getroot()
    
    # Go through the CONF and SET for the settings
        for node in doc.findall('CONF'):
            for nodeSet in node.findall('SET'): 
                if(nodeSet.get('name')=="debugProg" and nodeSet.get('value')=="true" and nodeSet.get('file')!=""):
                    debugProg["flag"]=1
                    debugProg["file"]=nodeSet.get('file')
                    if(nodeSet.get('print_out')=="true"):
                        debugProg["print"]=1
                    else:
                        debugProg["print"]=0
                    
                if(nodeSet.get('name')=="debugProg" and nodeSet.get('value')=="false"):
                    debugProg["flag"]=0
                    debugProg["file"]=""
                    debugProg["print"]=0
                    
                if(nodeSet.get('name')=="dbip" and nodeSet.get('value')!=""): db_Settings["dbip"]=nodeSet.get('value')
                if(nodeSet.get('name')=="dbnm" and nodeSet.get('value')!=""): db_Settings["dbnm"]=nodeSet.get('value')
                if(nodeSet.get('name')=="dbuser" and nodeSet.get('value')!=""): db_Settings["dbuser"]=nodeSet.get('value')
                if(nodeSet.get('name')=="dbpass" and nodeSet.get('value')!=""): db_Settings["dbpass"]=nodeSet.get('value')
                if(nodeSet.get('name')=="dbencod" and nodeSet.get('value')!=""): db_Settings["dbencod"]=nodeSet.get('value')
                if(nodeSet.get('name')=="dbunicod" and nodeSet.get('value')!=""): db_Settings["dbunicod"]=nodeSet.get('value')
                
                if(nodeSet.get('name')=="databaseSchema" and nodeSet.get('value')!=""): db_Settings["databaseSchema"]=nodeSet.get('value')
    
                if(nodeSet.get('name')=="Soap_Server_IP" and nodeSet.get('value')!=""): Soap_Server_Settings["Soap_Server_IP"]=nodeSet.get('value')
                if(nodeSet.get('name')=="Soap_Server_Port" and nodeSet.get('value')!=""): Soap_Server_Settings["Soap_Server_Port"]=nodeSet.get('value')
    
        if(debugProg["flag"]==1):
            debug_Info= "Getting settings from configuration file... [%s]\n" %(aXMLfile) 
            debug_Info= debug_Info + "The settings document is " + ElementTree.tostring(doc) + "\n"
            debug_Info= debug_Info +  "Settings accepted -\n\tSoap Server: " + str(Soap_Server_Settings) + "\n\t Database setting: " + str(db_Settings) + " \n\tDebug Flag: " + str(debugProg) + "\n"
            if(debugProg["print"]==1): print debug_Info
            writefile(debug_Info,debugProg["file"])
            debug_Info=""
        
#------ def end


# Function - Details
# 
# valueConcat(aValue,connStr,nodeValue) - Concatenats the nodeValue to the aValue with the connStr
# aValue - The initial value
# connStr - the concatenating string that will be added in between
# nodeValue - the value that will be concatenated
#
# returns - the new aValue 

def valueConcat(aValue,connStr,nodeValue):
    if aValue=='':
        aValue=aValue + nodeValue
    else:
        aValue=aValue + connStr + nodeValue
        
    return aValue
#------ def end

# Function - Details
# 
# getPrimaryKey(dbTable) - The table is given and based on the database schema specified the 
#                       primary key column is then returned.
# dbTable - The table who's primary key we are looking for.
#
# returns primaryKey - the primary key column that has been found from the database schema file.
def getPrimaryKey(dbTable):
    primaryKey=""
    aXMLfile=db_Settings["databaseSchema"]
    if(debugProg["flag"]==1):
        debug_Info= "Database schema XML file that will be processed... [%s]\n" %(aXMLfile)
        if(debugProg["print"]==1): print debug_Info
        writefile(debug_Info,debugProg["file"])
        debug_Info=""

    doc = ElementTree.parse(aXMLfile).getroot()
    # Find the table and go through the columns till the primary key is found
    for node in doc.findall('TABLE'):
      if(dbTable==node.get('name')):
        for columnsNode in node.findall('COLUMNS'):
         for columnNode in columnsNode.findall("COLUMN"):
            if (columnNode.get('primary_key')=="true"):
                primaryKey=columnNode.text

    return primaryKey
#------ def end

# Function - Details
# 
# dbChecker(dbTable,dbWhere) - Checks whether the table already exists,before the insertion,
#                             and if it does then its' primary key is returned.
# dbTable - the table we are going to insert information in
# dbWhere - the where clause that has been created, based on the attributes provided.
#
# returns - The primary key of the table(idExistsStr) and the primary keys column name (table_key)
def dbChecker(dbTable,dbWhere):        

    idExists=''
    idExistsStr=''
    table_key=''
    table_key =getPrimaryKey(dbTable)
    SelectQuery="SELECT " + table_key + " FROM " + dbTable + " WHERE " + dbWhere + " ;"

    idExists= selectDatabase(SelectQuery)
    idExistsStr=str(idExists)
    idExistsStr=idExistsStr.strip('[(,)]')

    if(debugProg["flag"]==1):
        debug_Info= "The select query executed during database checking: " + str(SelectQuery) + " . The primary key returned is: " + str(idExistsStr) + ".\n" 
        if(debugProg["print"]==1): print debug_Info
        writefile(debug_Info,debugProg["file"])
        debug_Info=""

    SelectQuery=''
	 
    return idExistsStr,table_key
#------ def end

# Function - Details
# 
# insertToDatabase(aQuery,dbTable) - Executes the insert query (aQuery) given and with 
#                       the table name the function can create the select to retrive
#                       and return the primary key instead of the OID.
# aQuery - the insert query passed
# dbTable - the table name
#
# returns - The table key (primary key) from the record that has just being inserted.
def insertToDatabase(aQuery,dbTable):
    dbip=db_Settings["dbip"]
    dbnm=db_Settings["dbnm"]
    dbuser=db_Settings["dbuser"]
    dbpass=db_Settings["dbpass"]
    dbencod=db_Settings["dbencod"]
    dbunicod=db_Settings["dbunicod"]

    DBconnection = pgdb.connect(host=dbip,user=dbuser, password=dbpass,
                             database=dbnm)
    cu = DBconnection.cursor()
    cu.execute(aQuery)
    result = cu.lastrowid
    
    DBconnection.commit()
    DBconnection.close()

    table_key =getPrimaryKey(dbTable)
    # Use the OID value(SelectQuery) to get and return the primary key
    SelectQuery="SELECT " + table_key + " FROM " + dbTable + " WHERE oid=" + str(result)
    if(debugProg["flag"]==1):
        debug_Info= "The select query executed during the retrival of the table key instead of the OID: " + str(SelectQuery) + "\n"
        if(debugProg["print"]==1): print debug_Info
        writefile(debug_Info,debugProg["file"])
        debug_Info=""

    result= selectDatabase(SelectQuery)

    results2=[]
    results3=[]

    # convert all returning types to strings    
    for n in range(len(result)):
      for j in range(len(result[n])):
    	results2.append(str(result[n][j]))
      results3.append(results2)
      results2=[]	
    
    result=results3
    
    return result
#------ def end


# Function - Details
# 
# selectDatabase(aQuery) - Executes the select query (aQuery) and returns the results.
#                       
# returns results - results from the select query given.
def selectDatabase(aQuery):
    
    dbip=db_Settings["dbip"]
    dbnm=db_Settings["dbnm"]
    dbuser=db_Settings["dbuser"]
    dbpass=db_Settings["dbpass"]
    dbencod=db_Settings["dbencod"]
    dbunicod=db_Settings["dbunicod"]

    DBconnection = pgdb.connect(host=dbip,user=dbuser, password=dbpass,
                             database=dbnm)
    cu = DBconnection.cursor()
    
    if(debugProg["flag"]==1):
        debug_Info= "The select query executed is: " + str(aQuery)
        if(debugProg["print"]==1): print debug_Info
        writefile(debug_Info,debugProg["file"])
        debug_Info=""

    cu.execute(aQuery)
    results=''
    results=cu.fetchall()
    DBconnection.close()
    
    results2=[]
    results3=[]

    # convert all returning types to strings
    for n in range(len(results)):
      for j in range(len(results[n])):
    	results2.append(str(results[n][j]))
      results3.append(results2)
      results2=[]
    results=results3

    return results
#------ def end


# Function - Details
# 
# doInsert(dbTable,dbCell,dbValues,dbWhere,idExistsStr) - Creates the insert string and passes
#                        it to the function insertToDatabase. The Primary Key value is returned
#                        and then the column name has to be retrived. The value and column name
#                        are returned.
# dbTable - The table name
# dbCell - the set of column names
# dbValues - the set of values to be inserted
# idExistsStr - the primary key, if the key does not exist then the process starts.
#
# returns tabID,table_key - the primary key value and column name
def doInsert(dbTable,dbCell,dbValues,idExistsStr):
    table_key=""
    tabID=""
    if idExistsStr=="":
        if(debugProg["flag"]==1): debug_Info= "Process insert for " + str(dbTable) + "\n"
            
        dbInsert = "INSERT INTO " + dbTable + " (" + dbCell + ") VALUES " + " (" + dbValues + ")"
        
        if(debugProg["flag"]==1): debug_Info=debug_Info + "The insert command executed: " + str(dbInsert) + "\n"
        
        results = insertToDatabase(dbInsert,dbTable)
        tabID=str(results)
        tabID=tabID.strip('[(,)]')

        #get primary key name
        table_key =getPrimaryKey(dbTable)
        
        if(debugProg["flag"]==1):
            debugInfo=debug_Info + "The primary key is : " + str(tabID) + " and the table column is : " + str(table_key) + "\n"
            if(debugProg["print"]==1): print debug_Info
            writefile(debug_Info,debugProg["file"])
            debug_Info=""
            
        dbValues=''
        dbTable=''
        dbCell=''
    return tabID,table_key
#------ def end


# Function - Details
# 
# dbSchemaChecker(XMLFile) - Checks if the data type of the database Schema and that of the
#                          XML file are the same.One (1, true) is retuned if they are correct.
# XMLFile - The XML document to check.
#
# returns - Returns 1 if the data types match, other wise 0 if they do not.
def dbSchemaChecker(XMLFile):

    aDbSchema=db_Settings["databaseSchema"]

    if(debugProg["flag"]==1):
        debug_Info= "The Database schema XML that will be processed... [%s]\n" %(aDbSchema) + "\n"
        if(debugProg["print"]==1): print debug_Info
        writefile(debug_Info,debugProg["file"])
        debug_Info=""

    dbSchema = ElementTree.parse(aDbSchema).getroot()

    if(dbSchema.get('datatype') and XMLFile.get('datatype')):
       if (dbSchema.get('datatype')==XMLFile.get('datatype')):
          return 1
    return 0
#------ def end


# Function - Details
# 
# columnChecker(dbTable,tableColumn,columnType) - Checks that the column name and type 
#                       match with those in the database Schema.
# dbTable - The table who's column we are looking for.
# tableColumn - The column name
# columnType - and the column type
#
# returns Returns 1 if the column name and type match, other wise 0 if they do not.
def columnChecker(dbTable,tableColumn,columnType):

    aDbSchema=db_Settings["databaseSchema"]

    if(debugProg["flag"]==1): debug_Info= "The Database schema XML that will be processed... [%s]\n" %(aDbSchema) + "\n"

    #XMLFile = ElementTree.parse(aXMLFile).getroot()
    dbSchema = ElementTree.parse(aDbSchema).getroot()

    found_type=0
    found_column=0
    # Find the table and go through the columns till the column and type are found and match.
    for node in dbSchema.findall('TABLE'):
       if(dbTable==node.get('name')):
          for columnsNode in node.findall('COLUMNS'):
             for columnNode in columnsNode.findall("COLUMN"):
                if (columnNode.text==tableColumn):
                   found_column=1
                   if (columnNode.get('type')==columnType):
                      found_type=1
                
    if (found_type==0):
        if(debugProg["flag"]==1):
            debug_Info=debug_Info + "There is a mismatch: column " + str(tableColumn) + " has a wrong type: " + str(columnType) + " .\n"
            if(debugProg["print"]==1): print debug_Info
            writefile(debug_Info,debugProg["file"])
            debug_Info=""
        return 0
    if (found_column==0):
        if(debugProg["flag"]==1):
            debug_Info="Column name:" + str(tableColumn) + " is not found.\n"
            if(debugProg["print"]==1): print debug_Info
            writefile(debug_Info,debugProg["file"])
            debug_Info=""
        return 0

    return 1

#------ def end


# Function - Details
# 
# finder(doc) - The function which goes through the tree for any 'REL' tags. Once
#               going over the first 'REL' tag and its 'ATT' tags it will recursively
#               try to find any more nested 'REL' elements.
#
#     IMPORTANT NOTE: the tag and attribute names are case sensitive
#                     (e.g. rel is differnt from REL)
#
# doc - the XML document the has to be parsed
#
# returns - table_relations, table_values, table_name, lists for storing columns, thier values and the table name
#
def finder(doc):
    rowValues=''
    dbTable=''
    rowCell=''
    rowWhere=''
    theSQLresults=''
    table_key=''
    table_relations=[]
    table_values=[]
    table_name=[]
    column_Names=[]
    
    for node in doc.findall('REL'):
        rowValues=''
        dbTable=''
        rowCell=''
        rowWhere=''
        theSQLresults=''
        
        dbTable=node.get('name')
        if(debugProg["flag"]==1):
            debug_Info= "Relation name: %s" %(node.get('name')) + "\n"
        if(debugProg["flag"]==1):
            debug_Info=debug_Info+ " -----Attributes------ " + "\n"
        for node2 in node.findall('ATT'):
                                             
            # add the values to the dbValues string required for the insert
            rowValues=valueConcat(rowValues,",","\'" + node2.text + "\'")
            if(debugProg["flag"]==1): debug_Info=debug_Info+ "Attribute Value: %s " %(node2.text) + "\n"
                                  
            # add the values to the dbCell string required for the insert
            rowCell=valueConcat(rowCell,",",node2.get('name'))
            if(debugProg["flag"]==1):
                debug_Info=debug_Info+ "name: %s " %(node2.get('name')) + "\n"
               
            if(debugProg["flag"]==1):
                debug_Info=debug_Info+ "type: %s" %(node2.get('type')) + "\n"
            columnType=node2.get('type')
            tableColumn=node2.get('name')

            #Stopper here if column and type mismatch with that from the database schema
            if (columnChecker(dbTable,tableColumn,columnType)==0):
                return "-","-","-"
            
            column_Names.append(node2.get('name'))
            # add the values to the dbWhere string required for the select
            rowWhere=valueConcat(rowWhere," AND ",node2.get('name') + "=\'" + node2.text + "\'")
            
            # add the values to the dbWhere string required for the select
            #rowWhere=valueConcat(rowWhere," AND ",node2.get('name') + "=\'" + node2.text + "\'")

        
        if(debugProg["flag"]==1):
            debug_Info =debug_Info+" --------------------- \n"

        # recursevly go and find the next value if it has more REL tags

	# test mpilgerm 17/11/2005
	debug_Info += "\n***********----***:" + str( node.findall('REL'))
	
        if node.findall('REL'):
            theDbTable=""
            table_key_insert,theSQLresults,theDbTable = finder(node)
	    debug_Info += "\n***********----***:" + str(theSQLresults) + "\n" + str(theDbTable)
            if(table_key_insert=="-" and theSQLresults=="-" and theDbTable=="-"): return "-","-","-"
            if(debugProg["flag"]==1):
                debug_Info=debug_Info+"The returned values from the recursion: " + str(theSQLresults) + " " + str(table_key_insert)+"\n"
                
            for i in range(len(theSQLresults)):

                if (str(type(theSQLresults[i])).split("\'")[1]=='str'):
                    rowValues=valueConcat(rowValues,",",theSQLresults[i])
                else:
                    rowValues=valueConcat(rowValues,",\'",theSQLresults[i]+"\'")
                rowCell=valueConcat(rowCell,",",table_key_insert[i])

                rowWhere=valueConcat(rowWhere," AND ",table_key_insert[i] + "=" + theSQLresults[i])

	        # mpilgerm 17/11/2005
	        debug_Info += "\n--**********************---*******: " + str( table_key_insert)
        
	        column_Names.append(table_key_insert[i])

        # get table fields and add them to the where clause with NULL    
        column_name=getTableFields(dbTable,"true")
        
        tempRange=range(len(column_name))
        for aKey in column_Names :
            if (aKey in column_name):
                column_name.remove(aKey)

        for n in range(len(column_name)):
                    rowWhere=valueConcat(rowWhere," AND ",column_name[n] + " is NULL")
                    
        # check if it exists otherwise insert it
        idExistsStr,table_key=dbChecker(dbTable,rowWhere)
        if (idExistsStr!="" and table_key!=""):
            table_values.append(idExistsStr)
            table_relations.append(table_key)
            table_name.append(dbTable)
        else:
        # Go and do the Insert now
            idExistsStr,table_key=doInsert(dbTable,rowCell,rowValues,idExistsStr)
            table_values.append(idExistsStr)
            table_relations.append(table_key)
            table_name.append(dbTable)

        idExistsStr=''
        table_key=''
        rowWhere=''
        column_name=[]
        column_Names=[]
        
        if(debugProg["flag"]==1):
            debug_Info =debug_Info+"The returned values from the finder function: " + str(table_relations) + " " + str(table_values)+"\n"
            if(debugProg["print"]==1): print debug_Info
            writefile(debug_Info,debugProg["file"])
            debug_Info=""
            
    return table_relations, table_values, table_name
#------ def end

# Function - Details
# 
# makeXMLReply(tableIdDesc,results,dbtable)) - Create the reply for the Insert. It processes
#                       the results and formats the XML document.
# tableIdDesc - The column names.
# results - The results from the Select query
# dbtable - The name of the table
#
# returns - myDoc which is the formatted XML string that will be sent over to the SOAP client.
def makeXMLReply(tableIdDesc,results,dbtable):
    myDoc="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<RELATIONS command=\"INSERT_RESULTS\">\n"
    results=str(results)
    tableIdDesc=str(tableIdDesc)
    dbtable=str(dbtable)
    
    results=results.replace('\'',"")
    tableIdDesc=tableIdDesc.replace('\'',"")
    dbtable=dbtable.replace('\'',"")

    rec=tableIdDesc.strip('[(,)]')
    rec=rec.split('], [')

    rec2=results.strip('[(,)]')
    rec2=rec2.split('], [')

    rec3=dbtable.strip('[(,)]')
    rec3=rec3.split('], [')
    for n in range(len(rec)):
        r=rec[n].split(', ')
        r2=rec2[n].split(', ')
        r3=rec3[n].split(', ')
        for n in range(len(r)):
         myDoc=myDoc+"\t<REL name=\""+r3[n]+"\">\n"    
         myDoc=myDoc+"\t\t<ATT name=\""+r[n]+"\" primary_key=\"true\">"+r2[n]+"</ATT>\n"
         myDoc=myDoc+"\t</REL>\n"
    myDoc=myDoc+"</RELATIONS>\n"

    if(debugProg["flag"]==1):
        debug_Info=myDoc
        if(debugProg["print"]==1): print debug_Info
        writefile(debug_Info,debugProg["file"])
        debug_Info=""
            
    return myDoc
#------ def end

# Function - Details
# 
# goInsert(doc) - The first function which calls the finder function to find and create 
#                 the insert statement and then formats the results and returns them 
#                 to be sent to the client.
# doc - the XML document that will be processed
#
# returns - the XML results to be sent to the client.
def goInsert(doc):
    
    results=""
    tableIdDesc=""
    xmlDocResults=""
    
    if(dbSchemaChecker(doc)==1):
        if(debugProg["flag"]==1):
            debug_Info= "The XML document is " + ElementTree.tostring(doc)+"\n"
            if(debugProg["print"]==1): print debug_Info
            writefile(debug_Info,debugProg["file"])
            debug_Info=""
        tableIdDesc,results,dbtable= finder(doc)

        # Specific Errors which are returned to the client
        if(tableIdDesc=="-" and results=="-" and dbtable=="-"):
            xmlDocResults="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            xmlDocResults=xmlDocResults + "<RELATIONS name=\"ERROR\">\n\t<REL name=\"ERROR_1\">\n\t\t<ATT name=\"error_message\">Column or Type mismatch in XML and Schema file."
            xmlDocResults=xmlDocResults + "</ATT>\n\t</REL>\n</RELATIONS>\n"
        else:
            xmlDocResults = makeXMLReply(tableIdDesc,results,dbtable)
    else:
        # Specific Errors which are returned to the client
        xmlDocResults="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        xmlDocResults=xmlDocResults + "<RELATIONS name=\"ERROR\">\n\t<REL name=\"ERROR_1\">\n\t\t<ATT name=\"error_message\">Datatype mismatch in files."
        xmlDocResults=xmlDocResults + "</ATT>\n\t</REL>\n</RELATIONS>\n"
	
    return xmlDocResults
#------ def end

#------ 
#------ SELECT PART
#------

# Function - Details
# 
# goSelect(doc) - The initial function, if the document is to process a Select request.
#                     The results are formatted here and in the finderSelect function.
#                     They are then returned to be sent to the client.
#
# doc - the XML document that will be processed
#
# returns - the XML results to be sent to the client.
def goSelect(doc):
    #global myDoc
    myDoc=''

    if(debugProg["flag"]==1):
        debug_Info= "The XML document is " + ElementTree.tostring(doc)+"\n"
        if(debugProg["print"]==1): print debug_Info
        writefile(debug_Info,debugProg["file"])
        debug_Info=""

    myDoc="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    myDoc=myDoc+"<RELATIONS command=\"SELECT_RESULTS\">\n"
    myDoc = finderSelect(doc,myDoc)
    myDoc=myDoc+"</RELATIONS>\n"

    return myDoc        
#------ def end

# Function - Details
# 
# finderSelect(doc) - The function goes through the document and constructs the
#                     select SQL statement components and send them to the 
#                     makeTheSelect.
# doc - the XML document that will be processed
#

def finderSelect(doc,myDoc):
    rowValues=''
    dbTable=''
    rowCell=''
    rowWhere=''
    replacedOp=''
    #global myDoc

    resultsIdCounter=0

    for node in doc.findall('REL'):
        rowValues=''
        dbTable=''
        rowCell=''
        rowWhere=''

        resultsIdCounter+=1
        myDoc=myDoc+"<REL name=\'RESULTS_ID\' value=\'" + str(resultsIdCounter) + "\'>\n"

        dbTable=node.get('name')

        if(debugProg["flag"]==1):
            debug_Info= "Relation name: %s" %(node.get('name')) + "\n -----Attributes------ " + "\n"

        for node2 in node.findall('ATT'):
                                             
            # add the values to the dbValues string required for the insert
            rowValues=valueConcat(rowValues,",",node2.text)
            if(debugProg["flag"]==1):
                debug_Info=debug_Info + "Attribute Value: %s " %(node2.text) + "\n"
                                  
            # add the values to the dbCell string required for the insert
            rowCell=valueConcat(rowCell,",",node2.get('name'))
            if(debugProg["flag"]==1):
                debug_Info=debug_Info + "name: %s " %(node2.get('name')) + "\n"
               
            if(debugProg["flag"]==1):
                debug_Info=debug_Info +  "type: %s" %(node2.get('type')) + "\n"

            # replace operator to create statement
            if node2.get('op'):
                replacedOp=getOperator(node2.get('op'),node2.text.strip().replace('\n',''))
                if (replacedOp=="none"):
                    if(debugProg["print"]==1): print "Error in operator"
                    if(debugProg["flag"]==1):
                        debug_Info=debug_Info + "Error in operator" + "\n"

                rowWhere=valueConcat(rowWhere," AND ",node2.get('name') + replacedOp)
            else:
                rowWhere=valueConcat(rowWhere," AND ",node2.get('name') + "= \'" + node2.text.strip().replace('\n','') + "\'")

        if(debugProg["flag"]==1):
            debug_Info=debug_Info + str(rowWhere) + "\n"
        
        if(debugProg["flag"]==1):
            debug_Info=debug_Info +  " --------------------- \n"
            if(debugProg["print"]==1): print debug_Info
            writefile(debug_Info,debugProg["file"])
            debug_Info=""
        
        if (replacedOp!="none"): myDoc=makeTheSelect(dbTable,rowWhere,myDoc)
        
        myDoc=myDoc+"</REL>\n"
    myDoc=myDoc+"<REL name=\"TOTAL_RESULTS\">" + str(resultsIdCounter)
    myDoc=myDoc+"</REL>\n"
    return myDoc

#------ def end

# Function - Details
# 
# getOperator(strOp,comparisonValue) - The limits of XML brought the introduction of
#                     string operators which have a one to one mapping. Found with
#                     the help of a dictionary variable.
# strOp - the value provided by the user,extracted from the XML document.
# comparisonValue - the value that will be used in the SQL statement.
#
# return - newString, which is the value after the one to one replacement with the value

def getOperator(strOp,comparisonValue):
    strOperators={"lt":"<","ltq":"<=","gt":">","gtq":">=","eq":"=","neq":"<>","lk":"like \'%","slk":"like \'","elk":"like \'%","nlk":"not like '%","nslk":"not like '","nelk":"not like '%"}
    newString=""

    if (strOperators.has_key(strOp)):
        if(strOp=="lk" or strOp=="slk" or strOp=="nlk" or strOp=="nslk" ):
            newString=newString + " " + strOperators[strOp] + comparisonValue + "%\'"
        else:
            if(strOp=="elk" or strOp=="nelk"):
                newString=newString+ " " + strOperators[strOp] + comparisonValue + "\'"
            else:
                newString=newString+ " " + strOperators[strOp] + " \'"+ comparisonValue + "\'"
    else:
        return "none"

    if(debugProg["flag"]==1):
            debug_Info= "Operator replacement: "+ str(newString) + "\n"
            if(debugProg["print"]==1): print debug_Info
            writefile(debug_Info,debugProg["file"])
            debug_Info=""

    return newString
    
#------ def end

# Function - Details
# 
# getTableFields(dbTable) - The function goes through the database Schema
#                       to find the table and save the column names in a  
#                       list which is returned.
# dbTable - the table name
#
# tableFields - a list with the columns of the table

def getTableFields(dbTable,noPrimaryKey):
    tableFields=[]
    aXMLfile=db_Settings["databaseSchema"]
    
    doc = ElementTree.parse(aXMLfile).getroot()
    # Find the table and go through the columns and save them to a list.
    for node in doc.findall('TABLE'):
      if(dbTable==node.get('name')):
        for columnsNode in node.findall('COLUMNS'):
         for columnNode in columnsNode.findall("COLUMN"):
            if(noPrimaryKey=='true' and (columnNode.get('primary_key')=="true" or columnNode.get('primary_key')=="True") ):
                pass
            else:
                tableFields.append(columnNode.text)

    if(debugProg["flag"]==1):
            debug_Info= "Table columns "+ str(tableFields) + "\n"
            if(debugProg["print"]==1): print debug_Info
            writefile(debug_Info,debugProg["file"])
            debug_Info=""
            
    return tableFields
#------ def end

# Function - Details
# 
# getTableRec(fieldsDB,recs,dbtable) - Gets the results, columnNames and table name  
#                       and formats the results in a XML format.
# fieldsDB - list of column names
# recs - list of results
# dbtable - table name

def getTableRec(fieldsDB,recs,dbtable,myDoc):
    #global myDoc
    recordsCounter=0
    for n in range(len(recs)):
        myDoc=myDoc+"<REL name=\'"+dbtable+"\'>\n"
        for j in range(len(recs[n])):
            myDoc=myDoc+"\t<ATT name=\'"+str(fieldsDB[j])+"\'>"+str(recs[n][j])+"</ATT>\n"
        myDoc=myDoc+"</REL>\n"
        recordsCounter+=1
        
    myDoc=myDoc+"<REL name=\"TOTAL_RECORDS\">" + str(recordsCounter)
    myDoc=myDoc+"</REL>\n"
    return myDoc
#------ def end

# Function - Details
# 
# makeTheSelect(dbtable,rowWhere) - Gets the columns names and makes the select requests.
#                       The results are then sent to getTableRec to format the results. 
# dbtable - the table name.
# rowWhere - the where clause constructed base on the values given by the user(XML document)

def makeTheSelect(dbtable,rowWhere,myDoc):
    tableFields=[]
    # get the names of the table's columns
    tableFields=getTableFields(dbtable,"false")

    fieldsDB=""
    
    for n in range(len(tableFields)):
        fieldsDB=valueConcat(fieldsDB,",",tableFields[n])

    if (rowWhere):

        result=selectDatabase("select "+ fieldsDB +" from "+ dbtable +" WHERE "+ rowWhere)

        if(debugProg["flag"]==1):
            debug_Info= "SELECT comamnd: select "+ str(fieldsDB) +" from "+ str(dbtable) +" WHERE "+ str(rowWhere) + "\nSelect results: \n" + str(result) + "\n"
            if(debugProg["print"]==1): print debug_Info
            writefile(debug_Info,debugProg["file"])
            debug_Info=""
    else:
        "select "+ fieldsDB +" from "+ dbtable
        result=selectDatabase("select "+ fieldsDB +" from "+ dbtable)

        if(debugProg["flag"]==1):
            debug_Info= "SELECT comamnd: select "+ str(fieldsDB) +" from "+ str(dbtable) + "\nSelect results: \n" + str(result) + "\n"
            if(debugProg["print"]==1): print debug_Info
            writefile(debug_Info,debugProg["file"])
            debug_Info=""

    myDoc=getTableRec(tableFields,result,dbtable,myDoc)
    return myDoc
#------ def end

#------ 
#------ END SELECT PART
#------

#------ 
#------ JOIN PART
#------


# Function - Details
# 
# goSelect(doc) - The initial function, if the document is to process a Select request.
#                     The results are formatted here and in the finderSelect function.
#                     They are then returned to be sent to the client.
#
# doc - the XML document that will be processed
#
# returns - the XML results to be sent to the client.
def goJoin(doc):
    #global myDoc
    myDoc=''
    global tableDB
    tableDB=''

    global resultsIdCounter
    global fieldsDB
    fieldsDB=''
    global rowWhere
    rowWhere=''
    global tableFKeys
    tableFKeys=[]
    global tableFieldsG
    tableFieldsG=[]

    global fkTable
    fkTable=[]
    

    resultsIdCounter=0


    if(debugProg["flag"]==1):
        debug_Info= "The XML document is " + ElementTree.tostring(doc)+"\n"
        if(debugProg["print"]==1): print debug_Info
        writefile(debug_Info,debugProg["file"])
        debug_Info=""

    myDoc="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    myDoc=myDoc+"<RELATIONS command=\"JOIN_RESULTS\">\n"

    myDoc=myDoc+"<REL name=\'RESULTS_ID\' value=\'" + str(resultsIdCounter) + "\'>\n"    

    finderJoin(doc,'0','none')
    resultsIdCounter+=1
    #if (replacedOp!="none"): makeTheSelect(dbTable,rowWhere)
    #print " " + rowWhere + " =-=-=- " +fieldsDB + " *** " + str(tableDB) + "^^^^^^^^" + str(tableFKeys) + str(tableFieldsG)

    for n in range(len(tableFKeys)):
        rowWhere=valueConcat(rowWhere," AND ", tableFKeys[n])
        print rowWhere +  tableFKeys[n]
    myDoc=makeTheJoin(tableDB,fieldsDB,rowWhere,myDoc)
    
    myDoc=myDoc+"</REL>\n"
    myDoc=myDoc+"<REL name=\"TOTAL_RESULTS\">" + str(resultsIdCounter)
    myDoc=myDoc+"</REL>\n"

    myDoc=myDoc+"</RELATIONS>\n"

    return myDoc        
#------ def end

# Function - Details
# 
# finderSelect(doc) - The function goes through the document and constructs the
#                     select SQL statement components and send them to the 
#                     makeTheSelect.
# doc - the XML document that will be processed
#

def finderJoin(doc,recursion,topTable):

    global tableDB
    global fieldsDB
    global tableFieldsG
    global tableFKeys
    global rowWhere
    rowValues=''
    rowCell=''

    replacedOp=''
    me=''        
    for node in doc.findall('REL'):
        rowValues=''
        rowCell=''
        tableName=''

        tableDB=valueConcat(tableDB,",",str(node.get('name')))
        tableName=node.get('name')

        if(debugProg["flag"]==1):
            debug_Info= "Relation name: %s" %(node.get('name')) + "\n -----Attributes------ " + "\n"

        for node2 in node.findall('ATT'):
                                             
            # add the values to the rowValues string required for the select
            rowValues=valueConcat(rowValues,",",node2.text)
            if(debugProg["flag"]==1):
                debug_Info=debug_Info + "Attribute Value: " + node2.text + "\n"
                                  
            # add the values to the rowCell string required for the select
            rowCell=valueConcat(rowCell,",",tableName+"."+node2.get('name'))
            if(debugProg["flag"]==1):
                debug_Info=debug_Info + "name: " + tableName + "." + node2.get('name') + "\n"


            # replace operator to create statement
            if node2.get('op'):
                replacedOp=getOperator(node2.get('op'),node2.text.strip().replace('\n',''))
                if (replacedOp=="none"):
                    if(debugProg["print"]==1): print "Error in operator"
                    if(debugProg["flag"]==1):
                        debug_Info=debug_Info + "Error in operator" + "\n"

                rowWhere=valueConcat(rowWhere," AND ",tableName+"."+node2.get('name') + replacedOp)
            else:
                rowWhere=valueConcat(rowWhere," AND ",tableName+"."+node2.get('name') + "=\'" + node2.text.strip().replace('\n','') + "\'")

            # add is NULL clause to where.    ----- bad remove me
           # if node2.get('isNULL'):
           #     if node2.get('isNULL')=='true':
           #         rowWhere=valueConcat(rowWhere," AND ",tableName+"."+node2.get('name') + " is NULL")

                
        if(debugProg["flag"]==1):
            debug_Info=debug_Info + str(rowWhere) + "\n"
        
        if(debugProg["flag"]==1):
            debug_Info=debug_Info +  " --------------------- \n"
            if(debugProg["print"]==1): print debug_Info
            writefile(debug_Info,debugProg["file"])
            debug_Info=""


        tableFields=[]
        # get the names of the table's columns
        tableFields=getTableFields(tableName,"false")

        for n in range(len(tableFields)):
            fieldsDB=valueConcat(fieldsDB,",",tableName+ "." +tableFields[n])
            tableFieldsG.append(tableName+ "." +tableFields[n])

        # get the top foreign relation table name an put in list
        #if (recursion=='1'):
        if (topTable!='none'):
            fkTable.append(tableName)

        # recursevly go and find the next value if it has more REL tags
        if node.findall('REL'):
            finderJoin(node,'1',tableName)

        #go through list to get foreign key from main table
        #if (recursion=='0'):
        if (topTable!='none'):
            for n in range(len(fkTable)):
                getTableForgnKeys(fkTable[n],topTable)
    #--end for
        

#------ def end

# Function - Details
# 
# getTableForgnKeys(dbTable) - The function goes through the database Schema
#                       to find the table and save the column names in a  
#                       list which is returned.
# dbTable - the table name
#
# tableFields - a list with the columns of the table

def getTableForgnKeys(fkT,dbTable):
    aXMLfile=db_Settings["databaseSchema"]
    
    doc = ElementTree.parse(aXMLfile).getroot()
    # Find the table and go through the columns and save them to a list.
    for node in doc.findall('TABLE'):
      if(dbTable==node.get('name')):
        for columnsNode in node.findall('COLUMNS'):
         for columnNode in columnsNode.findall("COLUMN"):
             if (columnNode.get('foreign_key')=="true" and fkT==columnNode.get('refTable')):
                 tableFKeys.append(columnNode.get('refTable')+ "." + columnNode.get('refColumn')+ "=" + dbTable + "." + columnNode.text)

    if(debugProg["flag"]==1):
            debug_Info= "Table foreign keys "+ str(tableFKeys) + "\n"
            if(debugProg["print"]==1): print debug_Info
            writefile(debug_Info,debugProg["file"])
            debug_Info=""
            
#------ def end

# Function - Details
# 
# makeTheSelect(dbtable,rowWhere) - Gets the columns names and makes the select requests.
#                       The results are then sent to getTableRec to format the results. 
# dbtable - the table name.
# rowWhere - the where clause constructed base on the values given by the user(XML document)

def makeTheJoin(dbtable,fieldDB,rowWhere,myDoc):

    global tableFieldsG

    if (rowWhere):
        result=selectDatabase("select "+ fieldDB +" from "+ dbtable +" WHERE "+ rowWhere)

        if(debugProg["flag"]==1):
            debug_Info= "SELECT comamnd: select "+ str(fieldDB) +" from "+ str(dbtable) +" WHERE "+ str(rowWhere) + "\nSelect results: \n" + str(result) + "\n"
            if(debugProg["print"]==1): print debug_Info
            writefile(debug_Info,debugProg["file"])
            debug_Info=""
            

    myDoc=getTableRec(tableFieldsG,result,dbtable,myDoc)
    return myDoc
#------ def end

#------ 
#------ END JOIN PART
#------

#------ 
#------ SOAP SERVER
#------ 
    
#------ SOAP server
Config.simplify_objects = 1

# Function - Details
# 
# getDocument(s) - The function gets the XML document sent by the client. Depending
#                  on the command the goInsert or goSelect function is called. In the
#                  end the formatted XML document is returned to be sent to the client.
#                  It also includes error reporting. All errors are traced back here.
# s - the XML document that will be processed
#
# return - xmlDocResults, returns the formatted XML document to the SOAP server
def getDocument(s):
    xmlDocResults=''
    try:
        getSettings()
        IOStreamer=StringIO(s)
        doc = ElementTree.parse(IOStreamer).getroot()
        if(debugProg["flag"]==1):
            debug_Info= "\nXML file execution command:" + str(doc.get('command')) + "\n"
            if(debugProg["print"]==1): print debug_Info
            writefile(debug_Info,debugProg["file"])
            debug_Info=""
        if(doc.get('command')):
            if(doc.get('command')=="INSERT"):
                xmlDocResults=goInsert(doc)
            if(doc.get('command')=="SELECT"):
                xmlDocResults=goSelect(doc)
            if(doc.get('command')=="JOIN"):
                xmlDocResults=goJoin(doc)
        else:
            xmlDocResults="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            xmlDocResults=xmlDocResults + "<RELATIONS name=\"ERROR\">\n\t<REL name=\"ERROR_1\">\n\t\t<ATT name=\"error_message\">Document command missing:Either SELECT or INSERT."
            xmlDocResults=xmlDocResults + "</ATT>\n\t</REL>\n</RELATIONS>\n"
    except:
        typ, value = sys.exc_info()[:2]
        if(debugProg["print"]==1): print "Error:", typ, "->", value
        if(debugProg["flag"]==1):
                debug_Info= "\nError:" + str(typ) + " -> "+ str(value) +"\n"
                writefile(debug_Info,debugProg["file"])
                debug_Info=""
        xmlDocResults="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        xmlDocResults=xmlDocResults + "<RELATIONS name=\"ERROR\">\n\t<REL name=\"ERROR_1\">\n\t\t<ATT name=\"error_message\">" + str(typ) + " -> " + str(value)
        xmlDocResults=xmlDocResults + "</ATT>\n\t</REL>\n</RELATIONS>\n"
	
    return xmlDocResults
#------ def end

# Function - Details
# 
# startSoapServer() - The time the server started and stopped are captured and saved
#                     in the debug file. The settings are then loaded for the server
#                     to initiate.
#                     After getDocument() is registered, it is invoked when a
#                     SOAP RPC request is sent to the server by a client.
#                     The server will listen for ever until it is stopped with:
#                     Windows OS: CTRL+C together with a request (i.e.,select or insert)
#                     Posix: CTRL+C
#
#                     Note: The threading SOAP server is being initiated.
#
def startSoapServer():

        #Get the time the server started and add it to add to the debug file.
        ServerTime="\n\t-------------------------------------\n"
        ServerTime=ServerTime+"SOAP Server Started at: " + strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()) + "\n"
        getSettings()
        SoapAddress=Soap_Server_Settings["Soap_Server_IP"]
        SoapPort=int(Soap_Server_Settings["Soap_Server_Port"])
	addr = (SoapAddress, SoapPort)
	prefix = 'http'
	# multi-threading implementation
	server = ThreadingSOAPServer(addr)
	print "Server listening at: %s://%s:%d/" % (prefix, addr[0], addr[1])

	
        if(debugProg["flag"]==1):
            debug_Info= ServerTime
            debug_Info= debug_Info + "Server listening at: %s://%s:%d/ \n" % (prefix, addr[0], addr[1])
            if(debugProg["print"]==1): print ServerTime
            writefile(debug_Info,debugProg["file"])
            debug_Info=""
                
	# register the method
	server.registerFunction(getDocument)

	# Start the server
	try:
            try:
    		server.serve_forever()
    		
            except KeyboardInterrupt:
                pass
    	finally:
            print "XSM: Program Exited Succesfully"
            if(debugProg["flag"]==1):
                ServerTime="\nSOAP Server Closed at: " + strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()) + "\n"
                ServerTime=ServerTime+"\t-------------------------------------\n"
                if(debugProg["print"]==1): print ServerTime
                debug_Info= ServerTime
                writefile(debug_Info,debugProg["file"])
                debug_Info=""
      
#------ def end
#------ SOAP server end

#------ main

# Start SOAP Server

##startSoapServer()

#------ main end

class DummyOut:
    def __init__(self, out):
        self._out = out
        self._file = open(LOGFILE, 'a')

    def write(self, msg):
        #self._out.write(msg)
        self._file.write(msg)
        self._file.flush()
        
    def flush(self):
        self._file.flush()
            
if __name__ == "__main__":

    import os, sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '-d':     # daemon mode
            daemon_mode = 1
        elif sys.argv[1] == '-D':   # no daemon mode
            daemon_mode = 0
    else:
        daemon_mode = 1
    
    if daemon_mode:
        try:
            pid = os.fork()
            if pid:
                os._exit(0) # kill original
        except OSError, msg:
            print "Could not start xsm as deamon. Error: %s" %msg
            sys.exit(1)
        
        sys.stdout = DummyOut(sys.stdout)
        sys.stderr = DummyOut(sys.stderr)
        
    startSoapServer()
