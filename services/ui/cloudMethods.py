import sys
import urllib
import json
import xml.etree.ElementTree as ET
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

    def wmGetClouds(self):
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
        
        db = catocommon.new_conn()
        rows = db.select_all_dict(sSQL)
        db.close()

        if rows:
            for row in rows:
                sHTML += "<tr account_id=\"" + row["cloud_id"] + "\">"
                sHTML += "<td class=\"chkboxcolumn\">"
                sHTML += "<input type=\"checkbox\" class=\"chkbox\"" \
                " id=\"chk_" + row["cloud_id"] + "\"" \
                " object_id=\"" + row["cloud_id"] + "\"" \
                " tag=\"chk\" />"
                sHTML += "</td>"
                
                sHTML += "<td tag=\"selectable\">" + row["cloud_name"] +  "</td>"
                sHTML += "<td tag=\"selectable\">" + row["provider"] +  "</td>"
                sHTML += "<td tag=\"selectable\">" + row["api_url"] +  "</td>"
                sHTML += "<td tag=\"selectable\">" + row["api_protocol"] +  "</td>"
                
                sHTML += "</tr>"

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
            return uiCommon.json_response("{'result':'fail','error':'Failed to get Cloud details for Cloud ID [" + sID + "].'}")
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
            return uiCommon.json_response("{'result':'fail','error':'Failed to get Cloud Accounts using filter [" + sProvider + "].'}")
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
                    return uiCommon.json_response("{\"error\" : \"" + sErr + "\"}")
                if c == None:
                    return "{\"error\" : \"Unable to create Cloud.\"}"
            elif sMode == "edit":
                c = cloud.Cloud()
                c.FromID(sCloudID)
                if c == None:
                    return uiCommon.json_response("{\"error\" : \"Unable to get Cloud using ID [" + sCloudID + "].\"}")
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
                return uiCommon.json_response("{\"error\" : \"Unable to save Cloud using mode [" + sMode + "].\"}")
        except Exception, ex:
            raise ex

    def wmDeleteClouds(self):
        try:
            sDeleteArray = uiCommon.getAjaxArg("sDeleteArray")
            if len(sDeleteArray) < 36:
                return uiCommon.json_response("{\"info\" : \"Unable to delete - no selection.\"}")
    
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
    
            return uiCommon.json_response("{\"result\" : \"success\"}")
            
        except Exception, ex:
            raise ex
        finally:
            db.close()

        
