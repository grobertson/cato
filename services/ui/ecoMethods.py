import sys
import traceback
import uiGlobals
import uiCommon
from catocommon import catocommon
import ecosystem

# unlike uiCommon, which is used for shared ui elements
# this is a methods class mapped to urls for web.py
# --- we CAN'T instantiate it - that's not how web.py works.
# (apparently it does the instantiation itself, or maybe not - it might just look into it.)
# it expects these classes to have GET and POST methods

class ecoMethods:
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
        except Exception as ex:
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
        except Exception as ex:
            raise ex
        finally:
            if uiGlobals.request:
                if uiGlobals.request.db.conn.socket:
                    uiGlobals.request.db.close()
                uiCommon.log(uiGlobals.request.DumpMessages(), 0)

    def wmGetEcotemplatesTable(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sHTML = ""
            sWhereString = ""
            sFilter = uiCommon.getAjaxArg("sSearch")
            if sFilter:
                aSearchTerms = sFilter.split()
                for term in aSearchTerms:
                    if term:
                        sWhereString += " and (a.ecotemplate_name like '%%" + term + "%%' " \
                            "or a.ecotemplate_desc like '%%" + term + "%%') "
    
            sSQL = "select a.ecotemplate_id, a.ecotemplate_name, a.ecotemplate_desc," \
                " (select count(*) from ecosystem where ecotemplate_id = a.ecotemplate_id) as in_use" \
                " from ecotemplate a" \
                " where 1=1 %s order by a.ecotemplate_name" % sWhereString
            
            rows = uiGlobals.request.db.select_all_dict(sSQL)
    
            if rows:
                for row in rows:
                    sHTML += "<tr ecotemplate_id=\"%s\">" % row["ecotemplate_id"]
                    sHTML += "<td class=\"chkboxcolumn\">"
                    sHTML += "<input type=\"checkbox\" class=\"chkbox\"" \
                    " id=\"chk_%s\"" \
                    " object_id=\"%s\"" \
                    " tag=\"chk\" />" % (row["ecotemplate_id"], row["ecotemplate_id"])
                    sHTML += "</td>"
                    
                    sHTML += "<td class=\"selectable\">%s</td>" % row["ecotemplate_name"]
                    sHTML += "<td class=\"selectable\">%s</td>" % (row["ecotemplate_desc"] if row["ecotemplate_desc"] else "")
                    
                    sHTML += "</tr>"
    
            return sHTML    
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            
    def wmCreateEcotemplate(self):
        try:
            sName = uiCommon.getAjaxArg("sName")
            sDescription = uiCommon.getAjaxArg("sDescription")
            sStormFileSource = uiCommon.getAjaxArg("sStormFileSource")
            sStormFile = uiCommon.getAjaxArg("sStormFile")
    
            et = ecosystem.Ecotemplate()
            et.FromArgs(uiCommon.unpackJSON(sName), uiCommon.unpackJSON(sDescription))
            if et is not None:
                sSrc = uiCommon.unpackJSON(sStormFileSource)
                et.StormFileType = ("URL" if sSrc == "URL" else "Text")
                et.StormFile = uiCommon.unpackJSON(sStormFile)
                
                result, msg = et.DBSave()
                if result:
                    return "{\"ecotemplate_id\" : \"%s\"}" % et.ID
                else:
                    uiGlobals.request.Messages.append(msg)
                    return "{\"info\" : \"%s\"}" % msg
            else:
                return "{\"error\" : \"Unable to create Ecotemplate.\"}"
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
