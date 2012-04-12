import sys
import urllib
import json
import xml.etree.ElementTree as ET
import uiGlobals
import uiCommon
from catocommon import catocommon
import task
import stepTemplates as ST

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
                    sWhereString += " and (a.task_name like '%%" + term + "%%' " \
                        "or a.task_code like '%%" + term + "%%' " \
                        "or a.task_desc like '%%" + term + "%%' " \
                        "or a.task_status like '%%" + term + "%%') "

        sSQL = "select a.task_id, a.original_task_id, a.task_name, a.task_code, a.task_desc, a.version, a.task_status," \
            " (select count(*) from task where original_task_id = a.original_task_id) as versions" \
            " from task a" \
            " where a.default_version = 1 " + sWhereString + " order by a.task_code"
        
        db = catocommon.new_conn()
        rows = db.select_all_dict(sSQL)
        db.close()

        if rows:
            for row in rows:
                sHTML += "<tr task_id=\"" + row["task_id"] + "\">"
                sHTML += "<td class=\"chkboxcolumn\">"
                sHTML += "<input type=\"checkbox\" class=\"chkbox\"" \
                " id=\"chk_" + row["original_task_id"] + "\"" \
                " object_id=\"" + row["task_id"] + "\"" \
                " tag=\"chk\" />"
                sHTML += "</td>"
                
                sHTML += "<td tag=\"selectable\">" + row["task_code"] +  "</td>"
                sHTML += "<td tag=\"selectable\">" + row["task_name"] +  "</td>"
                sHTML += "<td tag=\"selectable\">" + str(row["version"]) +  "</td>"
                sHTML += "<td tag=\"selectable\">" + row["task_desc"] +  "</td>"
                sHTML += "<td tag=\"selectable\">" + row["task_status"] +  "</td>"
                sHTML += "<td tag=\"selectable\">" + str(row["versions"]) +  "</td>"
                
                sHTML += "</tr>"

        return sHTML    

    def wmGetTask(self):
        try:
            sID = uiCommon.getAjaxArg("sTaskID")
            t, sErr = task.Task.FromID(sID)
            if sErr:
                uiCommon.log(sErr, 2)
            if t:
                if t.ID:
                    return t.AsJSON()
            
            #should not get here if all is well
            return "{'result':'fail','error':'Failed to get Task details for Task ID [" + sID + "].'}"
        except Exception, ex:
            raise ex

    def wmGetTaskCodeFromID(self):
            sOriginalTaskID = uiCommon.getAjaxArg("sOriginalTaskID")

            if not uiCommon.IsGUID(sOriginalTaskID.replace("'", "")):
                raise Exception("Invalid or missing Task ID.")

            try:
                db = catocommon.new_conn()
                sSQL = "select task_code from task where original_task_id = '" + sOriginalTaskID + "' and default_version = 1"
                sTaskCode = db.select_col_noexcep(sSQL)
                if not sTaskCode:
                    if db.error:
                        raise Exception("Unable to get task code." + db.error)
                    else:
                        return ""
                else:
                    return "{\"code\" : \"%s\"}" % (sTaskCode)
            except Exception, ex:
                raise(ex)
    
    def wmGetTaskVersionsDropdown(self):
        try:
            sOriginalTaskID = uiCommon.getAjaxArg("sOriginalTaskID")
            db = catocommon.new_conn()
            sbString = []
            sSQL = "select task_id, version, default_version" \
                " from task " \
                " where original_task_id = '" + sOriginalTaskID + "'" \
                " order by default_version desc, version"
            dt = db.select_all_dict(sSQL)
            if not dt:
                raise Exception("Error selecting versions: " + db.error)
            else:
                for dr in dt:
                    sLabel = str(dr["version"]) + (" (default)" if dr["default_version"] == 1 else "")
                    sbString.append("<option value=\"" + dr["task_id"] + "\">" + sLabel + "</option>")

                return "".join(sbString)
        except Exception, ex:
            raise (ex)
    
    def wmCreateTask(self):
        sTaskName = uiCommon.unpackJSON(uiCommon.getAjaxArg("sTaskName"))
        sTaskCode = uiCommon.unpackJSON(uiCommon.getAjaxArg("sTaskCode"))
        sTaskDesc = uiCommon.unpackJSON(uiCommon.getAjaxArg("sTaskDesc"))

        t = None
        try:
            t = task.Task()
            t.FromArgs(sTaskName, sTaskCode, sTaskDesc)

            if not t.Name:
                return "{\"error\" : \"Unable to create Task.\"}"
            
            bSuccess, sErr = t.DBSave()
            if not bSuccess:
                if sErr:
                    return "{\"info\" : \"" + sErr + "\"}"
                else:
                    return "{\"error\" : \"Unable to save Task.\"}"
            
            return "{\"id\" : \"%s\"}" % (t.ID)
        except Exception, ex:
            raise ex

    def wmCopyTask(self):
        sCopyTaskID = uiCommon.getAjaxArg("sCopyTaskID")
        sTaskName = uiCommon.getAjaxArg("sTaskName")
        sTaskCode =uiCommon.getAjaxArg("sTaskCode")

        try:
            t, sErr = task.Task.FromID(sCopyTaskID)
            if not t:
                return "{\"error\" : \"Unable to build Task object from ID [" + sCopyTaskID + "].\"}"
            
            sNewTaskID = t.Copy(0, sTaskName, sTaskCode)
            if not sNewTaskID:
                return "Unable to create Task."
            
            return "{\"id\" : \"%s\"}" % (sNewTaskID)
        except Exception, ex:
            raise ex

    def wmDeleteTasks(self):
        try:
            sDeleteArray = uiCommon.getAjaxArg("sDeleteArray")
            if len(sDeleteArray) < 36:
                return "{\"info\" : \"Unable to delete - no selection.\"}"
    
            sDeleteArray = uiCommon.QuoteUp(sDeleteArray)

            db = catocommon.new_conn()
            
            if not sDeleteArray:
                return "{\"info\" : \"Unable to delete - no selection.\"}"
                
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
            sTaskIDs = db.select_csv(sSQL, True)
            if len(sTaskIDs) > 1:
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
                return "{\"info\" : \"Task(s) (" + sTaskNames + ") have history rows and could not be deleted.\"}"
            
            return "{\"result\" : \"success\"}"
            
        except Exception, ex:
            raise ex
        finally:
            db.close()

    def wmGetCodeblocks(self):
        try:
            sTaskID = uiCommon.getAjaxArg("sTaskID")
            if len(sTaskID) < 36:
                return "Unable to get Codeblocks - invalid Task ID."
            sErr = ""
            #instantiate the new Task object
            oTask, sErr = task.Task.FromID(sTaskID, False)
            if sErr:
                uiCommon.log(sErr, 2)
            if not oTask:
                return "wmGetCodeblocks: Unable to get Task for ID [" + sTaskID + "]. " + sErr
            sCBHTML = ""
            for name, cb in oTask.Codeblocks.iteritems():
                #if it's a guid it's a bogus codeblock (for export only)
                if uiCommon.IsGUID(cb.Name):
                    continue
                sCBHTML += "<li class=\"ui-widget-content codeblock\" id=\"cb_" + cb.Name + "\">"
                sCBHTML += "<div>"
                sCBHTML += "<div class=\"codeblock_title\" name=\"" + cb.Name + "\">"
                sCBHTML += "<span>" + cb.Name + "</span>"
                sCBHTML += "</div>"
                sCBHTML += "<div class=\"codeblock_icons pointer\">"
                sCBHTML += "<span id=\"codeblock_rename_btn_" + cb.Name + "\">"
                sCBHTML += "<img class=\"codeblock_rename\" codeblock_name=\"" + cb.Name + "\""
                sCBHTML += " src=\"static/images/icons/edit_16.png\" alt=\"\" /></span><span class=\"codeblock_copy_btn\""
                sCBHTML += " codeblock_name=\"" + cb.Name + "\">"
                sCBHTML += "<img src=\"static/images/icons/editcopy_16.png\" alt=\"\" /></span><span id=\"codeblock_delete_btn_" + cb.Name + "\""
                sCBHTML += " class=\"codeblock_delete_btn codeblock_icon_delete\" remove_id=\"" + cb.Name + "\">"
                sCBHTML += "<img src=\"static/images/icons/fileclose.png\" alt=\"\" /></span>"
                sCBHTML += "</div>"
                sCBHTML += "</div>"
                sCBHTML += "</li>"
            return sCBHTML
        except Exception, ex:
            return ex
        
    def wmGetSteps(self):
        try:
            sTaskID = uiCommon.getAjaxArg("sTaskID")
            sCodeblockName = uiCommon.getAjaxArg("sCodeblockName")
            if len(sTaskID) < 36:
                return "Unable to get Steps - invalid Task ID."
            if not sCodeblockName:
                return "Unable to get Steps - No Codeblock specified."

            sAddHelpMsg =  "No Commands have been defined in this Codeblock. Drag a Command here to add it."
            sErr = ""
            #instantiate the new Task object
            oTask, sErr = task.Task.FromID(sTaskID, True)
            if sErr:
                uiCommon.log(sErr, 2)
            if not oTask:
                return "wmGetSteps: Unable to get Task for ID [" + sTaskID + "]. " + sErr

            sHTML = ""

            cb = oTask.Codeblocks[sCodeblockName]
            if cb.Steps:
                # we always need the no_step item to be there, we just hide it if we have other items
                # it will get unhidden if someone deletes the last step.
                sHTML = "<li id=\"no_step\" class=\"ui-widget-content ui-corner-all ui-state-active ui-droppable no_step hidden\">" + sAddHelpMsg + "</li>"
        
                for order, step in sorted(cb.Steps.iteritems()):
                    sHTML += ST.DrawFullStep(step)
            else:
                sHTML = "<li id=\"no_step\" class=\"ui-widget-content ui-corner-all ui-state-active ui-droppable no_step\">" + sAddHelpMsg + "</li>"
                    
            return sHTML
        except Exception, ex:
            return ex
        
    def wmToggleStepCommonSection(self):
        # no exceptions, just a log message if there are problems.
        try:
            sStepID = uiCommon.getAjaxArg("sStepID")
            sButton = uiCommon.getAjaxArg("sButton")
            db = catocommon.new_conn()
            print sStepID
            if uiCommon.IsGUID(sStepID):
                sUserID = uiCommon.GetSessionUserID()
                sButton = ("null" if sButton == "" else "'" + sButton + "'")
    
                #is there a row?
                iRowCount = db.select_col_noexcep("select count(*) from task_step_user_settings" \
                    " where user_id = '" + sUserID + "'" \
                    " and step_id = '" + sStepID + "'")
                if iRowCount == 0:
                    sSQL = "insert into task_step_user_settings" \
                        " (user_id, step_id, visible, breakpoint, skip, button)" \
                        " values ('" + sUserID + "','" + sStepID + "', 1, 0, 0, " + sButton + ")"
                else:
                    sSQL = "update task_step_user_settings set button = " + sButton + " where step_id = '" + sStepID + "'"

                if not db.exec_db_noexcep(sSQL):
                    uiCommon.log("Unable to toggle step button [" + sStepID + "]." + db.error, 2)

                return ""
            else:
                uiCommon.log("Unable to toggle step button. Missing or invalid step_id.", 2)
        except Exception, ex:
            raise ex
        finally:
            db.close()
            
    def wmToggleStep(self):
        # no exceptions, just a log message if there are problems.
        try:
            sStepID = uiCommon.getAjaxArg("sStepID")
            sVisible = uiCommon.getAjaxArg("sVisible")
            
            db = catocommon.new_conn()
            if uiCommon.IsGUID(sStepID):
                sUserID = uiCommon.GetSessionUserID()

                sVisible = ("1" if sVisible == "1" else "0")
    
                #is there a row?
                iRowCount = db.select_col_noexcep("select count(*) from task_step_user_settings" \
                    " where user_id = '" + sUserID + "'" \
                    " and step_id = '" + sStepID + "'")
                if iRowCount == 0:
                    sSQL = "insert into task_step_user_settings" \
                        " (user_id, step_id, visible, breakpoint, skip)" \
                        " values ('" + sUserID + "','" + sStepID + "', " + sVisible + ", 0, 0)"
                else:
                    sSQL = "update task_step_user_settings set visible = '" + sVisible + "' where step_id = '" + sStepID + "'"

                if not db.exec_db_noexcep(sSQL):
                    uiCommon.log("Unable to toggle step visibility [" + sStepID + "]." + db.error, 2)
                
                return ""
            else:
                uiCommon.log("Unable to toggle step visibility. Missing or invalid step_id.", 2)
        except Exception, ex:
            raise ex
        finally:
            db.close()            
