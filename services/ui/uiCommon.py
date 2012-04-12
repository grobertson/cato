import urllib
import uiGlobals
import os
import sys
import json
import uuid
import base64
import cgi
import re
import xml.etree.ElementTree as ET
from catocommon import catocommon
import providers

# writes to stdout using the catocommon.server output function
# also prints to the console.
def log(msg, debuglevel = 2):
    if debuglevel >= uiGlobals.debuglevel:
        uiGlobals.server.output(msg)
        print msg

def getAjaxArg(sArg):
    data = uiGlobals.web.data()
    dic = json.loads(data)
    return dic[sArg]

def NewGUID():
    return str(uuid.uuid1())

def IsGUID(s):
    p = re.compile("^(\{{0,1}([0-9a-fA-F]){8}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){12}\}{0,1})$")
    m = p.match(s)
    if m:
        return True
    else:
        return False

def IsTrue(var):
    # not just regular python truth testing - certain string values are also "true"
    # but false if the string has length but isn't a "true" statement
    # since any object could be passed here (we only want bools, ints or strs)
    # we just cast it to a str
    s = str(var).lower()
    if len(s) > 0 and str(var).lower() in "true,yes,on,enable,enabled":
        print "[" + str(var).lower() + "] IS TRUE because it matched [true,yes,on,enable,enabled]"
        return True
    else:
        # wasn't an explicit string match, return the regular python truth value
        if var:
            print "[" + str(var) + "] IS TRUE because of Python"
            return True
        else:
            return False
         
def TickSlash(s):
    return s.replace("'", "''").replace("\\", "\\\\")

def packJSON(sIn):
    if not sIn:
        return sIn
    
    sOut = base64.b64decode(sIn)
    return sOut.replace("/", "%2F").replace("+", "%2B")

def unpackJSON(sIn):
    if not sIn:
        return sIn
    
    sOut = sIn.replace("%2F", "/").replace("%2B", "+")
    return base64.b64decode(sOut)

def QuoteUp(sString):
    retval = ""
    
    for s in sString.split(","):
        retval += "'" + s + "',"
    
    return retval[:-1] #whack the last comma 

def GetSnip(sString, iMaxLength):
    # helpful for short notes or long notes with a short title line.
    
    # odd behavior, but web forms seems to put just a \n as the newline entered in a textarea.
    # so I'll test for both just to be safe.
    sReturn = ""
    if sString:
        bShowElipse = False
        
        iLength = sString.find("\\n")
        if iLength < 0:
            iLength = sString.find("\\r\\n")
        if iLength < 0:
            iLength = sString.find("\\r")
        if iLength < 0:
            iLength = iMaxLength
            
        # now, if what we are showing is shorter than the entire field, show an elipse
        # if it is the entire field, set the length
        if iLength < len(sString):
            bShowElipse = True
        else:
            iLength = len(sString)

        sReturn += sString[0:iLength]
        if bShowElipse:
            sReturn += " ... "

    return SafeHTML(sReturn)

def SafeHTML(sInput):
    return cgi.escape(sInput)

def FixBreaks(sInput):
    return sInput.replace("\r\n", "<br />").replace("\r", "<br />").replace("\n", "<br />").replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")

def AddSecurityLog(db, sUserID, LogType, Action, ObjectType, ObjectID, LogMessage):
    sTrimmedLog = LogMessage.replace("'", "''").replace("\\","\\\\").strip()
    if sTrimmedLog:
        if len(sTrimmedLog) > 7999:
            sTrimmedLog = sTrimmedLog[:7998]
    sSQL = "insert into user_security_log (log_type, action, user_id, log_dt, object_type, object_id, log_msg) \
        values ('" + LogType + "', '" + Action + "', '" + sUserID + "', now(), " + str(ObjectType) + ", '" + ObjectID + "', '" + sTrimmedLog + "')"
    if not db.exec_db_noexcep(sSQL):
        log(__name__ + "." + sys._getframe().f_code.co_name + ":: " + db.error, 2)

def WriteObjectAddLog(db, oType, sObjectID, sObjectName, sLog = ""):
    if sObjectID and sObjectName:
        if not sLog:
            sLog = "Created: [" + TickSlash(sObjectName) + "]."
        else:
            sLog = "Created: [" + TickSlash(sObjectName) + "] - [" + sLog + "]"

        AddSecurityLog(db, GetSessionUserID(), uiGlobals.SecurityLogTypes.Object, uiGlobals.SecurityLogActions.ObjectAdd, oType, sObjectID, sLog)

def WriteObjectDeleteLog(db, oType, sObjectID, sObjectName, sLog = ""):
    if sObjectID and sObjectName:
        if not sLog:
            sLog = "Deleted: [" + TickSlash(sObjectName) + "]."
        else:
            sLog = "Deleted: [" + TickSlash(sObjectName) + "] - [" + sLog + "]"

        AddSecurityLog(db, GetSessionUserID(), uiGlobals.SecurityLogTypes.Object, uiGlobals.SecurityLogActions.ObjectDelete, oType, sObjectID, sLog)

