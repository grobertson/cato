import urllib2
import uiGlobals
import sys
import traceback
import json
import uuid
import base64
import cgi
import re
import pickle
import xml.etree.ElementTree as ET
import providers
from catocommon import catocommon

# writes to stdout using the catocommon.server output function
# also prints to the console.
def log(msg, debuglevel = 2):
    if debuglevel <= uiGlobals.debuglevel:
        user_id = ""
        try:
            user_id = GetSessionUserID()
        except:
            """ do nothing if there's no user - it may be pre-login """
            
        if not user_id:
            user_id = ""
            
        log_nouser(msg, debuglevel)

def log_nouser(msg, debuglevel = 2):
    if debuglevel <= uiGlobals.debuglevel:
        try:
            if msg:
                uiGlobals.server.output(str(msg))
                print str(msg)
        except:
            if msg:
                uiGlobals.server.output(msg)
                print msg

def CatoEncrypt(s):
    return catocommon.cato_encrypt(s)

def CatoDecrypt(s):
    return catocommon.cato_decrypt(s)

def getAjaxArgs():
    """Just returns the whole posted json as a json dictionary"""
    data = uiGlobals.web.data()
    return json.loads(data)

def getAjaxArg(sArg, sDefault=""):
    """Picks out and returns a single value."""
    data = uiGlobals.web.data()
    dic = json.loads(data)
    
    if dic.has_key(sArg):
        if dic[sArg]:
            return dic[sArg]
        else:
            return sDefault
    else:
        return sDefault

def GetCookie(sCookie):
    cookie=uiGlobals.web.cookies().get(sCookie)
    if cookie:
        return cookie
    else:
        log("Warning: Attempt to retrieve cookie [%s] failed - cookie doesn't exist.  This is usually OK immediately following a login." % sCookie, 3)
        return ""

def SetCookie(sCookie, sValue):
    try:
        uiGlobals.web.setcookie(sCookie, sValue)
    except Exception:
        log("Warning: Attempt to set cookie [%s] failed." % sCookie, 2)
        uiGlobals.request.Messages.append(traceback.format_exc())

def NewGUID():
    return str(uuid.uuid1())

def IsGUID(s):
    if not s:
        return False

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
    
    # JUST BE AWARE, this isn't standard python truth testing.
    # So, "foo" will be false... where if "foo" would be true in pure python
    s = str(var).lower()
    if len(s) > 0:
        if str(var).lower() in "true,yes,on,enable,enabled":
            return True
        else:
            # let's see if it was a number, in which case we can just test it
            try:
                int(s)
                if s > 0:
                    return True
            except Exception:
                """no exception, it just wasn't parseable into an int"""
                
    return False
         
def TickSlash(s):
    """ Prepares string values for string concatenation, or insertion into MySql. """
    return s.replace("'", "''").replace("\\", "\\\\").replace("%", "%%")

def packJSON(sIn):
    if not sIn:
        return sIn
    sOut = base64.b64encode(sIn)
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

def LastIndexOf(s, pat):
    if not s:
        return -1

    return len(s) - 1 - s[::-1].index(pat)

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

def AddSecurityLog(LogType, Action, ObjectType, ObjectID, LogMessage):
    uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
    
    sTrimmedLog = TickSlash(LogMessage).strip()
    if sTrimmedLog:
        if len(sTrimmedLog) > 7999:
            sTrimmedLog = sTrimmedLog[:7998]
    sSQL = "insert into user_security_log (log_type, action, user_id, log_dt, object_type, object_id, log_msg) \
        values ('" + LogType + "', '" + Action + "', '" + GetSessionUserID() + "', now(), " + str(ObjectType) + ", '" + ObjectID + "', '" + sTrimmedLog + "')"
    if not uiGlobals.request.db.exec_db_noexcep(sSQL):
        uiGlobals.request.Messages.append(uiGlobals.request.db.error)

def WriteObjectAddLog(oType, sObjectID, sObjectName, sLog = ""):
    if sObjectID and sObjectName:
        if not sLog:
            sLog = "Created: [" + TickSlash(sObjectName) + "]."
        else:
            sLog = "Created: [" + TickSlash(sObjectName) + "] - [" + sLog + "]"

        AddSecurityLog(uiGlobals.SecurityLogTypes.Object, uiGlobals.SecurityLogActions.ObjectAdd, oType, sObjectID, sLog)

def WriteObjectDeleteLog(oType, sObjectID, sObjectName, sLog = ""):
    if sObjectID and sObjectName:
        if not sLog:
            sLog = "Deleted: [" + TickSlash(sObjectName) + "]."
        else:
            sLog = "Deleted: [" + TickSlash(sObjectName) + "] - [" + sLog + "]"

        AddSecurityLog(uiGlobals.SecurityLogTypes.Object, uiGlobals.SecurityLogActions.ObjectDelete, oType, sObjectID, sLog)

