import urllib
import uiGlobals
import sys
import json
from catocommon import catocommon

def json_response(content):
    #jQuery ajax in "json" mode expects a json object with a single attribute - "d"
    #so, this wraps content in that construct so we don't need to change a ton of existing javascript
    return "{\"d\":\"%s\"}" % (content.replace("\"", "\\\""))

def getAjaxArg(sArg):
    data = uiGlobals.web.data()
    dic = json.loads(data)
    return dic[sArg]

def AddSecurityLog(db, sUserID, LogType, Action, ObjectType, ObjectID, LogMessage):
    sTrimmedLog = LogMessage.replace("'", "''").replace("\\","\\\\").strip();
    if sTrimmedLog:
        if len(sTrimmedLog) > 7999:
            sTrimmedLog = sTrimmedLog[:7998]
    sSQL = "insert into user_security_log (log_type, action, user_id, log_dt, object_type, object_id, log_msg) \
        values ('" + LogType + "', '" + Action + "', '" + sUserID + "', now(), " + str(ObjectType) + ", '" + ObjectID + "', '" + sTrimmedLog + "')"
    if not db.try_exec_db(sSQL):
        print __name__ + "." + sys._getframe().f_code.co_name + ":: " + db.error

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

def GetCloudProviders(): #These were put in the session at login
    try:
        cp = GetSessionObject("", "cloud_providers")
        if cp:
            return cp
        else:
            ForceLogout("Server Session has expired (1). Please log in again.")
    except Exception as ex:
        raise ex
