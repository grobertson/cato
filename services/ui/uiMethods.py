import sys
import urllib
import json
import xml.etree.ElementTree as ET
import uiGlobals
import uiCommon
from catocommon import catocommon

# unlike uiCommon, which is used for shared ui elements
# this is a methods class mapped to urls for web.py
# --- we CAN'T instantiate it - that's not how web.py works.
# (apparently it does the instantiation itself, or maybe not - it might just look into it.)
# it expects these classes to have GET and POST methods

# these are generic ui web methods, and stuff that's not enough to need it's own file.
class login:
    def GET(self):
        # visiting the login page kills the session
        uiGlobals.session.kill()
        
        qs = ""
        i = uiGlobals.web.input(msg=None)
        if i.msg:
            qs = "?msg=" + urllib.quote(i.msg)
        raise uiGlobals.web.seeother('/static/login.html' + qs)

    def POST(self):
        in_name = uiGlobals.web.input(username=None).username
        in_pwd = uiGlobals.web.input(password=None).password

        db = catocommon.new_conn()
        sql = "select user_id, user_password, full_name, user_role, email, status, failed_login_attempts, expiration_dt, force_change \
            from users where username='" + in_name + "'"
        
        row = db.select_row_dict(sql)
        if not row:
            uiGlobals.server.output("Invalid login attempt - [%s] not a valid user." % (in_name))
            msg = "Invalid Username or Password."
            raise uiGlobals.web.seeother('/static/login.html?msg=' + urllib.quote(msg))

        
        #alrighty, lets check the password
        # we do this by encrypting the form submission and comparing, 
        # NOT by decrypting it here.
        encpwd = catocommon.cato_encrypt(in_pwd)
        
        if row["user_password"] != encpwd:
            uiGlobals.server.output("Invalid login attempt - [%s] bad password." % (in_name))
            msg = "Invalid Username or Password."
            raise uiGlobals.web.seeother('/static/login.html?msg=' + urllib.quote(msg))
            
        user_id = row["user_id"]
        
        #all good, put a few key things in the session
        user = {}
        user["user_id"] = user_id
        user["full_name"] = row["full_name"]
        user["role"] = row["user_role"]
        user["email"] = row["email"]
        user["ip_address"] = uiGlobals.web.ctx.ip
        uiCommon.SetSessionObject("user", user)
        #uiGlobals.session.user = user
        uiCommon.log("Login granted for: ", 4)
        uiCommon.log(uiGlobals.session.user, 4)
        # reset the user counters and last_login
        sql = "update users set failed_login_attempts=0, last_login_dt=now() where user_id='" + user_id + "'"
        if not db.exec_db_noexcep(sql):
            uiCommon.log(db.error, 0)

        #update the security log
        uiCommon.AddSecurityLog(db, user_id, uiGlobals.SecurityLogTypes.Security, 
            uiGlobals.SecurityLogActions.UserLogin, uiGlobals.CatoObjectTypes.User, "", 
            "Login from [" + uiGlobals.web.ctx.ip + "] granted.")

        db.close()

        uiCommon.log("Creating session...", 3)
        #put the site.master.xml in the session here
        # this is a significant boost to performance
        x = ET.parse("site.master.xml")
        if x:
            uiGlobals.session.site_master_xml = x
        else:
            raise Exception("Critical: Unable to read/parse site.master.xml.")


        uiCommon.log("Refreshing datacache...", 3)
        #put the cloud providers and object types in a pickle
        # also a big performance boost
        uiCommon.SetCloudProviders()
        
        #put the task commands in a pickle
        # another big performance boost
        uiCommon.SetTaskCommands()
        
        raise uiGlobals.web.seeother('/home')


class logout:        
    def GET(self):
        i = uiGlobals.web.input(msg=None)
        msg = "User Logged out."
        if i.msg:
            msg = i.msg
        uiCommon.ForceLogout(msg)

