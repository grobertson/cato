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
    
    def wmGetCommands(self):
        try:
            sCatHTML = ""
            sFunHTML = ""

            # so, we will use the FunctionCategories class in the session that was loaded at login, and build the list items for the commands tab.
            cats = uiCommon.GetTaskFunctionCategories()
            if not cats:
                return "{\"error\" : \"Error: Task Function Categories class is not in the session.\"}"
            else:
                for cat in cats:
                    sCatHTML += "<li class=\"ui-widget-content ui-corner-all command_item category\""
                    sCatHTML += " id=\"cat_" + cat.Name + "\""
                    sCatHTML += " name=\"" + cat.Name + "\">"
                    sCatHTML += "<div>"
                    sCatHTML += "<img class=\"category_icon\" src=\"static/images/" + cat.Icon + "\" alt=\"\" />"
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
                        sFunHTML += "<img class=\"function_icon\" src=\"static/images/" + fn.Icon + "\" alt=\"\" />"
                        sFunHTML += "<span>" + fn.Label + "</span>"
                        sFunHTML += "<div id=\"help_text_" + fn.Name + "\" class=\"hidden\">"
                        sFunHTML += fn.Description
                        sFunHTML += "</div>"
                        sFunHTML += "</div>"

                    sFunHTML += "</div>"

            return "{\"categories\" : \"%s\", \"functions\" : \"%s\"}" % (uiCommon.packJSON(sCatHTML), uiCommon.packJSON(sFunHTML))
        except Exception, ex:
            raise ex

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
        
    def wmAddStep(self):
        sTaskID = uiCommon.getAjaxArg("sTaskID")
        sCodeblockName = uiCommon.getAjaxArg("sCodeblockName")
        sItem = uiCommon.getAjaxArg("sItem")
        try:
            sUserID = uiCommon.GetSessionUserID()

            db = catocommon.new_conn()

            sStepHTML = ""
            sErr = ""
            sSQL = ""
            sNewStepID = ""
            
            # in some cases, we'll have some special values to go ahead and set in the function_xml
            # when it's added
            # it's content will be xpath, value
            dValues = {}

            if not uiCommon.IsGUID(sTaskID):
                raise Exception("Unable to add step. Invalid or missing Task ID. [" + sTaskID + "]")


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

                if not db.exec_db_noexcep(sSQL):
                    raise Exception("Unable to add step." + db.error)

                uiCommon.WriteObjectChangeLog(db, uiGlobals.CatoObjectTypes.Task, sTaskID, sItem,
                    "Added Command from Clipboard to Codeblock:" + sCodeblockName)

            else:
                # THE NEW CLASS CENTRIC WAY
                # 1) Get a Function object for the sItem (function_name)
                # 2) use those values to construct an insert statement
                
                func = uiCommon.GetTaskFunction(sItem)
                if not func:
                    raise Exception("Unable to add step.  Can't find a Function definition for [" + sItem + "]")
                
                # add a new command
                sNewStepID = uiCommon.NewGUID()

                # NOTE: !! yes we are doing some command specific logic here.
                # Certain commands have different 'default' values for delimiters, etc.
                # sOPM: 0=none, 1=delimited, 2=parsed
                sOPM = "0"

                # gotta do a few things to the templatexml
                xdTemplate = ET.fromstring(func.TemplateXML)
                if xdTemplate is not None:
                    xe = xdTemplate.find("function")
                    if xe is not None:
                        # get the OPM
                        sOPM = xe.get("parse_method", "0")
                        # it's possible that variables=true and parse_method=0..
                        # (don't know why you'd do that on purpose, but whatever.)
                        # but if there's NO parse method attribute, and yet there is a 'variables=true' attribute
                        # well, we can't let the absence of a parse_method negate it,
                        # so the default is "2".
                        sPopVars = xe.get("variables", "false")
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
                    "'" + ET.tostring(xdTemplate) + "'" \
                    ")"

                if not db.exec_db_noexcep(sSQL):
                    raise Exception("Unable to add step." + db.error)

                uiCommon.WriteObjectChangeLog(db, uiGlobals.CatoObjectTypes.Task, sTaskID, sItem,
                    "Added Command Type:" + sItem + " to Codeblock:" + sCodeblockName)

            if sNewStepID:
                # now... get the newly inserted step and draw it's HTML
                oNewStep = task.Step.ByIDWithSettings(sNewStepID, sUserID)
                print "gotastep!"
                if oNewStep:
                    sStepHTML += ST.DrawFullStep(oNewStep)
                else:
                    sStepHTML += "<span class=\"red_text\">Error: Unable to draw Step.</span>"

                # return the html
                return "{\"step_id\":\"" + sNewStepID + "\",\"step_html\":\"" + uiCommon.packJSON(sStepHTML) + "\"}"
            else:
                raise Exception("Unable to add step.  No new step_id." + sErr)
        except Exception, ex:
            raise ex
        finally:
            db.close()

    def wmReorderSteps(self):
        sSteps = uiCommon.getAjaxArg("sSteps")
        db = catocommon.new_conn()

        try:
            i = 1
            aSteps = sSteps.split(',')
            for step_id in aSteps:
                sSQL = "update task_step set step_order = " + str(i) + " where step_id = '" + step_id + "'"

                # there will be no sSQL if there were no steps, so just skip it.
                if sSQL:
                    if not db.exec_db_noexcep(sSQL):
                        raise Exception("Unable to update steps." + db.error)
                    
                i += 1

            return ""
        except Exception, ex:
            raise ex
        finally:
            db.close()
    
    def wmToggleStepCommonSection(self):
        # no exceptions, just a log message if there are problems.
        try:
            sStepID = uiCommon.getAjaxArg("sStepID")
            sButton = uiCommon.getAjaxArg("sButton")
            db = catocommon.new_conn()
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
