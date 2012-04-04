import xml.etree.ElementTree as ET
import uiGlobals
import uiCommon
from catocommon import catocommon

#unlike uiCommon, which is used for shared ui elements
# this is a methods class mapped to urls for web.py
# --- we CAN'T instantiate it - that's not how web.py works.
# (apparently it does the instantiation itself, or maybe not - it might just look into it.)
# it expects this class to have GET and POST methods

class uiMethods:
    #the GET method here is hooked by web.py.
    #whatever method is requested, that function is called.
    def GET(self, method):
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
            raise Error("Critical: site_master_xml not cached in session.")
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