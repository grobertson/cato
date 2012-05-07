import sys
import traceback
import uiGlobals
import uiCommon
import providers
from catocommon import catocommon
import cloud

# methods for dealing with clouds and cloud accounts

class cloudMethods:
    #the GET and POST methods here are hooked by web.py.
    #whatever method is requested, that function is called.
    def GET(self, method):
        try:
            # EVERY new HTTP request sets up the "request" in uiGlobals.
            # ALL functions chained from this HTTP request handler share that request
            uiGlobals.request = uiGlobals.Request(catocommon.new_conn())
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            methodToCall = getattr(self, method)
            result = methodToCall()
            return result
        except Exception, ex:
            raise ex
        finally:
            if uiGlobals.request:
                if uiGlobals.request.db.conn.socket:
                    uiGlobals.request.db.close()
                uiCommon.log(uiGlobals.request.DumpMessages(), 0)

    def POST(self, method):
        try:
            # EVERY new HTTP request sets up the "request" in uiGlobals.
            # ALL functions chained from this HTTP request handler share that request
            uiGlobals.request = uiGlobals.Request(catocommon.new_conn())
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            methodToCall = getattr(self, method)
            result = methodToCall()
            return result
        except Exception, ex:
            raise ex
            return traceback.format_exc()
        finally:
            if uiGlobals.request:
                if uiGlobals.request.db.conn.socket:
                    uiGlobals.request.db.close()
                uiCommon.log(uiGlobals.request.DumpMessages(), 0)

    """ Clouds edit page """
    def wmGetCloudsTable(self):
        try:
            sHTML = ""
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
            
            rows = uiGlobals.request.db.select_all_dict(sSQL)
            if uiGlobals.request.db.error:
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
    
            if rows:
                for row in rows:
                    sHTML += "<tr cloud_id=\"" + row["cloud_id"] + "\">"
                    sHTML += "<td class=\"chkboxcolumn\">"
                    sHTML += "<input type=\"checkbox\" class=\"chkbox\"" \
                    " id=\"chk_" + row["cloud_id"] + "\"" \
                    " object_id=\"" + row["cloud_id"] + "\"" \
                    " tag=\"chk\" />"
                    sHTML += "</td>"
                    
                    sHTML += "<td class=\"selectable\">" + row["cloud_name"] +  "</td>"
                    sHTML += "<td class=\"selectable\">" + row["provider"] +  "</td>"
                    sHTML += "<td class=\"selectable\">" + row["api_url"] +  "</td>"
                    sHTML += "<td class=\"selectable\">" + row["api_protocol"] +  "</td>"
                    
                    sHTML += "</tr>"
    
            return sHTML    
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()

    def wmGetProvidersList(self):
        try:
            sUserDefinedOnly = uiCommon.getAjaxArg("sUserDefinedOnly")
            sHTML = ""
            cp = uiCommon.GetCloudProviders()
            if cp:
                for name, p in cp.Providers.iteritems():
                    if uiCommon.IsTrue(sUserDefinedOnly):
                        if p.UserDefinedClouds:
                            sHTML += "<option value=\"" + name + "\">" + name + "</option>"
                    else:
                        sHTML += "<option value=\"" + name + "\">" + name + "</option>"
    
                    
            return sHTML
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()
    
    def wmGetCloud(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sID = uiCommon.getAjaxArg("sID")
            c = cloud.Cloud()
            if c:
                c.FromID(sID)
                if c.ID:
                    return c.AsJSON()
            
            #should not get here if all is well
            return "{'result':'fail','error':'Failed to get Cloud details for Cloud ID [" + sID + "].'}"
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()

    def wmGetCloudAccounts(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            provider = uiCommon.getAjaxArg("sProvider")
            ca = cloud.CloudAccounts()
            ca.Fill(sFilter="", sProvider=provider)
            if ca.DataTable:
                return ca.AsJSON()
            
            #should not get here if all is well
            return "{'result':'fail','error':'Failed to get Cloud Accounts using filter [" + provider + "].'}"
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()

    def wmSaveCloud(self):
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
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

                uiCommon.WriteObjectAddLog(uiGlobals.CatoObjectTypes.Cloud, c.ID, c.Name, "Cloud Created")
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
                    uiGlobals.request.Messages.append(sErr)
                
                uiCommon.WriteObjectPropertyChangeLog(uiGlobals.CatoObjectTypes.Cloud, self.ID, self.Name, sCloudName, self.Name)

            if c:
                return c.AsJSON()
            else:
                return "{\"error\" : \"Unable to save Cloud using mode [" + sMode + "].\"}"
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()

    def wmDeleteClouds(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sDeleteArray = uiCommon.getAjaxArg("sDeleteArray")
            if len(sDeleteArray) < 36:
                return "{\"info\" : \"Unable to delete - no selection.\"}"
    
            sDeleteArray = uiCommon.QuoteUp(sDeleteArray)
            
            #get important data that will be deleted for the log
            sSQL = "select cloud_id, cloud_name, provider from clouds where cloud_id in (" + sDeleteArray + ")"
            rows = uiGlobals.request.db.select_all(sSQL)

            sSQL = "delete from clouds where cloud_id in (" + sDeleteArray + ")"
            if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
            
            #reget the cloud providers class in the session
            uiCommon.SetCloudProviders()

            #if we made it here, save the logs
            for dr in rows:
                uiCommon.WriteObjectDeleteLog(uiGlobals.CatoObjectTypes.Cloud, dr[0], dr[1], dr[2] + " Cloud Deleted.")
    
            return "{\"result\" : \"success\"}"
            
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()

        
    """ Cloud Accounts Edit page"""
    def wmGetCloudAccountsTable(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sFilter = uiCommon.getAjaxArg("sSearch")
            sHTML = ""
            
            ca = cloud.CloudAccounts()
            ca.Fill(sFilter)
            if ca.DataTable:
                for row in ca.DataTable:
                    sHTML += "<tr account_id=\"" + row["account_id"] + "\">"
                    
                    if row["has_ecosystems"]:
                        sHTML += "<td class=\"chkboxcolumn\">"
                        sHTML += "<input type=\"checkbox\" class=\"chkbox\"" \
                        " id=\"chk_" + row["account_id"] + "\"" \
                        " object_id=\"" + row["account_id"] + "\"" \
                        " tag=\"chk\" />"
                        sHTML += "</td>"
                    else:
                        sHTML += "<td>"
                        sHTML += "<span class=\"ui-icon ui-icon-info forceinline account_help_btn\"" \
                            " title=\"This account has associated Ecosystems and cannot be deleted.\"></span>"
                        sHTML += "</td>"
                    
                    sHTML += "<td class=\"selectable\">" + row["account_name"] +  "</td>"
                    sHTML += "<td class=\"selectable\">" + row["account_number"] +  "</td>"
                    sHTML += "<td class=\"selectable\">" + row["provider"] +  "</td>"
                    sHTML += "<td class=\"selectable\">" + row["login_id"] +  "</td>"
                    sHTML += "<td class=\"selectable\">" + row["is_default"] +  "</td>"
                    
                    sHTML += "</tr>"

            return sHTML    
            
            #should not get here if all is well
            return "{'result':'fail','error':'Failed to get Cloud Accounts using filter [" + sFilter + "].'}"
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()

    def wmGetCloudAccount(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sID = uiCommon.getAjaxArg("sID")
            a = cloud.CloudAccount()
            if a:
                a.FromID(sID)
                if a.ID:
                    return a.AsJSON()
            
            #should not get here if all is well
            return "{'result':'fail','error':'Failed to get details for Cloud Account [" + sID + "].'}"
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()

    def wmGetKeyPairs(self):
        try:
            sID = uiCommon.getAjaxArg("sID")
            sHTML = ""
    
            sSQL = "select keypair_id, keypair_name, private_key, passphrase" \
                " from cloud_account_keypair" \
                " where account_id = '" + sID + "'"
    
            dt = uiGlobals.request.db.select_all_dict(sSQL)
            if uiGlobals.request.db.error:
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
    
            if dt:
                sHTML += "<ul>"
                for dr in dt:
                    sName = dr["keypair_name"]
    
                    # DO NOT send these back to the client.
                    sPK = ("false" if not dr["private_key"] else "true")
                    sPP = ("false" if not dr["passphrase"] else "true")
                    # sLoginPassword = "($%#d@x!&"
    
                    sHTML += "<li class=\"ui-widget-content ui-corner-all keypair\" id=\"kp_" + dr["keypair_id"] + "\" has_pk=\"" + sPK + "\" has_pp=\"" + sPP + "\">"
                    sHTML += "<span class=\"keypair_label pointer\">" + sName + "</span>"
                    sHTML += "<span class=\"keypair_icons pointer\"><img src=\"static/images/icons/fileclose.png\" class=\"keypair_delete_btn\" /></span>"
                    sHTML += "</li>"
                sHTML += "</ul>"
            else:
                sHTML += ""
    
            return sHTML
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()

    