import sys
import urllib
import json
import xml.etree.ElementTree as ET
import uiGlobals
import uiCommon
import providers
from catocommon import catocommon

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
        uiGlobals.session.user = user
        
        # reset the user counters and last_login
        sql = "update users set failed_login_attempts=0, last_login_dt=now() where user_id='" + user_id + "'"
        if not db.try_exec_db(sql):
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
        x = ET.parse("../../conf/cloud_providers.xml")
        if x:
            cp = providers.CloudProviders(x)
            uiGlobals.session.cloud_providers = cp
        else:
            raise Exception("Critical: Unable to read/parse cloud_providers.xml.")
        
        
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
    
                    sHTML += "<li class=\"ui-widget-header " + sClass + "\" style=\"cursor: pointer;\">";
                    sHTML += "<a";
                    sHTML += sOnClick ;
                    sHTML += sHref ;
                    sHTML += sTarget ;
                    sHTML += ">";
                    sHTML += sIcon;
                    sHTML += sLabel;
                    sHTML += "</a>";
                    sHTML += "</li>";
                sHTML += "</ul>"
                
            #wrap up the outer menu
            sHTML += "</li>"
        
        return sHTML

    def wmGetCloudAccountsForHeader(self):
        return "<option value=\"foo\">NOT REAL!</option>"

    def wmUpdateHeartbeat(self):
        #NOTE: this needs all the kick and warn stuff
        uid = uiCommon.GetSessionUserID()
        ip = uiCommon.GetSessionObject("user", "ip_address")
        
        if uid and ip:
            sSQL = "update user_session set heartbeat = now() where user_id = '" + uid + "' \
                and address = '" + ip + "'";
            db = catocommon.new_conn()
            if not db.try_exec_db(sSQL):
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
        data = uiGlobals.web.data()
        dic = json.loads(data)
        sFilter = dic["sSearch"]
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
                
                sHTML += "</tr>";

        sHTML += "</table>"    
        return sHTML    

    def wmGetProvidersList(self):
        print "in GPL"
        sHTML = ""
        cp = uiCommon.GetCloudProviders();
        print cp
        if cp:
            print cp.Providers
            for name, p in cp.Providers.iteritems():
                if p.UserDefinedClouds:
                    sHTML += "<option value=\"" + name + "\">" + name + "</option>"
                
        print sHTML
        return sHTML