def WriteObjectChangeLog(oType, sObjectID, sObjectName, sLog = ""):
    if sObjectID and sObjectName:
        if not sObjectName:
            sObjectName = "[" + TickSlash(sObjectName) + "]."
        else:
            sLog = "Changed: [" + TickSlash(sObjectName) + "] - [" + sLog + "]"

        AddSecurityLog(uiGlobals.SecurityLogTypes.Object, uiGlobals.SecurityLogActions.ObjectAdd, oType, sObjectID, sLog)

def WriteObjectPropertyChangeLog(oType, sObjectID, sLabel, sFrom, sTo):
    if sFrom and sTo:
        if sFrom != sTo:
            sLog = "Changed: " + sLabel + " from [" + TickSlash(sFrom) + "] to [" + TickSlash(sTo) + "]."
            AddSecurityLog(uiGlobals.SecurityLogTypes.Object, uiGlobals.SecurityLogActions.ObjectAdd, oType, sObjectID, sLog)

def PrepareAndEncryptParameterXML(sParameterXML):
    try:
        if sParameterXML:
            xDoc = ET.fromstring(sParameterXML)
            if xDoc is None:
                uiGlobals.request.Messages.append("Parameter XML data is invalid.")
    
            # now, all we're doing here is:
            #  a) encrypting any new values
            #  b) moving any oev values from an attribute to a value
            
            #  a) encrypt new values
            for xToEncrypt in xDoc.findall("parameter/values/value[@do_encrypt='true']"):
                xToEncrypt.text = CatoEncrypt(xToEncrypt.text)
                del xToEncrypt.attrib["do_encrypt"]
    
            # b) unbase64 any oev's and move them to values
            for xToEncrypt in xDoc.findall("parameter/values/value[@oev='true']"):
                xToEncrypt.text = unpackJSON(xToEncrypt.text)
                del xToEncrypt.attrib["oev"]
            
            return ET.tostring(xDoc)
        else:
            return ""
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())


def ForceLogout(sMsg):
    if not sMsg:
        sMsg = "Session Ended"
    
    # logging out kills the session
    uiGlobals.session.kill()
    
    log("Forcing logout with message: " + sMsg, 0)
    raise uiGlobals.web.seeother('/login?msg=' + urllib2.quote(sMsg))

def GetSessionUserID():
    try:
        uid = GetSessionObject("user", "user_id")
        if uid:
            return uid
        else:
            ForceLogout("Server Session has expired (1). Please log in again.")
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())

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
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())

def SetSessionObject(key, obj, category=""):
    if category:
        uiGlobals.session[category][key] = obj
    else:
        uiGlobals.session[key] = obj
    
#this one returns a list of Categories from the FunctionCategories class
def GetTaskFunctionCategories():
    try:
        f = open("datacache/_categories.pickle", 'rb')
        if not f:
            log("ERROR: Categories pickle missing.", 0)
        obj = pickle.load(f)
        f.close()
        if obj:
            return obj.Categories
        else:
            log("ERROR: Categories pickle could not be read.", 0)
    except Exception:
        log("ERROR: Categories pickle could not be read." + traceback.format_exc(), 0)
        
    return None
        
    # return GetSessionObject("", "function_categories")

#this one returns the Functions dict containing all functions
def GetTaskFunctions():
    try:
        f = open("datacache/_categories.pickle", 'rb')
        if not f:
            log("ERROR: Categories pickle missing.", 0)
        obj = pickle.load(f)
        f.close()
        if obj:
            return obj.Functions
        else:
            log("ERROR: Categories pickle could not be read.", 0)
    except Exception:
        log("ERROR: Categories pickle could not be read." + traceback.format_exc(), 0)
        
    return None
    # return GetSessionObject("", "functions")

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

def HTTPGetNoFail(url):
    """
    This function does not fail.  For any errors it returns an empty result.

    NOTE: this function is called by unauthenticated pages.
    DO NOT use any of the helper functions like uiCommon.log - they look for a user and kick back to the login page 
    if none is found.  (infinite_loop = bad)
    
    That's why we're using log_nouser.
    
    """
    try:
        import socket
        socket.setdefaulttimeout(5)
        
        log_nouser("Trying an HTTP GET to %s" % url, 4)
        if not url:
            return ""
        
        f = urllib2.urlopen(url)
        result = f.read()
        
        # PUT THE SOCKET TIMEOUT BACK! it's global!
        socket.setdefaulttimeout(None)

        if result:
            return result
        else:
            return ""
        
    except Exception:
        log_nouser(traceback.format_exc(), 4)
