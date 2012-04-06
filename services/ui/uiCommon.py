import urllib
import uiGlobals
import sys
import json
import uuid
from catocommon import catocommon

def json_response(content):
    #jQuery ajax in "json" mode expects a json object with a single attribute - "d"
    #so, this wraps content in that construct so we don't need to change a ton of existing javascript
    return "{\"d\":\"%s\"}" % (content.replace("\"", "\\\""))

def getAjaxArg(sArg):
    data = uiGlobals.web.data()
    dic = json.loads(data)
    return dic[sArg]

def NewGUID():
    return str(uuid.uuid1())

def TickSlash(s):
    return s.replace("'", "''").replace("\\", "\\\\");


def AddSecurityLog(db, sUserID, LogType, Action, ObjectType, ObjectID, LogMessage):
    sTrimmedLog = LogMessage.replace("'", "''").replace("\\","\\\\").strip();
    if sTrimmedLog:
        if len(sTrimmedLog) > 7999:
            sTrimmedLog = sTrimmedLog[:7998]
    sSQL = "insert into user_security_log (log_type, action, user_id, log_dt, object_type, object_id, log_msg) \
        values ('" + LogType + "', '" + Action + "', '" + sUserID + "', now(), " + str(ObjectType) + ", '" + ObjectID + "', '" + sTrimmedLog + "')"
    if not db.try_exec_db(sSQL):
        print __name__ + "." + sys._getframe().f_code.co_name + ":: " + db.error

def WriteObjectAddLog(db, oType, sObjectID, sObjectName, sLog = ""):
    if sObjectID and sObjectName:
        if not sLog:
            sLog = "Created: [" + TickSlash(sObjectName) + "]."
        else:
            sLog = "Created: [" + TickSlash(sObjectName) + "] - [" + sLog + "]"

        AddSecurityLog(db, GetSessionUserID(), uiGlobals.SecurityLogTypes.Object, uiGlobals.SecurityLogActions.ObjectAdd, oType, sObjectID, sLog)

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
    
    uiGlobals.session.user = None
    print "forcing logout with message: " + sMsg
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
