import sys
import urllib
import json
import xml.etree.ElementTree as ET
import uiGlobals
import uiCommon
from catocommon import catocommon
import task

# task-centric web methods

class taskMethods:
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

    def wmGetTasks(self):
        sHTML = ""
        sWhereString = ""
        sFilter = uiCommon.getAjaxArg("sSearch")
        if sFilter:
            aSearchTerms = sFilter.split()
            for term in aSearchTerms:
                if term:
                    sWhereString += " and (task_name like '%%" + term + "%%' " \
                        "or task_code like '%%" + term + "%%' " \
                        "or task_desc like '%%" + term + "%%' " \
                        "or task_status like '%%" + term + "%%') "

        sSQL = "select task_id, original_task_id, task_name, task_code, task_desc, version, task_status," \
            " (select count(*) from task a where original_task_id = a.original_task_id) as versions" \
            " from task" \
            " where default_version = 1 " + sWhereString + " order by task_code"

        db = catocommon.new_conn()
        rows = db.select_all(sSQL)
        db.close()

        if rows:
            for row in rows:
                sHTML += "<tr task_id=\"" + row[0] + "\">"
                sHTML += "<td class=\"chkboxcolumn\">"
                sHTML += "<input type=\"checkbox\" class=\"chkbox\"" \
                " id=\"chk_" + row[0] + "\"" \
                " object_id=\"" + row[0] + "\"" \
                " tag=\"chk\" />"
                sHTML += "</td>"
                
                sHTML += "<td tag=\"selectable\">" + row[3] +  "</td>"
                sHTML += "<td tag=\"selectable\">" + row[2] +  "</td>"
                sHTML += "<td tag=\"selectable\">" + str(row[5]) +  "</td>"
                sHTML += "<td tag=\"selectable\">" + row[4] +  "</td>"
                sHTML += "<td tag=\"selectable\">" + row[6] +  "</td>"
                sHTML += "<td tag=\"selectable\">" + str(row[7]) +  "</td>"
                
                sHTML += "</tr>"

        return sHTML    

    def wmCreateTask(self):
        sTaskName = uiCommon.unpackJSON(uiCommon.getAjaxArg("sTaskName"))
        sTaskCode = uiCommon.unpackJSON(uiCommon.getAjaxArg("sTaskCode"))
        sTaskDesc = uiCommon.unpackJSON(uiCommon.getAjaxArg("sTaskDesc"))

        print sTaskName + sTaskCode + sTaskDesc

        t = None
        try:
            t = task.Task()
            t.FromArgs(sTaskName, sTaskCode, sTaskDesc)

            if not t.Name:
                return uiCommon.json_response("{\"error\" : \"Unable to create Task.\"}")
            
            bSuccess, sErr = t.DBSave()
            print "~" + str(bSuccess)
            if not bSuccess:
                if sErr:
                    return uiCommon.json_response("{\"info\" : \"" + sErr + "\"}")
                else:
                    return uiCommon.json_response("{\"error\" : \"Unable to save Task.\"}")
            
            return uiCommon.json_response("{\"id\" : \"%s\"}" % (t.ID))
        except Exception, ex:
            raise ex

"""         Task t = new Task(ui.unpackJSON(sTaskName), ui.unpackJSON(sTaskCode), ui.unpackJSON(sTaskDesc));

                //commit it
                if (t.DBSave(ref sErr, null))
                {
                    //success, but was there an error?
                    if (!string.IsNullOrEmpty(sErr))
                        throw new Exception(sErr);
                    
                    return "task_id=" + t.ID;
                }    
                else
                {
                    //failed
                    return sErr;
                }
            }
            catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }
"""