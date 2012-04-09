import sys
import urllib
import json
import xml.etree.ElementTree as ET
import uiGlobals
import uiCommon
import providers
from catocommon import catocommon
import cloud

#unlike uiCommon, which is used for shared ui elements
# this is a methods class mapped to urls for web.py
# --- we CAN'T instantiate it - that's not how web.py works.
# (apparently it does the instantiation itself, or maybe not - it might just look into it.)
# it expects these classes to have GET and POST methods

class login:
    def GET(self):
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
        
        row = db.select_row(sql)
        if not row:
            uiGlobals.server.output("Invalid login attempt - [%s] not a valid user." % (in_name))
            msg = "Invalid Username or Password."
            raise uiGlobals.web.seeother('/static/login.html?msg=' + urllib.quote(msg))

        
        #alrighty, lets check the password
        # we do this by encrypting the form submission and comparing, 
        # NOT by decrypting it here.
        encpwd = catocommon.cato_encrypt(in_pwd)
        
        if row[1] != encpwd:
            uiGlobals.server.output("Invalid login attempt - [%s] bad password." % (in_name))
            msg = "Invalid Username or Password."
            raise uiGlobals.web.seeother('/static/login.html?msg=' + urllib.quote(msg))
            
        user_id = row[0]
        
        #all good, put a few key things in the session
        user = {}
        user["user_id"] = user_id
        user["full_name"] = row[2]
        user["role"] = row[3]
        user["email"] = row[4]
        user["ip_address"] = uiGlobals.web.ctx.ip
        uiCommon.SetSessionObject("user", user)
        #uiGlobals.session.user = user
        print uiGlobals.session.user
        # reset the user counters and last_login
        sql = "update users set failed_login_attempts=0, last_login_dt=now() where user_id='" + user_id + "'"
        if not db.exec_db_noexcep(sql):
            print db.error

        #update the security log
        uiCommon.AddSecurityLog(db, user_id, uiGlobals.SecurityLogTypes.Security, 
            uiGlobals.SecurityLogActions.UserLogin, uiGlobals.CatoObjectTypes.User, "", 
            "Login from [" + uiGlobals.web.ctx.ip + "] granted.")

        db.close()


        #put the site.master.xml in the session here
        # this is a significant boost to performance
        x = ET.parse("site.master.xml")
        if x:
            uiGlobals.session.site_master_xml = x
        else:
            raise Exception("Critical: Unable to read/parse site.master.xml.")

        #put the cloud providers and object types in the session
        # also a big performance boost
        uiCommon.SetCloudProviders()
        
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
                print __name__ + "." + sys._getframe().f_code.co_name + ":: " + db.error
            db.close()
        return uiCommon.json_response("")
    
    def wmGetClouds(self):
        sHTML = ""
        sHTML += "<table class=\"jtable\" cellspacing=\"1\" cellpadding=\"1\" width=\"99%\">"
        sHTML += "<tr>"
        sHTML += "<th class=\"chkboxcolumn\">"
        sHTML += "<input type=\"checkbox\" class=\"chkbox\" id=\"chkAll\" />"
        sHTML += "</th>"           
        sHTML += "<th sortcolumn=\"cloud_name\">Cloud Name</th>"
        sHTML += "<th sortcolumn=\"provider\">Type</th>"
        sHTML += "<th sortcolumn=\"api_protocol\">Protocol</th>"
        sHTML += "<th sortcolumn=\"api_url\">URL</th>"
        sHTML += "</tr>"

        sWhereString = ""
        sFilter = uiCommon.getAjaxArg("sSearch")
        if sFilter:
            aSearchTerms = sFilter.split()
            for term in aSearchTerms:
                if term:
                    sWhereString += " and (cloud_name like '%%" + term + "%%' " \
                        "or provider like '%%" + term + "%%' " \
                        "or api_url like '%%" + term + "%%') "

        sSQL = "select cloud_id, cloud_name, provider, api_url, api_protocol" \
            " from clouds" \
            " where 1=1 " + sWhereString + " order by provider, cloud_name"
        
        db = catocommon.new_conn()
        rows = db.select_all(sSQL)
        db.close()

        if rows:
            for row in rows:
                sHTML += "<tr account_id=\"" + row[0] + "\">"
                sHTML += "<td class=\"chkboxcolumn\">"
                sHTML += "<input type=\"checkbox\" class=\"chkbox\"" \
                " id=\"chk_" + row[0] + "\"" \
                " object_id=\"" + row[0] + "\"" \
                " tag=\"chk\" />"
                sHTML += "</td>"
                
                sHTML += "<td tag=\"selectable\">" + row[1] +  "</td>"
                sHTML += "<td tag=\"selectable\">" + row[2] +  "</td>"
                sHTML += "<td tag=\"selectable\">" + row[3] +  "</td>"
                sHTML += "<td tag=\"selectable\">" + row[4] +  "</td>"
                
                sHTML += "</tr>"

        sHTML += "</table>"    
        return sHTML    

    def wmGetProvidersList(self):
        sHTML = ""
        cp = uiCommon.GetCloudProviders()
        if cp:
            for name, p in cp.Providers.iteritems():
                if p.UserDefinedClouds:
                    sHTML += "<option value=\"" + name + "\">" + name + "</option>"
                
        return sHTML
    
    def wmGetCloud(self):
        try:
            sID = uiCommon.getAjaxArg("sID")
            c = cloud.Cloud()
            if c:
                c.FromID(sID)
                if c.ID:
                    return uiCommon.json_response(c.AsJSON())
            
            #should not get here if all is well
            return "{'result':'fail','error':'Failed to get Cloud details for Cloud ID [" + sID + "].'}"
        except Exception, ex:
            raise ex

    def wmGetCloudAccounts(self):
        try:
            sProvider = uiCommon.getAjaxArg("sProvider")
            ca = cloud.CloudAccounts()
            ca.Fill(sProvider)
            if ca.DataTable:
                return uiCommon.json_response(ca.AsJSON())
            
            #should not get here if all is well
            return "{'result':'fail','error':'Failed to get Cloud Accounts using filter [" + sProvider + "].'}"
        except Exception, ex:
            raise ex

    def wmSaveCloud(self):
        sMode = uiCommon.getAjaxArg("sMode")
        sCloudID = uiCommon.getAjaxArg("sCloudID")
        sCloudName = uiCommon.getAjaxArg("sCloudName")
        sProvider = uiCommon.getAjaxArg("sProvider")
        sAPIUrl = uiCommon.getAjaxArg("sAPIUrl")
        sAPIProtocol = uiCommon.getAjaxArg("sAPIProtocol")

        sErr = ""
        c = None
        try:
            if sMode == "add":
                c, sErr = cloud.Cloud.DBCreateNew(sCloudName, sProvider, sAPIUrl, sAPIProtocol)
                if sErr:
                    return "{\"error\" : \"" + sErr + "\"}"
                if c == None:
                    return "{\"error\" : \"Unable to create Cloud.\"}"
            elif sMode == "edit":
                c = cloud.Cloud()
                c.FromID(sCloudID)
                if c == None:
                    return "{\"error\" : \"Unable to get Cloud using ID [" + sCloudID + "].\"}"
                c.Name = sCloudName
                c.APIProtocol = sAPIProtocol
                c.APIUrl = sAPIUrl
                #get a new provider by name
                c.Provider = providers.Provider.GetFromSession(sProvider)
                if not c.DBUpdate():
                    raise Exception(sErr)
            
            if c:
                return uiCommon.json_response(c.AsJSON())
            else:
                return "{\"error\" : \"Unable to save Cloud using mode [" + sMode + "].\"}"
        except Exception, ex:
            raise ex

    def wmDeleteClouds(self):
        try:
            sDeleteArray = uiCommon.getAjaxArg("sDeleteArray")
            if len(sDeleteArray) < 36:
                return uiCommon.json_response("")
    
            sDeleteArray = uiCommon.QuoteUp(sDeleteArray)
            
            #get important data that will be deleted for the log
            sSQL = "select cloud_id, cloud_name, provider from clouds where cloud_id in (" + sDeleteArray + ")"
            db = catocommon.new_conn()
            rows = db.select_all(sSQL)

            sSQL = "delete from clouds where cloud_id in (" + sDeleteArray + ")"
            if not db.tran_exec_noexcep(sSQL):
                raise Exception(db.error)
            
            #reget the cloud providers class in the session
            uiCommon.SetCloudProviders()

            #if we made it here, save the logs
            for dr in rows:
                uiCommon.WriteObjectDeleteLog(db, uiGlobals.CatoObjectTypes.Cloud, dr[0], dr[1], dr[2] + " Cloud Deleted.")
    
            return uiCommon.json_response("")
            
        except Exception, ex:
            raise ex
        finally:
            db.close()