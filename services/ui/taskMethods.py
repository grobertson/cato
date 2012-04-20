import sys
import traceback
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
        finally:
            if uiGlobals.request:
                if uiGlobals.request.db.conn.socket:
                    uiGlobals.request.db.close()
                uiCommon.log(uiGlobals.request.DumpMessages(), 0)

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
        
        rows = uiGlobals.request.db.select_all_dict(sSQL)

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
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sID = uiCommon.getAjaxArg("sTaskID")
            t, sErr = task.Task.FromID(sID)
            if sErr:
                uiCommon.log(sErr, 2)
            if t:
                if t.ID:
                    return t.AsJSON()
            
            #should not get here if all is well
            return "{'result':'fail','error':'Failed to get Task details for Task ID [" + sID + "].'}"
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmGetTaskCodeFromID(self):
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
        sOriginalTaskID = uiCommon.getAjaxArg("sOriginalTaskID")

        if not uiCommon.IsGUID(sOriginalTaskID.replace("'", "")):
            uiGlobals.request.Messages.append("Invalid or missing Task ID.")

        try:
            sSQL = "select task_code from task where original_task_id = '" + sOriginalTaskID + "' and default_version = 1"
            sTaskCode = uiGlobals.request.db.select_col_noexcep(sSQL)
            if not sTaskCode:
                if uiGlobals.request.db.error:
                    uiGlobals.request.Messages.append("Unable to get task code." + uiGlobals.request.db.error)
                else:
                    return ""
            else:
                return "{\"code\" : \"%s\"}" % (sTaskCode)
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    
    def wmGetTaskVersionsDropdown(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sOriginalTaskID = uiCommon.getAjaxArg("sOriginalTaskID")
            sbString = []
            sSQL = "select task_id, version, default_version" \
                " from task " \
                " where original_task_id = '" + sOriginalTaskID + "'" \
                " order by default_version desc, version"
            dt = uiGlobals.request.db.select_all_dict(sSQL)
            if not dt:
                uiGlobals.request.Messages.append("Error selecting versions: " + uiGlobals.request.db.error)
            else:
                for dr in dt:
                    sLabel = str(dr["version"]) + (" (default)" if dr["default_version"] == 1 else "")
                    sbString.append("<option value=\"" + dr["task_id"] + "\">" + sLabel + "</option>")

                return "".join(sbString)
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
    
    def wmGetTaskVersions(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
            
            sTaskID = uiCommon.getAjaxArg("sTaskID")
            sHTML = ""

            sSQL = "select task_id, version, default_version," \
                " case default_version when 1 then ' (default)' else '' end as is_default," \
                " case task_status when 'Approved' then 'encrypted' else 'unlock' end as status_icon," \
                " created_dt" \
                " from task" \
                " where original_task_id = " \
                " (select original_task_id from task where task_id = '" + sTaskID + "')" \
                " order by version"

            dt = uiGlobals.request.db.select_all_dict(sSQL)
            if uiGlobals.request.db.error:
                sHTML = "Error selecting versions: " + uiGlobals.request.db.error
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
            else:
                if dt:
                    for dr in dt:
                        print dr
                        sHTML += "<li class=\"ui-widget-content ui-corner-all version code\" id=\"v_" + dr["task_id"] + "\""
                        sHTML += "task_id=\"" + dr["task_id"] + "\">"
                        sHTML += "<img src=\"static/images/icons/" + dr["status_icon"] + "_16.png\" alt=\"\" />"
                        sHTML += str(dr["version"]) + "&nbsp;&nbsp;" + str(dr["created_dt"]) + dr["is_default"]
                        sHTML += "</li>"

            return sHTML
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmGetCommands(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sCatHTML = ""
            sFunHTML = ""

            # so, we will use the FunctionCategories class in the session that was loaded at login, and build the list items for the commands tab.
            cats = uiCommon.GetTaskFunctionCategories()
            if not cats:
                return "{\"error\" : \"Error: Task Function Categories class is not in the datacache.\"}"
            else:
                for cat in cats:
                    sCatHTML += "<li class=\"ui-widget-content ui-corner-all command_item category\""
                    sCatHTML += " id=\"cat_" + cat.Name + "\""
                    sCatHTML += " name=\"" + cat.Name + "\">"
                    sCatHTML += "<div>"
                    sCatHTML += "<img class=\"category_icon\" src=\"" + cat.Icon + "\" alt=\"\" />"
                    sCatHTML += "<span>" + cat.Label + "</span>"
                    sCatHTML += "</div>"
                    sCatHTML += "<div id=\"help_text_" + cat.Name + "\" class=\"hidden\">"
                    sCatHTML += cat.Description
                    sCatHTML += "</div>"
                    sCatHTML += "</li>"
                    
                    sFunHTML += "<div class=\"functions hidden\" id=\"cat_" + cat.Name + "_functions\">"
                    # now, let's work out the functions.
                    # we can just draw them all... they are hidden and will display on the client as clicked
                    for fn in cat.Functions:
                        sFunHTML += "<div class=\"ui-widget-content ui-corner-all command_item function\""
                        sFunHTML += " id=\"fn_" + fn.Name + "\""
                        sFunHTML += " name=\"" + fn.Name + "\">"
                        sFunHTML += "<img class=\"function_icon\" src=\"" + fn.Icon + "\" alt=\"\" />"
                        sFunHTML += "<span>" + fn.Label + "</span>"
                        sFunHTML += "<div id=\"help_text_" + fn.Name + "\" class=\"hidden\">"
                        sFunHTML += fn.Description
                        sFunHTML += "</div>"
                        sFunHTML += "</div>"

                    sFunHTML += "</div>"

            return "{\"categories\" : \"%s\", \"functions\" : \"%s\"}" % (uiCommon.packJSON(sCatHTML), uiCommon.packJSON(sFunHTML))
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmCreateTask(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
            
            sTaskName = uiCommon.unpackJSON(uiCommon.getAjaxArg("sTaskName"))
            sTaskCode = uiCommon.unpackJSON(uiCommon.getAjaxArg("sTaskCode"))
            sTaskDesc = uiCommon.unpackJSON(uiCommon.getAjaxArg("sTaskDesc"))
    
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
            
                # add security log
                uiCommon.WriteObjectAddLog(uiGlobals.CatoObjectTypes.Task, t.ID, t.Name, "");

                return "{\"id\" : \"%s\"}" % (t.ID)
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmCopyTask(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
            
            sCopyTaskID = uiCommon.getAjaxArg("sCopyTaskID")
            sTaskName = uiCommon.getAjaxArg("sTaskName")
            sTaskCode =uiCommon.getAjaxArg("sTaskCode")

            t, sErr = task.Task.FromID(sCopyTaskID)
            if not t:
                return "{\"error\" : \"Unable to build Task object from ID [" + sCopyTaskID + "].\"}"
            
            sNewTaskID = t.Copy(0, sTaskName, sTaskCode)
            if not sNewTaskID:
                return "Unable to create Task."
            
            uiCommon.WriteObjectAddLog(uiGlobals.CatoObjectTypes.Task, t.ID, t.Name, "Copied from " + sCopyTaskID);
            return "{\"id\" : \"%s\"}" % (sNewTaskID)
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmDeleteTasks(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sDeleteArray = uiCommon.getAjaxArg("sDeleteArray")
            if len(sDeleteArray) < 36:
                return "{\"info\" : \"Unable to delete - no selection.\"}"
    
            sDeleteArray = uiCommon.QuoteUp(sDeleteArray)

            if not sDeleteArray:
                return "{\"info\" : \"Unable to delete - no selection.\"}"
                
            # first we need a list of tasks that will not be deleted
            sSQL = "select task_name from task t " \
                    " where t.original_task_id in (" + sDeleteArray + ")" \
                    " and t.task_id in (select ti.task_id from tv_task_instance ti where ti.task_id = t.task_id)"
            sTaskNames = uiGlobals.request.db.select_csv(sSQL, True)

            # list of tasks that will be deleted
            # we have an array of 'original_task_id' - we need an array of task_id
            sSQL = "select t.task_id from task t " \
                " where t.original_task_id in (" + sDeleteArray + ")" \
                " and t.task_id not in (select ti.task_id from tv_task_instance ti where ti.task_id = t.task_id)"
            sTaskIDs = uiGlobals.request.db.select_csv(sSQL, True)
            if len(sTaskIDs) > 1:
                sSQL = "delete from task_step_user_settings" \
                    " where step_id in" \
                    " (select step_id from task_step where task_id in (" + sTaskIDs + "))"
                if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                    uiGlobals.request.Messages.append(uiGlobals.request.db)
    
                sSQL = "delete from task_step where task_id in (" + sTaskIDs + ")"
                if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                    uiGlobals.request.Messages.append(uiGlobals.request.db.error)
    
                sSQL = "delete from task_codeblock where task_id in (" + sTaskIDs + ")"
                if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                    uiGlobals.request.Messages.append(uiGlobals.request.db)
    
                sSQL = "delete from task where task_id in (" + sTaskIDs + ")"
                if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                    uiGlobals.request.Messages.append(uiGlobals.request.db)
    
                uiGlobals.request.db.tran_commit()
    
                uiCommon.WriteObjectDeleteLog(uiGlobals.CatoObjectTypes.Task, "Multiple", "Original Task IDs", sDeleteArray)
            
            if len(sTaskNames) > 0:
                return "{\"info\" : \"Task(s) (" + sTaskNames + ") have history rows and could not be deleted.\"}"
            
            return "{\"result\" : \"success\"}"
            
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmUpdateTaskDetail(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sTaskID = uiCommon.getAjaxArg("sTaskID")
            sColumn = uiCommon.getAjaxArg("sColumn")
            sValue = uiCommon.getAjaxArg("sValue")
            sUserID = uiCommon.GetSessionUserID()

            if uiCommon.IsGUID(sTaskID) and uiCommon.IsGUID(sUserID):
                # we encoded this in javascript before the ajax call.
                # the safest way to unencode it is to use the same javascript lib.
                # (sometimes the javascript and .net libs don't translate exactly, google it.)
                sValue = uiCommon.unpackJSON(sValue)
                sValue = uiCommon.TickSlash(sValue)

                sSQL = "select original_task_id from task where task_id = '" + sTaskID + "'"
                sOriginalTaskID = uiGlobals.request.db.select_col_noexcep(sSQL)

                if not sOriginalTaskID:
                    uiGlobals.request.Messages.append("ERROR: Unable to get original_task_id for [" + sTaskID + "]." + uiGlobals.request.db.error)
                    return "{\"error\" : \"Unable to get original_task_id for [" + sTaskID + "].\"}"


                # what's the "set clause"?
                sSetClause = sColumn + "='" + sValue + "'"

                #  bugzilla 1074, check for existing task_code and task_name
                if sColumn == "task_code" or sColumn == "task_name":
                    sSQL = "select task_id from task where " + \
                        sColumn + "='" + sValue + "'" \
                        " and original_task_id <> '" + sOriginalTaskID + "'"

                    sValueExists = uiGlobals.request.db.select_col_noexcep(sSQL)
                    if uiGlobals.request.db.error:
                        uiGlobals.request.Messages.append("ERROR: Unable to check for existing names [" + sTaskID + "]." + uiGlobals.request.db.error)

                    if sValueExists:
                        return "{\"info\" : \"" + sValue + " exists, please choose another value.\"}"
                
                    # changing the name or code updates ALL VERSIONS
                    sSQL = "update task set " + sSetClause + " where original_task_id = '" + sOriginalTaskID + "'"
                else:
                    # some columns on this table allow nulls... in their case an empty sValue is a null
                    if sColumn == "concurrent_instances" or sColumn == "queue_depth":
                        if len(sValue.replace(" ", "")) == 0:
                            sSetClause = sColumn + " = null"
                    
                    # some columns are checkboxes, so make sure it is a db appropriate value (1 or 0)
                    if sColumn == "concurrent_by_asset":
                        if uiCommon.IsTrue(sValue):
                            sSetClause = sColumn + " = 1"
                        else:
                            sSetClause = sColumn + " = 0"
                    
                    sSQL = "update task set " + sSetClause + " where task_id = '" + sTaskID + "'"
                

                if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                    uiGlobals.request.Messages.append("Unable to update task [" + sTaskID + "]." + uiGlobals.request.db.error)

                uiCommon.WriteObjectChangeLog(uiGlobals.CatoObjectTypes.Task, sTaskID, sColumn, sValue)

            else:
                uiGlobals.request.Messages.append("Unable to update task. Missing or invalid task [" + sTaskID + "] id.")

            return "{\"result\" : \"success\"}"
            
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())           


    def wmGetCodeblocks(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
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
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
        
    def wmGetSteps(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
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
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
        
    def wmGetStep(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name

            sStepID = uiCommon.getAjaxArg("sStepID")
            sStepHTML = ""
            if not uiCommon.IsGUID(sStepID):
                uiGlobals.request.Messages.append("Unable to get step. Invalid or missing Step ID. [" + sStepID + "].")

            sUserID = uiCommon.GetSessionUserID()

            oStep = ST.GetSingleStep(sStepID, sUserID)
            if oStep is not None:
                # embedded steps...
                # if the step_order is -1 and the codeblock_name is a guid, this step is embedded 
                # within another step
                if oStep.Order == -1 and uiCommon.IsGUID(oStep.Codeblock):
                    sStepHTML += "Embedded not yet implemeneted." # sStepHTML += ft.DrawEmbeddedStep(oStep)
                else:
                    sStepHTML += ST.DrawFullStep(oStep)
            else:
                sStepHTML += "<span class=\"red_text\">ERROR: No data found.<br />This command should be deleted and recreated.<br /><br />ID [" + sStepID + "].</span>"

            # return the html
            return sStepHTML
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmAddStep(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
            
            sTaskID = uiCommon.getAjaxArg("sTaskID")
            sCodeblockName = uiCommon.getAjaxArg("sCodeblockName")
            sItem = uiCommon.getAjaxArg("sItem")
            sUserID = uiCommon.GetSessionUserID()

            sStepHTML = ""
            sSQL = ""
            sNewStepID = ""
            
            # in some cases, we'll have some special values to go ahead and set in the function_xml
            # when it's added
            # it's content will be xpath, value
            dValues = {}

            if not uiCommon.IsGUID(sTaskID):
                uiGlobals.request.Messages.append("Unable to add step. Invalid or missing Task ID. [" + sTaskID + "]")


            # now, the sItem variable may have a function name (if it's a new command)
            # or it may have a guid (if it's from the clipboard)

            # so, if it's a guid after stripping off the prefix, it's from the clipboard

            # the function has a fn_ or clip_ prefix on it from the HTML.  Strip it off.
            # FIX... test the string to see if it BEGINS with fn_ or clip_
            # IF SO... cut off the beginning... NOT a replace operation.
            if sItem[:3] == "fn_": sItem = sItem[3:]
            if sItem[:5] == "clip_": sItem = sItem[5:]

            # could also beging with cb_, which means a codeblock was dragged and dropped.
            # this special case will result in a codeblock command.
            if sItem[:3] == "cb_":
                # so, the sItem becomes "codeblock"
                sCBName = sItem[3:]
                dValues["//codeblock"] = sCBName
                sItem = "codeblock"

            # NOTE: !! yes we are adding the step with an order of -1
            # the update event on the client does not know the index at which it was dropped.
            # so, we have to insert it first to get the HTML... but the very next step
            # will serialize and update the entire sortable... 
            # immediately replacing this -1 with the correct position

            if uiCommon.IsGUID(sItem):
                sNewStepID = sItem

                # copy from the clipboard (using the root_step_id to get ALL associated steps)
                sSQL = "insert into task_step (step_id, task_id, codeblock_name, step_order, step_desc," \
                    " commented, locked, output_parse_type, output_row_delimiter, output_column_delimiter," \
                    " function_name, function_xml, variable_xml)" \
                    " select step_id, '" + sTaskID + "'," \
                    " case when codeblock_name is null then '" + sCodeblockName + "' else codeblock_name end," \
                    "-1,step_desc," \
                    "0,0,output_parse_type,output_row_delimiter,output_column_delimiter," \
                    "function_name,function_xml,variable_xml" \
                    " from task_step_clipboard" \
                    " where user_id = '" + sUserID + "'" \
                    " and root_step_id = '" + sItem + "'"

                if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                    uiGlobals.request.Messages.append("Unable to add step." + uiGlobals.request.db.error)

                uiCommon.WriteObjectChangeLog(uiGlobals.CatoObjectTypes.Task, sTaskID, sItem,
                    "Added Command from Clipboard to Codeblock:" + sCodeblockName)

            else:
                # THE NEW CLASS CENTRIC WAY
                # 1) Get a Function object for the sItem (function_name)
                # 2) use those values to construct an insert statement
                
                func = uiCommon.GetTaskFunction(sItem)
                if not func:
                    uiGlobals.request.Messages.append("Unable to add step.  Can't find a Function definition for [" + sItem + "]")
                
                # add a new command
                sNewStepID = uiCommon.NewGUID()

                # NOTE: !! yes we are doing some command specific logic here.
                # Certain commands have different 'default' values for delimiters, etc.
                # sOPM: 0=none, 1=delimited, 2=parsed
                sOPM = "0"

                # gotta do a few things to the templatexml
                xe = ET.fromstring(func.TemplateXML)
                if xe is not None:
                    # get the OPM
                    sOPM = xe.get("parse_method", "0")
                    # it's possible that variables=true and parse_method=0..
                    # (don't know why you'd do that on purpose, but whatever.)
                    # but if there's NO parse method attribute, and yet there is a 'variables=true' attribute
                    # well, we can't let the absence of a parse_method negate it,
                    # so the default is "2".
                    sPopVars = xe.get("variables", "false")
                    print sPopVars
                    print sOPM
                    if uiCommon.IsTrue(sPopVars) and sOPM == "0":
                        sOPM = "2"
                    
                    
                    # there may be some provided values ... so alter the func.TemplateXML accordingly
                    for sXPath, sValue in dValues.iteritems():
                        xNode = xe.find(sXPath)
                        if xNode is not None:
                            xNode.text = dValues[sXPath]
                
                    sSQL = "insert into task_step (step_id, task_id, codeblock_name, step_order," \
                        " commented, locked, output_parse_type, output_row_delimiter, output_column_delimiter," \
                        " function_name, function_xml)" \
                        " values (" \
                        "'" + sNewStepID + "'," \
                        "'" + sTaskID + "'," + \
                        ("'" + sCodeblockName + "'" if sCodeblockName else "null") + "," \
                        "-1," \
                        "0,0," + sOPM + ",0,0," \
                        "'" + func.Name + "'," \
                        "'" + ET.tostring(xe) + "'" \
                        ")"
                    if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                        uiGlobals.request.Messages.append("Unable to add step." + uiGlobals.request.db.error)
    
                    uiCommon.WriteObjectChangeLog(uiGlobals.CatoObjectTypes.Task, sTaskID, sItem,
                        "Added Command Type:" + sItem + " to Codeblock:" + sCodeblockName)
                else:
                    uiGlobals.request.Messages.append("Unable to add step.  No template xml.")
            if sNewStepID:
                # now... get the newly inserted step and draw it's HTML
                oNewStep = task.Step.ByIDWithSettings(sNewStepID, sUserID)
                if oNewStep:
                    sStepHTML += ST.DrawFullStep(oNewStep)
                else:
                    sStepHTML += "<span class=\"red_text\">Error: Unable to draw Step.</span>"

                # return the html
                return "{\"step_id\":\"" + sNewStepID + "\",\"step_html\":\"" + uiCommon.packJSON(sStepHTML) + "\"}"
            else:
                uiGlobals.request.Messages.append("Unable to add step.  No new step_id.")
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmReorderSteps(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sSteps = uiCommon.getAjaxArg("sSteps")
            i = 1
            aSteps = sSteps.split(',')
            for step_id in aSteps:
                sSQL = "update task_step set step_order = " + str(i) + " where step_id = '" + step_id + "'"

                # there will be no sSQL if there were no steps, so just skip it.
                if sSQL:
                    if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                        uiGlobals.request.Messages.append("Unable to update steps." + uiGlobals.request.db.error)
                    
                i += 1

            return ""
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmDeleteStep(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sStepID = uiCommon.getAjaxArg("sStepID")
            # you have to know which one we are removing
            sDeletedStepOrder = "0"
            sTaskID = ""
            sCodeblock = ""
            sFunction = ""
            sFunctionXML = ""

            sSQL = "select task_id, codeblock_name, step_order, function_name, function_xml" \
                " from task_step where step_id = '" + sStepID + "'"

            dr = uiGlobals.request.db.select_row_dict(sSQL)
            if dr:
                sDeletedStepOrder = str(dr["step_order"])
                sTaskID = dr["task_id"]
                sCodeblock = dr["codeblock_name"]
                sFunction = dr["function_name"]
                sFunctionXML = dr["function_xml"]

                # for logging, we'll stick the whole command XML into the log
                # so we have a complete record of the step that was just deleted.
                uiCommon.WriteObjectDeleteLog(uiGlobals.CatoObjectTypes.Task, "Multiple", "Original Task IDs",
                    "Codeblock:" + sCodeblock +
                    " Step Order:" + sDeletedStepOrder +
                    " Command Type:" + sFunction +
                    " Details:" + sFunctionXML)

            # "embedded" steps have a codeblock name referencing their "parent" step.
            # if we're deleting a parent, whack all the children
            sSQL = "delete from task_step where codeblock_name = '" + sStepID + "'"
            if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                uiGlobals.request.Messages.append("Unable to delete step." + uiGlobals.request.db.error)

            # step might have user_settings
            sSQL = "delete from task_step_user_settings where step_id = '" + sStepID + "'"
            if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                uiGlobals.request.Messages.append("Unable to delete step user settings." + uiGlobals.request.db.error)

            # now whack the parent
            sSQL = "delete from task_step where step_id = '" + sStepID + "'"
            if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                uiGlobals.request.Messages.append("Unable to delete step." + uiGlobals.request.db.error)

            sSQL = "update task_step set step_order = step_order - 1" \
                " where task_id = '" + sTaskID + "'" \
                " and codeblock_name = '" + sCodeblock + "'" \
                " and step_order > " + sDeletedStepOrder
            if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                uiGlobals.request.Messages.append("Unable to reorder steps after deletion." + uiGlobals.request.db.error)

            uiGlobals.request.db.tran_commit()
            
            return ""
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
    
    def wmUpdateStep(self):
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
        sStepID = uiCommon.getAjaxArg("sStepID")
        sFunction = uiCommon.getAjaxArg("sFunction")
        sXPath = uiCommon.getAjaxArg("sXPath")
        sValue = uiCommon.getAjaxArg("sValue")

        # we encoded this in javascript before the ajax call.
        # the safest way to unencode it is to use the same javascript lib.
        # (sometimes the javascript and .net libs don't translate exactly, google it.)
        sValue = uiCommon.unpackJSON(sValue)

        uiCommon.log("Updating step [%s (%s)] setting [%s] to [%s]." % (sFunction, sStepID, sXPath, sValue) , 4)
        # if the function type is "_common" that means this is a literal column on the step table.
        if sFunction == "_common":
            sValue = uiCommon.TickSlash(sValue) # escape single quotes for the SQL insert
            sSQL = "update task_step set " + sXPath + " = '" + sValue + "' where step_id = '" + sStepID + "'"

            if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)

        else:
            # XML processing
            # get the xml from the step table and update it
            sSQL = "select function_xml from task_step where step_id = '" + sStepID + "'"

            sXMLTemplate = uiGlobals.request.db.select_col_noexcep(sSQL)
            print sXMLTemplate
            if uiGlobals.request.db.error:
                uiGlobals.request.Messages.append("Unable to get XML data for step [" + sStepID + "].")

            xDoc = ET.fromstring(sXMLTemplate)
            if xDoc is None:
                uiGlobals.request.Messages.append("XML data for step [" + sStepID + "] is invalid.")

            try:
                uiCommon.log("... looking for %s" % sXPath, 4)
                xNode = xDoc.find(sXPath)
                print ET.tostring(xNode)
                if xNode is None:
                    uiGlobals.request.Messages.append("XML data for step [" + sStepID + "] does not contain '" + sXPath + "' node.")

                xNode.text = sValue
            except Exception:
                try:
                    # here's the deal... given an XPath statement, we simply cannot add a new node if it doesn't exist.
                    # why?  because xpath is a query language.  It doesnt' describe exactly what to add due to wildcards and # foo syntax.

                    # but, what we can do is make an assumption in our specific case... 
                    # that we are only wanting to add because we changed an underlying command XML template, and there are existing commands.

                    # so... we will split the xpath into segments, and traverse upward until we find an actual node.
                    # once we have it, we will need to add elements back down.

                    # string[] nodes = sXPath.Split('/')

                    # for node in nodes:
#                         #     # try: to select THIS one, and stick it on the backwards stack
                    #     xNode = xRoot.find("# " + node)
                    #     if xNode is None:
                    #         uiGlobals.request.Messages.append("XML data for step [" + sStepID + "] does not contain '" + sXPath + "' node.")

                    # }

                    xFoundNode = None
                    aMissingNodes = []

                    # if there are no slashes we'll just add this one explicitly as a child of root
                    if sXPath.find("/") == -1:
                        xDoc.append(ET.Element(sXPath))
                    else:                             # and if there are break it down
                        sWorkXPath = sXPath
                        while sWorkXPath.find("/") > -1:
                            idx = uiCommon.LastIndexOf(sWorkXPath, "/") + 1
                            aMissingNodes.append(sWorkXPath[idx:])
                            sWorkXPath = sWorkXPath[:idx]

                            xFoundNode = xDoc.find(sWorkXPath)
                            if xFoundNode is not None:
                                # Found one! stop looping
                                break

                        # now that we know where to start (xFoundNode), we can use that as a basis for adding
                        for sNode in aMissingNodes:
                            xFoundNode.append(ET.Element(sNode))

                    # now we should be good to stick the value on the final node.
                    xNode = xDoc.find(sXPath)
                    if xNode is None:
                        uiGlobals.request.Messages.append("XML data for step [" + sStepID + "] does not contain '" + sXPath + "' node.")

                    xNode.text = sValue

                    # xRoot.Add(new XElement(sXPath, sValue))
                    # xRoot.SetElementValue(sXPath, sValue)
                except Exception, ex:
                    uiGlobals.request.Messages.append("Error Saving Step [" + sStepID + "].  Could not find and cannot create the [" + sXPath + "] property in the XML." + ex.__str__())



            sSQL = "update task_step set " \
                " function_xml = '" + uiCommon.TickSlash(ET.tostring(xDoc)) + "'" \
                " where step_id = '" + sStepID + "';"

            if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db)


        sSQL = "select task_id, codeblock_name, step_order from task_step where step_id = '" + sStepID + "'"
        dr = uiGlobals.request.db.select_row_dict(sSQL)
        if uiGlobals.request.db.error:
            uiGlobals.request.Messages.append(uiGlobals.request.db.error)

        if dr is not None:
            uiCommon.WriteObjectChangeLog(uiGlobals.CatoObjectTypes.Task, dr["task_id"], sFunction,
                "Codeblock:" + dr["codeblock_name"] + \
                " Step Order:" + str(dr["step_order"]) + \
                " Command Type:" + sFunction + \
                " Property:" + sXPath + \
                " New Value: " + sValue)

        return ""

    def wmToggleStepCommonSection(self):
        # no exceptions, just a log message if there are problems.
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sStepID = uiCommon.getAjaxArg("sStepID")
            sButton = uiCommon.getAjaxArg("sButton")
            if uiCommon.IsGUID(sStepID):
                sUserID = uiCommon.GetSessionUserID()
                sButton = ("null" if sButton == "" else "'" + sButton + "'")
    
                #is there a row?
                iRowCount = uiGlobals.request.db.select_col_noexcep("select count(*) from task_step_user_settings" \
                    " where user_id = '" + sUserID + "'" \
                    " and step_id = '" + sStepID + "'")
                if iRowCount == 0:
                    sSQL = "insert into task_step_user_settings" \
                        " (user_id, step_id, visible, breakpoint, skip, button)" \
                        " values ('" + sUserID + "','" + sStepID + "', 1, 0, 0, " + sButton + ")"
                else:
                    sSQL = "update task_step_user_settings set button = " + sButton + " where step_id = '" + sStepID + "'"

                if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                    uiGlobals.request.Messages.append("Unable to toggle step button [" + sStepID + "]." + uiGlobals.request.db.error)

                return ""
            else:
                uiGlobals.request.Messages.append("Unable to toggle step button. Missing or invalid step_id.")
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            
    def wmToggleStep(self):
        # no exceptions, just a log message if there are problems.
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sStepID = uiCommon.getAjaxArg("sStepID")
            sVisible = uiCommon.getAjaxArg("sVisible")
            
            if uiCommon.IsGUID(sStepID):
                sUserID = uiCommon.GetSessionUserID()

                sVisible = ("1" if sVisible == "1" else "0")
    
                #is there a row?
                iRowCount = uiGlobals.request.db.select_col_noexcep("select count(*) from task_step_user_settings" \
                    " where user_id = '" + sUserID + "'" \
                    " and step_id = '" + sStepID + "'")
                if iRowCount == 0:
                    sSQL = "insert into task_step_user_settings" \
                        " (user_id, step_id, visible, breakpoint, skip)" \
                        " values ('" + sUserID + "','" + sStepID + "', " + sVisible + ", 0, 0)"
                else:
                    sSQL = "update task_step_user_settings set visible = '" + sVisible + "' where step_id = '" + sStepID + "'"

                if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                    uiGlobals.request.Messages.append("Unable to toggle step visibility [" + sStepID + "]." + uiGlobals.request.db.error)
                
                return ""
            else:
                uiCommon.log("Unable to toggle step visibility. Missing or invalid step_id.", 2)
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmFnSetvarAddVar(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sStepID = uiCommon.getAjaxArg("sStepID")
            ST.AddToCommandXML(sStepID, "function", "<variable>" \
                "<name input_type=\"text\"></name>" \
                "<value input_type=\"text\"></value>" \
                "<modifier input_type=\"select\">DEFAULT</modifier>" \
                "</variable>")

            return ""
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmFnClearvarAddVar(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sStepID = uiCommon.getAjaxArg("sStepID")
            ST.AddToCommandXML(sStepID, "function", "<variable><name input_type=\"text\"></name></variable>")

            return ""
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmFnExistsAddVar(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sStepID = uiCommon.getAjaxArg("sStepID")
            ST.AddToCommandXML(sStepID, "function", "<variable>" \
                "<name input_type=\"text\"></name><is_true>0</is_true>" \
                "</variable>")

            return ""
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmFnVarRemoveVar(self):
        # NOTE: this function supports both the set_varible AND clear_variable commands
        try:
            sStepID = uiCommon.getAjaxArg("sStepID")
            iIndex = uiCommon.getAjaxArg("iIndex")
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            if iIndex > 0:
                ST.RemoveFromCommandXML(sStepID, "variable[" + iIndex + "]")
                return ""
            else:
                uiGlobals.request.Messages.append("Unable to modify step. Invalid index.")
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmFnWaitForTasksRemoveHandle(self):
        sStepID = uiCommon.getAjaxArg("sStepID")
        iIndex = uiCommon.getAjaxArg("iIndex")
        try:
            if iIndex > 0:
                ST.RemoveFromCommandXML(sStepID, "handle[" + iIndex + "]")
                return ""
            else:
                uiGlobals.request.Messages.append("Unable to modify step. Invalid index.")
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmFnWaitForTasksAddHandle(self):
        sStepID = uiCommon.getAjaxArg("sStepID")
        try:
            ST.AddToCommandXML(sStepID, "function", "<handle><name input_type=\"text\"></name></handle>")
            return ""
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmFnAddPair(self):
        sStepID = uiCommon.getAjaxArg("sStepID")
        try:
            ST.AddToCommandXML(sStepID, "function", "<pair><key input_type=\"text\"></key><value input_type=\"text\"></value></pair>")

            return ""
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmFnRemovePair(self):
        sStepID = uiCommon.getAjaxArg("sStepID")
        iIndex = uiCommon.getAjaxArg("iIndex")
        try:
            if iIndex > 0:
                ST.RemoveFromCommandXML(sStepID, "pair[" + iIndex + "]")

                return ""
            else:
                uiGlobals.request.Messages.append("Unable to modify step. Invalid index.")
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmTaskSearch(self):
        sSearchText = uiCommon.getAjaxArg("sSearchText")
        try:
            sWhereString = ""

            if sSearchText:
                sWhereString = " and (a.task_name like '%%" + sSearchText + \
                   "%%' or a.task_desc like '%%" + sSearchText + \
                   "%%' or a.task_code like '%%" + sSearchText + "%%' ) "

            sSQL = "select a.original_task_id, a.task_id, a.task_name, a.task_code," \
                " left(a.task_desc, 255) as task_desc, a.version" \
                   " from task a  " \
                   " where default_version = 1" + \
                   sWhereString + \
                   " order by task_name, default_version desc, version"

            dt = uiGlobals.request.db.select_all_dict(sSQL)
            if uiGlobals.request.db.error:
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)

            sHTML = "<hr />"

            iRowsToGet = len(dt)

            if iRowsToGet == 0:
                sHTML += "No results found"
            else:
                if iRowsToGet >= 100:
                    sHTML += "<div>Search found " + iRowsToGet + " results.  Displaying the first 100.</div>"
                    iRowsToGet = 99
                sHTML += "<ul id=\"search_task_ul\" class=\"search_dialog_ul\">"

                i = 0
                for row in dt:
                    if i > iRowsToGet:
                        break
                    
                    sTaskName = row["task_name"].replace("\"", "\\\"")
                    sLabel = row["task_code"] + " : " + sTaskName
                    sDesc = row["task_desc"].replace("\"", "").replace("'", "")

                    sHTML += "<li class=\"ui-widget-content ui-corner-all search_dialog_value\" tag=\"task_picker_row\"" \
                        " original_task_id=\"" + row["original_task_id"] + "\"" \
                        " task_label=\"" + sLabel + "\"" \
                        "\">"
                    sHTML += "<div class=\"step_header_title search_dialog_value_name\">" + sLabel + "</div>"

                    sHTML += "<div class=\"step_header_icons\">"

                    # if there's a description, show a tooltip
                    if sDesc:
                        sHTML += "<img src=\"static/images/icons/info.png\" class=\"search_dialog_tooltip trans50\" title=\"" + sDesc + "\" />"

                    sHTML += "</div>"
                    sHTML += "<div class=\"clearfloat\"></div>"
                    sHTML += "</li>"
                    
                    i += 1
                    
            sHTML += "</ul>"

            return sHTML
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmGetStepVarsEdit(self):
        sStepID = uiCommon.getAjaxArg("sStepID")
        sUserID = uiCommon.GetSessionUserID()

        oStep = ST.GetSingleStep(sStepID, sUserID)
        fn = uiCommon.GetTaskFunction(oStep.FunctionName)
        if fn is None:
            uiGlobals.request.Messages.append("Error - Unable to get the details for the Command type '" + oStep.FunctionName + "'.")
        
        # we will return some key values, and the html for the dialog
        sHTML = ST.DrawVariableSectionForEdit(oStep)
        
        if not sHTML:
            sHTML = "<span class=\"red_text\">Unable to get command variables.</span>"

        return '{"parse_type":"%d","row_delimiter":"%d","col_delimiter":"%d","html":"%s"}' % \
            (oStep.OutputParseType, oStep.OutputRowDelimiter, oStep.OutputColumnDelimiter, uiCommon.packJSON(sHTML))

    def wmUpdateVars(self):
        try:
            sStepID = uiCommon.getAjaxArg("sStepID")
            sOPM = uiCommon.getAjaxArg("sOPM")
            sRowDelimiter = uiCommon.getAjaxArg("sRowDelimiter")
            sColDelimiter = uiCommon.getAjaxArg("sColDelimiter")
            oVarArray = uiCommon.getAjaxArg("oVarArray")
            
            # if every single variable is delimited, we can sort them!
            bAllDelimited = True
            
            # # update the processing method
            # sOutputProcessingType = sOutputProcessingType.replace("'", "''")
    
            # we might need to do something special for some function types
    
            # removed this on 10/6/09 because we are hiding "output type"
            #                 " output_parse_type = '" + sOutputProcessingType + "'," \
    
            sSQL = "update task_step set " \
                " output_row_delimiter = '" + sRowDelimiter + "'," \
                " output_column_delimiter = '" + sColDelimiter + "'" \
                " where step_id = '" + sStepID + "';"
    
            if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
    
    
            # 1 - create a new xdocument
            # 2 - spin thru adding the variables
            # 3 - commit the whole doc at once to the db
    
            xVars = ET.Element("variables")
    
            # spin thru the variable array from the client
            for oVar in oVarArray:
                # [0 - var type], [1 - var_name], [2 - left property], [3 - right property], [4 - left property type], [5 - right property type]
    
                # I'm just declaring named variable here for readability
                sVarName = str(oVar[0])  # no case conversion
                sVarType = str(oVar[1]).lower()
                sLProp = str(uiCommon.unpackJSON(oVar[2]))
                sRProp = str(uiCommon.unpackJSON(oVar[3]))
                sLType = str(oVar[4])
                sRType = str(oVar[5])
    
                xVar = ET.SubElement(xVars, "variable")
                xVarName = ET.SubElement(xVar, "name")
                xVarName.text = sVarName
                xVarType = ET.SubElement(xVar, "type")
                xVarType.text = sVarType
    
                # now that we've added it, based on the type let's add the custom properties
                if sVarType == "delimited":
                    x = ET.SubElement(xVar, "position")
                    x.text = sLProp
                elif sVarType == "regex":
                    bAllDelimited = False
                    x = ET.SubElement(xVar, "regex")
                    x.text = sLProp
                elif sVarType == "range":
                    bAllDelimited = False
                    # we favor the 'string' mode over the index.  If a person selected 'index' that's fine
                    # but if something went wrong, we default to prefix/suffix.
                    if sLType == "index":
                        x = ET.SubElement(xVar, "range_begin")
                        x.text = sLProp
                    else:
                        x = ET.SubElement(xVar, "prefix")
                        x.text = sLProp
    
                    if sRType == "index":
                        x = ET.SubElement(xVar, "range_end")
                        x.text = sRProp
                    else:
                        x = ET.SubElement(xVar, "suffix")
                        x.text = sRProp
                elif sVarType == "xpath":
                    bAllDelimited = False
                    x = ET.SubElement(xVar, "xpath")
                    x.text = sLProp
    
            # if it's delimited, sort it
            if sOPM == "1" or bAllDelimited == True:
                print "would sort"
    #            List<XElement> ordered = xVars.Elements("variable")
    #                .OrderBy(element => (int?)element.Element("position"))
    #                    .ToList()
    #            
    #            xVars.RemoveAll()
    #            xVars.Add(ordered)
            
            
            uiCommon.log("Saving variables ...", 4)
            uiCommon.log(ET.tostring(xVars), 4)
            
            sSQL = "update task_step set " \
                " variable_xml = '" + uiCommon.TickSlash(ET.tostring(xVars)) + "'" \
                " where step_id = '" + sStepID + "';"
    
            if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
    
            return ""
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