class uiMethods:
    #the GET and POST methods here are hooked by web.py.
    #whatever method is requested, that function is called.
    def GET(self, method):
        try:
            methodToCall = getattr(self, method)
            result = methodToCall()
            return result
        except Exception as ex:
            raise ex

    def POST(self, method):
        try:
            methodToCall = getattr(self, method)
            result = methodToCall()
            return result
        except Exception as ex:
            raise ex

    def wmGetMenu(self):
        sHTML = ""
        xRoot = uiCommon.GetSessionObject("", "site_master_xml")
        if not xRoot:
            raise Exception("Critical: site_master_xml not cached in session.")
        xMenus = xRoot.findall("mainmenu/menu") 
        for xMenu in xMenus:
            sLabel = xMenu.get("label", "No Label Defined")
            sHref = " href=\"" + xMenu.get("href", "") + "\""
            sOnClick = " onclick=\"" + xMenu.get("onclick", "") + "\""
            sTarget = xMenu.get("target", "")
            sIcon = "<img src=\"" + xMenu.get("icon", "") + "\" alt=\"\" />"
            sClass = xMenu.get("class", "")
            
            sHTML += "<li class=\"" + sClass + "\" style=\"cursor: pointer;\">"
            sHTML += "<a"
            sHTML += sOnClick
            sHTML += sHref
            sHTML += sTarget
            sHTML += ">"
            sHTML += sIcon
            sHTML += sLabel
            sHTML += "</a>"
            
            xItems = xMenu.findall("item")
            if str(len(xItems)) > 0:
                sHTML += "<ul>"
                for xItem in xItems:
                    sLabel = xItem.get("label", "No Label Defined")
                    sHref = " href=\"" + xItem.get("href", "") + "\""
                    sOnClick = " onclick=\"" + xItem.get("onclick", "") + "\""
                    sTarget = xItem.get("target", "")
                    sIcon = "<img src=\"" + xItem.get("icon", "") + "\" alt=\"\" />"
                    sClass = xItem.get("class", "")
    
                    sHTML += "<li class=\"ui-widget-header " + sClass + "\" style=\"cursor: pointer;\">"
                    sHTML += "<a"
                    sHTML += sOnClick 
                    sHTML += sHref 
                    sHTML += sTarget 
                    sHTML += ">"
                    sHTML += sIcon
                    sHTML += sLabel
                    sHTML += "</a>"
                    sHTML += "</li>"
                sHTML += "</ul>"
                
            #wrap up the outer menu
            sHTML += "</li>"
        
        return sHTML

    def wmGetCloudAccountsForHeader(self):
        try:
            #Gotta get this list from the list stored in the session.
            # or, quit using session and read from the db each time (preferred)
            
            #this should select the active one in the session
            """sHTML = ""
            ca = cloud.CloudAccounts()
            ca.Fill("")
            print ca.DataTable
            if ca.DataTable:
                for row in ca.DataTable:
                    sHTML +=  "<option value=\"%s\">%s</option>" % (row[0], row[1])

                return sHTML
            
            #should not get here if all is well
            return "<option>ERROR</option>"
            """
            return "<option>NOT REAL!</option>"
        except Exception, ex:
            raise ex

    def wmUpdateHeartbeat(self):
        #NOTE: this needs all the kick and warn stuff
        uid = uiCommon.GetSessionUserID()
        ip = uiCommon.GetSessionObject("user", "ip_address")
        
        if uid and ip:
            sSQL = "update user_session set heartbeat = now() where user_id = '" + uid + "' \
                and address = '" + ip + "'"
            db = catocommon.new_conn()
            if not db.exec_db_noexcep(sSQL):
                uiCommon.log(__name__ + "." + sys._getframe().f_code.co_name + ":: " + db.error, 2)
            db.close()
        return ""
    
    def wmGetSystemStatus(self):
        try:
            db = catocommon.new_conn()
    
            sProcessHTML = ""
            sSQL = "select app_instance as Instance," \
                " app_name as Component," \
                " heartbeat as Heartbeat," \
                " case master when 1 then 'Yes' else 'No' end as Enabled," \
                " timestampdiff(MINUTE, heartbeat, now()) as mslr," \
                " load_value as LoadValue, platform, hostname" \
                " from application_registry " \
                " order by component, master desc"
            rows = db.select_all(sSQL)
            for dr in rows:
                sProcessHTML += "<tr>" \
                    "<td>" + str((dr[0] if dr[0] else "")) + "</td>" \
                    "<td>" + str((dr[1] if dr[1] else "")) + "</td>" \
                    "<td>" + str((dr[2] if dr[2] else "")) + "</td>" \
                    "<td>" + str((dr[3] if dr[3] else "")) + "</td>" \
                    "<td>" + str((dr[4] if dr[4] else "")) + "</td>" \
                    "<td>" + str((dr[5] if dr[5] else "")) + "</td>" \
                    "</tr>"

            sUserHTML = ""
            sSQL = "select u.full_name, us.login_dt, us.heartbeat as last_update, us.address," \
                " case when us.kick = 0 then 'Active' when us.kick = 1 then 'Warning' " \
                " when us.kick = 2 then 'Kicking' when us.kick = 3 then 'Inactive' end as 'kick' " \
                " from user_session us join users u on u.user_id = us.user_id " \
                " where timestampdiff(MINUTE,us.heartbeat, now()) < 10" \
                " order by us.heartbeat desc"
            rows = db.select_all(sSQL)
            for dr in rows:
                sUserHTML += "<tr>" \
                    "<td>" + str((dr[0] if dr[0] else "")) + "</td>" \
                    "<td>" + str((dr[1] if dr[1] else "")) + "</td>" \
                    "<td>" + str((dr[2] if dr[2] else "")) + "</td>" \
                    "<td>" + str((dr[3] if dr[3] else "")) + "</td>" \
                    "<td>" + str((dr[4] if dr[4] else "")) + "</td>" \
                    "</tr>"
                    
            sMessageHTML = ""
            sSQL = "select msg_to, msg_subject," \
                " case status when 0 then 'Queued' when 1 then 'Error' when 2 then 'Success' end as status," \
                " error_message," \
                " convert(date_time_entered, CHAR(20)) as entered_dt, convert(date_time_completed, CHAR(20)) as completed_dt" \
                " from message" \
                " order by msg_id desc limit 100"
            rows = db.select_all(sSQL)
            for dr in rows:
                sMessageHTML += "<tr>" \
                    "<td>" + str((dr[0] if dr[0] else "")) + "</td>" \
                    "<td>" + str((dr[1] if dr[1] else "")) + "</td>" \
                    "<td>" + str((dr[2] if dr[2] else "")) + "</td>" \
                    "<td>" + str((dr[3] if dr[3] else "")) + "</td>" \
                    "<td>" + str((dr[4] if dr[4] else "")) + "<br />" + str((dr[5] if dr[5] else "")) + "</td>" \
                    "</tr>"
                    
            
            return "{ \"processes\" : \"%s\", \"users\" : \"%s\", \"messages\" : \"%s\" }" % (sProcessHTML, sUserHTML, sMessageHTML)

        except Exception, ex:
            raise ex
        finally:
            db.close()

        