def WriteObjectChangeLog(db, oType, sObjectID, sObjectName, sLog = ""):
    if sObjectID and sObjectName:
        if not sObjectName:
            sObjectName = "[" + TickSlash(sObjectName) + "]."
        else:
            sLog = "Changed: [" + TickSlash(sObjectName) + "] - [" + sLog + "]"

        AddSecurityLog(db, GetSessionUserID(), uiGlobals.SecurityLogTypes.Object, uiGlobals.SecurityLogActions.ObjectAdd, oType, sObjectID, sLog)

def WriteObjectPropertyChangeLog(db, oType, sObjectID, sLabel, sFrom, sTo):
    if sFrom and sTo:
        if sFrom != sTo:
            sLog = "Changed: " + sLabel + " from [" + TickSlash(sFrom) + "] to [" + TickSlash(sTo) + "]."
            AddSecurityLog(db, GetSessionUserID(), uiGlobals.SecurityLogTypes.Object, uiGlobals.SecurityLogActions.ObjectAdd, oType, sObjectID, sLog)


def ForceLogout(sMsg):
    if not sMsg:
        sMsg = "Session Ended"
    
    # logging out kills the session
    uiGlobals.session.kill()
    
    log("Forcing logout with message: " + sMsg, 0)
    raise uiGlobals.web.seeother('/login?msg=' + urllib.quote(sMsg))

def GetSessionUserID():
    try:
        uid = GetSessionObject("user", "user_id")
        if uid:
            return uid
        else:
            ForceLogout("Server Session has expired (1). Please log in again.")
    except Exception as ex:
        raise ex

def GetSessionObject(category, key):
    try:
        cat = uiGlobals.session.get(category, False)
        if cat:
            val = cat.get(key, None)
            if val:
                return val
            else:
                return ""
        else:
            #no category?  try the session root
            val = uiGlobals.session.get(key, False)
            if val:
                return val
            else:
                return ""
        
        return ""
    except Exception as ex:
        raise ex

def SetSessionObject(key, obj, category=""):
    if category:
        uiGlobals.session[category][key] = obj
    else:
        uiGlobals.session[key] = obj
    
def GetCloudProviders(): #These were put in the session at login
    try:
        cp = GetSessionObject("", "cloud_providers")
        if cp:
            return cp
        else:
            ForceLogout("Server Session has expired (1). Please log in again.")
    except Exception as ex:
        raise ex

#this one takes a modified Cloud Providers class and puts it into the session
def UpdateCloudProviders(cp):
    SetSessionObject("cloud_providers", cp, "")
    
#put the cloud providers and object types from a file into the session
def SetCloudProviders():
    x = ET.parse("../../conf/cloud_providers.xml")
    if x:
        cp = providers.CloudProviders(x)
        uiGlobals.session.cloud_providers = cp
    else:
        raise Exception("Critical: Unable to read/parse cloud_providers.xml.")

#this one returns the entire FunctionCategories class
def GetTaskFunctionCategories():
    return GetSessionObject("", "function_categories")

#this one returns the flattened Functions class
def GetTaskFunctions():
    return GetSessionObject("", "functions")

#this one returns just one specific function
def GetTaskFunction(sFunctionName):
    funcs = GetTaskFunctions()
    if funcs:
        try:
            fn = funcs[sFunctionName]
            if fn:
                return fn
            else:
                return None
        except Exception:
            return None
    else:
        return None
#put the cloud providers and object types from a file into the session
def SetTaskCommands():
    try:
        from taskCommands import FunctionCategories, Functions
        #we load two classes here...
        #first, the category/function hierarchy
        cats = FunctionCategories()
        bCoreSuccess = cats.Load("task_commands.xml")
        if not bCoreSuccess:
            raise Exception("Critical: Unable to read/parse task_commands.xml.")

        #try to append any extension files
        #this will read all the xml files in /extensions
        #and append to sErr if it failed, but not crash or die.
        for root, subdirs, files in os.walk("extensions"):
            for f in files:
                ext = os.path.splitext(f)[-1]
                if ext == ".xml":
                    fullpath = os.path.join(root, f)
                    if not cats.Append(fullpath):
                        log("WARNING: Unable to load extension command xml file [" + fullpath + "].", 0)

        #put it in the session...
        uiGlobals.session.function_categories = cats

        #then the flat list of all functions for fastest lookups
        funcs = Functions.WithCategories(cats)
        uiGlobals.session.functions = funcs

        return True
    except Exception, ex:
        raise Exception("Unable to load Task Commands XML." + ex.__str__())

