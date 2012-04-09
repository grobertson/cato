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

    def wmDeleteTasks(self):
        try:
            sDeleteArray = uiCommon.getAjaxArg("sDeleteArray")
            if len(sDeleteArray) < 36:
                return uiCommon.json_response("{\"info\" : \"Unable to delete - no selection.\"}")
    
            sDeleteArray = uiCommon.QuoteUp(sDeleteArray)

            db = catocommon.new_conn()
            
            if not sDeleteArray:
                return uiCommon.json_response("{\"info\" : \"Unable to delete - no selection.\"}")
                
            # first we need a list of tasks that will not be deleted
            sSQL = "select task_name from task t " \
                    " where t.original_task_id in (" + sDeleteArray + ")" \
                    " and t.task_id in (select ti.task_id from tv_task_instance ti where ti.task_id = t.task_id)"
            sTaskNames = db.select_csv(sSQL, True)

            # list of tasks that will be deleted
            # we have an array of 'original_task_id' - we need an array of task_id
            sSQL = "select t.task_id from task t " \
                " where t.original_task_id in (" + sDeleteArray + ")" \
                " and t.task_id not in (select ti.task_id from tv_task_instance ti where ti.task_id = t.task_id)"
            print sSQL
            sTaskIDs = db.select_csv(sSQL, True)
            print "!" + sTaskIDs
            if len(sTaskIDs) > 1:
                print "deleting..."
                sSQL = "delete from task_step_user_settings" \
                    " where step_id in" \
                    " (select step_id from task_step where task_id in (" + sTaskIDs + "))"
                if not db.tran_exec_noexcep(sSQL):
                    raise Exception(db.error)
    
                sSQL = "delete from task_step where task_id in (" + sTaskIDs + ")"
                if not db.tran_exec_noexcep(sSQL):
                    raise Exception(db.error)
    
                sSQL = "delete from task_codeblock where task_id in (" + sTaskIDs + ")"
                if not db.tran_exec_noexcep(sSQL):
                    raise Exception(db.error)
    
                sSQL = "delete from task where task_id in (" + sTaskIDs + ")"
                if not db.tran_exec_noexcep(sSQL):
                    raise Exception(db.error)
    
                db.tran_commit()
    
                uiCommon.WriteObjectDeleteLog(db, uiGlobals.CatoObjectTypes.Task, "Multiple", "Original Task IDs", sDeleteArray)
            
            if len(sTaskNames) > 0:
                return uiCommon.json_response("{\"info\" : \"Task(s) (" + sTaskNames + ") have history rows and could not be deleted.\"}")
            
            return uiCommon.json_response("{\"result\" : \"success\"}")
            
        except Exception, ex:
            raise ex
        finally:
            db.close()
