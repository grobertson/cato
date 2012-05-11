import sys
import os
import traceback
import xml.etree.ElementTree as ET
import json
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

    def wmGetEcotemplate(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sID = uiCommon.getAjaxArg("sID")
            et = ecosystem.Ecotemplate()
            if et:
                et.FromID(sID, bIncludeActions=False)
                if et.ID:
                    return et.AsJSON()
            
            #should not get here if all is well
            return "{'result':'fail','error':'Failed to get Cloud details for Cloud ID [" + sID + "].'}"
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()

    def wmGetEcotemplatesTable(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sHTML = ""
            sFilter = uiCommon.getAjaxArg("sSearch")
            ets = ecosystem.Ecotemplates(sFilter)
            if ets:
                for row in ets.rows:
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
                    uiCommon.WriteObjectAddLog(uiGlobals.CatoObjectTypes.Ecosystem, et.ID, et.Name, "Ecotemplate created.")
                    return "{\"ecotemplate_id\" : \"%s\"}" % et.ID
                else:
                    uiGlobals.request.Messages.append(msg)
                    return "{\"info\" : \"%s\"}" % msg
            else:
                return "{\"error\" : \"Unable to create Ecotemplate.\"}"
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmDeleteEcotemplates(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sDeleteArray = uiCommon.getAjaxArg("sDeleteArray")
            if len(sDeleteArray) < 36:
                return "{\"info\" : \"Unable to delete - no selection.\"}"
    
            sDeleteArray = uiCommon.QuoteUp(sDeleteArray)
            
            # can't delete it if it's referenced.
            sSQL = "select count(*) from ecosystem where ecotemplate_id in (" + sDeleteArray + ")"
            iResults = uiGlobals.request.db.select_col_noexcep(sSQL)

            if not iResults:
                sSQL = "delete from ecotemplate_action where ecotemplate_id in (" + sDeleteArray + ")"
                if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                    uiGlobals.request.Messages.append(uiGlobals.request.db.error)
                
                sSQL = "delete from ecotemplate where ecotemplate_id in (" + sDeleteArray + ")"
                if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                    uiGlobals.request.Messages.append(uiGlobals.request.db.error)
                
                #if we made it here, save the logs
                uiCommon.WriteObjectDeleteLog(uiGlobals.CatoObjectTypes.EcoTemplate, "", "", "Ecosystem Templates(s) Deleted [" + sDeleteArray + "]")
            else:
                return "{\"info\" : \"Unable to delete - %d Ecosystems are referenced by these templates.\"}" % iResults
                
            return "{\"result\" : \"success\"}"
            
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()

    def wmCopyEcotemplate(self):
        try:
            sEcoTemplateID = uiCommon.getAjaxArg("sEcoTemplateID")
            sNewName = uiCommon.getAjaxArg("sNewName")
            
            if sEcoTemplateID and sNewName:
    
                # have to instantiate one to copy it
                et = ecosystem.Ecotemplate()
                et.FromID(sEcoTemplateID)
                if et is not None:
                    result, msg = et.DBCopy(sNewName)
                    if not result:
                        return "{\"error\" : \"%s\"}" % msg
                    
                    # returning the ID indicates success...
                    return "{\"ecotemplate_id\" : \"%s\"}" % et.ID
                else:
                    uiGlobals.request.Messages.append("Unable to get Template [" + sEcoTemplateID + "] to copy.")
            else:
                return "{\"info\" : \"Unable to Copy - New name and source ID are both required.\"}"
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmGetEcotemplateEcosystems(self):
        try:
            sEcoTemplateID = uiCommon.getAjaxArg("sEcoTemplateID")
        
            sHTML = ""

            if sEcoTemplateID:
                sSQL = "select ecosystem_id, ecosystem_name, ecosystem_desc" \
                    " from ecosystem" \
                    " where ecotemplate_id = '" + sEcoTemplateID + "'" \
                    " and account_id = '" + uiCommon.GetCookie("selected_cloud_account") + "'" \
                    " order by ecosystem_name"

                dt = uiGlobals.request.db.select_all_dict(sSQL)
                if uiGlobals.request.db.error:
                    uiGlobals.request.Messages.append(uiGlobals.request.db.error)

                if dt:
                    sHTML += "<ul>"
                    for dr in dt:
                        sEcosystemID = dr["ecosystem_id"]
                        sEcosystemName = dr["ecosystem_name"]
                        sDesc = (dr["ecosystem_desc"] if dr["ecosystem_desc"] else "")
                        sDesc = sDesc.replace("\"", "").replace("'", "")

                        sHTML += "<li class=\"ui-widget-content ui-corner-all\"" \
                            " ecosystem_id=\"" + sEcosystemID + "\"" \
                            "\">"
                        sHTML += "<div class=\"step_header_title ecosystem_name pointer\">"
                        sHTML += "<img src=\"static/images/icons/ecosystems_24.png\" alt=\"\" /> " + sEcosystemName
                        sHTML += "</div>"

                        sHTML += "<div class=\"step_header_icons\">"

                        # if there's a description, show a tooltip
                        if sDesc:
                            sHTML += "<span class=\"ui-icon ui-icon-info ecosystem_tooltip\" title=\"" + sDesc + "\"></span>"

                        sHTML += "</div>"
                        sHTML += "<div class=\"clearfloat\"></div>"
                        sHTML += "</li>"

                    sHTML += "</ul>"
            else:
                uiGlobals.request.Messages.append("Unable to get Ecosystems - Missing Ecotemplate ID")

            return sHTML
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmAddEcotemplateAction(self):
        try:
            sEcoTemplateID = uiCommon.getAjaxArg("sEcoTemplateID")
            sActionName = uiCommon.getAjaxArg("sActionName")
            sOTID = uiCommon.getAjaxArg("sOTID")
    
            if not sEcoTemplateID or not sActionName or not sOTID:
                uiGlobals.request.Messages.append("Missing or invalid Ecotemplate ID, Action Name or Task.")
    
            sSQL = "insert into ecotemplate_action " \
                 " (action_id, action_name, ecotemplate_id, original_task_id)" \
                 " values (" \
                 " '" + uiCommon.NewGUID() + "'," \
                 " '" + sActionName + "'," \
                 " '" + sEcoTemplateID + "'," \
                 " '" + sOTID + "'" \
                 ")"
    
            if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                # don't raise an error if its just a PK collision.  That just means it's already there.
                if "Duplicate entry:" not in uiGlobals.request.db.error:
                    uiGlobals.request.Messages.append(uiGlobals.request.db.error)
    
            uiCommon.WriteObjectChangeLog(uiGlobals.CatoObjectTypes.EcoTemplate, sEcoTemplateID, "", "Action Added : [" + sActionName + "]")
    
            return ""
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    # delete an Action
    def wmDeleteEcotemplateAction(self):
        try:
            sActionID = uiCommon.getAjaxArg("sActionID")
    
            if not sActionID:
                return ""

            sSQL = "delete from action_plan where action_id = '" + sActionID + "'"
            sSQL = sSQL
            if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)

            sSQL = "delete from action_schedule where action_id = '" + sActionID + "'"
            sSQL = sSQL
            if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)

            sSQL = "delete from ecotemplate_action where action_id = '" + sActionID + "'"
            sSQL = sSQL
            if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)

            uiGlobals.request.db.tran_commit()

            #  if we made it here, so save the logs
            uiCommon.WriteObjectDeleteLog(uiGlobals.CatoObjectTypes.EcoTemplate, "", "", "Action [" + sActionID + "] removed from Ecotemplate.")
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

        return ""

    def wmGetEcotemplateActions(self):
        sEcoTemplateID = uiCommon.getAjaxArg("sEcoTemplateID")

        sHTML = ""

        try:
            if sEcoTemplateID:
                sSQL = "select ea.action_id, ea.action_name, ea.category, ea.action_desc, ea.action_icon, ea.original_task_id, ea.task_version," \
                    " t.task_id, t.task_code, t.task_name," \
                    " ea.parameter_defaults as action_param_xml, t.parameter_xml as task_param_xml" \
                    " from ecotemplate_action ea" \
                    " join task t on ea.original_task_id = t.original_task_id" \
                    " and t.default_version = 1" \
                    " where ea.ecotemplate_id = '" + sEcoTemplateID + "'" \
                    " order by ea.category, ea.action_name"

                dt = uiGlobals.request.db.select_all_dict(sSQL)
                if uiGlobals.request.db.error:
                    uiGlobals.request.Messages.append(uiGlobals.request.db.error)

                if dt:
                    for dr in dt:
                        sHTML += " <li class=\"ui-widget-content ui-corner-all action pointer\" id=\"ac_" + dr["action_id"] + "\">"
                        sHTML += ecoMethods.DrawEcotemplateAction(dr)
                        sHTML += " </li>"
            else:
                uiGlobals.request.Messages.append("Unable to get Actions - Missing Ecotemplate ID")

            return sHTML
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
    
    @staticmethod
    def DrawEcotemplateAction(dr):
        try:
            sHTML = ""

            # sActionID = dr["action_id"]
            sActionName = dr["action_name"]
            sCategory = (dr["category"] if dr["category"] else "")
            sDesc = (dr["action_desc"] if dr["action_desc"] else "")
            sIcon = ("action_default_48.png" if not dr["action_icon"] else dr["action_icon"])
            sOriginalTaskID = dr["original_task_id"]
            sTaskID = dr["task_id"]
            sTaskCode = (dr["task_code"] if dr["task_code"] else "")
            sTaskName = dr["task_name"]
            sVersion = (str(dr["task_version"]) if dr["task_version"] else "")
            sTaskParameterXML = (dr["task_param_xml"] if dr["task_param_xml"] else "")
            # sActionParameterXML = ("" if not dr["action_param_xml"]) else dr["action_param_xml"])

            sHTML += "<div class=\"ui-state-default step_header\">"

            sHTML += "<div class=\"step_header_title\">"
            sHTML += "<span class=\"action_category_lbl\">" + (sCategory + " - " if sCategory else "") + "</span>"
            sHTML += "<span class=\"action_name_lbl\">" + sActionName + "</span>"
            sHTML += "</div>"

            sHTML += "<div class=\"step_header_icons\">"
            sHTML += "<span class=\"ui-icon ui-icon-close action_remove_btn\" remove_id=\"" + sActionName + "\"" \
                " title=\"Delete\"></span>"
            sHTML += "</div>"

            sHTML += "</div>"


            # gotta clear the floats
            sHTML += "<div class=\"ui-widget-content step_detail\">"

            # Action Name
            sHTML += "Action: \n"
            sHTML += "<input type=\"text\" " \
                " column=\"action_name\"" \
                " class=\"code\"" \
                " value=\"" + sActionName + "\" />"

            # Category
            sHTML += "Category: \n"
            sHTML += "<input type=\"text\" " \
                " column=\"category\"" \
                " class=\"code\"" \
                " value=\"" + sCategory + "\" />"

            # Icon
            sHTML += "Icon: \n"
            sHTML += "<img class=\"action_icon\" src=\"static/images/actions/" + sIcon + "\" />\n"

            sHTML += "<br />"

            # Description
            sHTML += "Description:<br />\n"
            sHTML += "<textarea rows=\"4\"" \
                " column=\"action_desc\"" \
                " class=\"code\"" \
                ">" + sDesc + "</textarea>\n"

            sHTML += "<br />"

            # Task
            # hidden field
            sHTML += "<input type=\"hidden\" " \
                " column=\"original_task_id\"" \
                " value=\"" + sOriginalTaskID + "\" />"

            # visible stuff
            sHTML += "Task: \n"
            sHTML += "<input type=\"text\"" \
                " onkeydown=\"return false;\"" \
                " onkeypress=\"return false;\"" \
                " is_required=\"true\"" \
                " class=\"code w75pct task_name\"" \
                " value=\"" + sTaskCode + " : " + sTaskName + "\" />\n"
            if sTaskID != "":
                sHTML += "<span class=\"ui-icon ui-icon-pencil forceinline task_open_btn pointer\" title=\"Edit Task\"" \
                    " task_id=\"" + sTaskID + "\"></span>\n"
                sHTML += "<span class=\"ui-icon ui-icon-print forceinline task_print_btn pointer\" title=\"View Task\"" \
                    " task_id=\"" + sTaskID + "\"" \
                    " src=\"static/images/icons/printer.png\"></span>\n"

            # NOT SURE if this is a requirement.  The looping actually slows things down quite a bit
            # so I don't mind not doing it.

            # versions
            if uiCommon.IsGUID(sOriginalTaskID):
                sHTML += "<br />"
                sHTML += "Version: \n"
                sHTML += "<select " \
                    " column=\"task_version\"" \
                    " reget_on_change=\"true\">\n"
                # default
                sHTML += "<option " + (" selected=\"selected\"" if sVersion == "" else "") + " value=\"\">Default</option>\n"

                sSQL = "select version from task" \
                    " where original_task_id = '" + sOriginalTaskID + "'" \
                    " order by version"
                dtVer = uiGlobals.request.db.select_all_dict(sSQL)
                if uiGlobals.request.db.error:
                    return "Database Error:" + uiGlobals.request.db.error

                if dtVer:
                    for drVer in dtVer:
                        sHTML += "<option " + (" selected=\"selected\"" if sVersion == str(drVer["version"]) else "") + \
                            " value=\"" + str(drVer["version"]) + "\">" + \
                            str(drVer["version"]) + "</option>\n"
                else:
                    return "Unable to continue - Cannot find Version for Task [" + sOriginalTaskID + "]."

                sHTML += "</select>\n"


            # we have the parameter xml for the task here.
            # let's peek.  if there are parameters, show the button
            # if any are "required", but a ! by it.
            if sTaskParameterXML:
                xDoc = ET.fromstring(sTaskParameterXML)
                if xDoc is not None:
                    xParams = xDoc.findall("parameter")
                    if xParams is not None:
                        # there are task params!  draw the edit link

                        # are any of them required?
                        xRequired = xDoc.findall("parameter[@required='true']")

                        # # and most importantly, do the required ones have values?
                        # # this should be in a loop of xRequired, and looking in the other XML document.
                        # xEmpty1 = xDoc.findall("/parameters/parameter[@required='true']/values[not(text())]")
                        # xEmpty2 = xDoc.findall("/parameters/parameter[@required='true']/values[not(node())]")


                        sHTML += "<hr />"
                        sHTML += "<div class=\"action_param_edit_btn pointer\" style=\"vertical-align: bottom;\">"

                        if len(xRequired) > 0: #and (xEmpty1.Count() > 0 or xEmpty2.Count() > 0):
                            sHTML += "<img src=\"static/images/icons/status_unknown_16.png\" />"
                        else:
                            sHTML += "<span class=\"ui-icon ui-icon-pencil forceinline\"></span>"

                        sHTML += "<span> Edit Parameters</span>"
                        sHTML += "<span> (" + str(len(xParams)) + ")</span>"

                        # close the div
                        sHTML += "</div>"

            sHTML += "</div>"

            return sHTML
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()

    def wmGetEcotemplateAction(self):
        try:
            sActionID = uiCommon.getAjaxArg("sActionID")
    
            sHTML = ""

            if sActionID:
                sSQL = "select ea.action_id, ea.action_name, ea.category, ea.action_desc, ea.action_icon, ea.original_task_id, ea.task_version," \
                    " t.task_id, t.task_code, t.task_name," \
                    " ea.parameter_defaults as action_param_xml, t.parameter_xml as task_param_xml" \
                    " from ecotemplate_action ea" \
                    " join task t on ea.original_task_id = t.original_task_id" \
                    " and t.default_version = 1" \
                    " where ea.action_id = '" + sActionID + "'"

                dr = uiGlobals.request.db.select_row_dict(sSQL)
                if uiGlobals.request.db.error:
                    uiGlobals.request.Messages.append(uiGlobals.request.db.error)

                # GetDataRow returns a message if there are no rows...
                if dr:
                    sHTML = ecoMethods.DrawEcotemplateAction(dr)
            else:
                uiGlobals.request.Messages.append("Unable to get Actions - Missing Ecotemplate ID")

            return sHTML
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())


    
    def wmUpdateEcoTemplateAction(self):
        try:
            sEcoTemplateID = uiCommon.getAjaxArg("sEcoTemplateID")
            sActionID = uiCommon.getAjaxArg("sActionID")
            sColumn = uiCommon.getAjaxArg("sColumn")
            sValue = uiCommon.getAjaxArg("sValue")
            
            sUserID = uiCommon.GetSessionUserID()

            if uiCommon.IsGUID(sEcoTemplateID) and uiCommon.IsGUID(sUserID):
                # we encoded this in javascript before the ajax call.
                # the safest way to unencode it is to use the same javascript lib.
                # (sometimes the javascript and .net libs don't translate exactly, google it.)
                sValue = uiCommon.unpackJSON(sValue)
                sValue = uiCommon.TickSlash(sValue)
                
                #  check for existing name
                if sColumn == "action_name":
                    sSQL = "select action_id from ecotemplate_action where " \
                            " action_name = '" + sValue + "'" \
                            " and ecotemplate_id = '" + sEcoTemplateID + "'"

                    sValueExists = uiGlobals.request.db.select_col_noexcep(sSQL)
                    if uiGlobals.request.db.error:
                        uiGlobals.request.Messages.append("Unable to check for existing names [" + sEcoTemplateID + "]." + uiGlobals.request.db.error)

                    if sValueExists:
                        return sValue + " exists, please choose another value."

                sSetClause = sColumn + "='" + sValue + "'"

                # some columns on this table allow nulls... in their case an empty sValue is a null
                if sColumn == "action_desc" or sColumn == "category" or sColumn == "task_version":
                    if not sValue.replace(" ", ""):
                        sSetClause = sColumn + " = null"
                    else:
                        sSetClause = sColumn + "='" + sValue + "'"

                sSQL = "update ecotemplate_action set " + sSetClause + " where action_id = '" + sActionID + "'"

                if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                    uiGlobals.request.Messages.append("Unable to update Ecotemplate Action [" + sActionID + "]." + uiGlobals.request.db.error)

                uiCommon.WriteObjectChangeLog(uiGlobals.CatoObjectTypes.EcoTemplate, sEcoTemplateID, sActionID, "Action updated: [" + sSetClause + "]")
            else:
                uiGlobals.request.Messages.append("Unable to update Ecotemplate Action. Missing or invalid Ecotemplate/Action ID.")

            return ""
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
        
    def wmGetActionIcons(self):
        try:
            # the icons are in the icons/actions directory
            # get a list of them all, and draw them on the picker dialog
            sIconHTML = ""
            dirList=os.listdir("static/images/actions")
            for fname in dirList:
                sIconHTML += "<img class='action_picker_icon' icon_name='" + fname + "' src='static/images/actions/" + fname + "' />"
        
            return sIconHTML
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()

    def wmGetEcotemplateStorm(self):
        try:
            sEcoTemplateID = uiCommon.getAjaxArg("sEcoTemplateID")

            sFileType = ""
            sURL = ""
            sFileDesc = ""
            sStormFileJSON = ""
            bIsValid = False
            
            bIsValid, sErr, sFileType, sURL, sFileDesc, sStormFileJSON = ecoMethods.GetEcotemplateStormJSON(sEcoTemplateID)
            
            sb = []
            
            sb.append("{")
            sb.append("\"%s\" : \"%s\"," % ("IsValid", bIsValid))
            sb.append("\"%s\" : \"%s\"," % ("Error", uiCommon.packJSON(sErr)))
            sb.append("\"%s\" : \"%s\"," % ("FileType", sFileType))
            sb.append("\"%s\" : \"%s\"," % ("URL",  uiCommon.packJSON(sURL)))
            sb.append("\"%s\" : \"%s\"," % ("Description", uiCommon.packJSON(sFileDesc)))
            sb.append("\"%s\" : \"%s\"," % ("Text", uiCommon.packJSON(sStormFileJSON)))
            sb.append("\"%s\" : \"%s\"," % ("HTMLDescription", uiCommon.packJSON(uiCommon.FixBreaks(uiCommon.SafeHTML(sFileDesc)))))
            sb.append("\"%s\" : \"%s\"" % ("HTMLText", uiCommon.packJSON(uiCommon.FixBreaks(uiCommon.SafeHTML(sStormFileJSON)))))
            sb.append("}")
            
            return "".join(sb)
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()

    @staticmethod
    def GetEcotemplateStormJSON(sEcoTemplateID): 
        bIsValid = False
        sErr = ""
        sFileType = ""
        sURL = ""
        sFileDesc = ""
        sStormFileJSON = ""
        try:
            if sEcoTemplateID:
                sSQL = "select storm_file_type, storm_file" \
                    " from ecotemplate" \
                    " where ecotemplate_id = '" + sEcoTemplateID + "'"

                dr = uiGlobals.request.db.select_row_dict(sSQL)
                if uiGlobals.request.db.error:
                    uiGlobals.request.Messages.append(uiGlobals.request.db.error)
                
                # now, we'll validate the json here as a safety precaution, but we're sending the whole storm file to the client
                # where the parameters and description will be parsed out and displayed.
                # this is really no different than where we send entire parameter_xml document to the client
                
                sFileType = (dr["storm_file_type"] if dr["storm_file_type"] else "")
                sStormFile = (dr["storm_file"] if dr["storm_file"] else "")
                
                if sStormFile:
                    if sFileType == "URL":
                        # if it's a URL we try: to get it and parse it.
                        # if we can't, we just send back a nice message.
                        
                        # for display purposes, we'll be sending back the URL as well as the results
                        sURL = sStormFile
                        
                        
                        # using our no fail routine here, error handling later if needed
                        try:
                            sStormFileJSON = uiCommon.HTTPGetNoFail(sURL)
                        except Exception:
                            sErr = "Error getting Storm from URL [" + sURL + "]. " + traceback.format_exc()
                    else:
                        # if it's not a URL we assume it's actual JSON text.
                        sStormFileJSON = sStormFile
                    
                    if sStormFileJSON:
                        try:
                            # the process is simple...
                            # 1) parse the json into a dict
                            # 2) make sure a few key sections exist
                            dic = json.loads(sStormFileJSON)
        
                            if dic.has_key("Description"):
                                sFileDesc = (dic["Description"] if dic["Description"] else "")
    
                            # VALIDATION
                            # we can test for certain values, and return false unless they exist.
                            if dic.has_key("Mappings") and dic.has_key("Resources"):
                                bIsValid = True
                            else:
                                sErr += "Document must contain a Mappings and a Resources section."
                                
                        except Exception:
                            sErr = traceback.format_exc()
                    else:
                        sErr = "Storm File is empty or URL returned nothing."
                else:
                    sErr = "No Storm File or URL defined."
            else:
                uiGlobals.request.Messages.append("Unable to get Storm Details - Missing Ecotemplate ID")

            # returns a big tuple
            return bIsValid, sErr, sFileType, sURL, sFileDesc, sStormFileJSON
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmGetStormFileFromURL(self):
        try:
            sURL = uiCommon.getAjaxArg("sURL")
            sURL = uiCommon.unpackJSON(sURL)
            sStormFileJSON = uiCommon.HTTPGetNoFail(sURL)
            if sStormFileJSON:
                return uiCommon.packJSON(sStormFileJSON)
            else:
                return ""
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return ""

    def wmGetEcosystemsTable(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sFilter = uiCommon.getAjaxArg("sSearch")
            sAccountID = uiCommon.getAjaxArg("sAccountID")

            sHTML = ""
            ets = ecosystem.Ecosystems(sAccountID, sFilter)
            if ets:
                for row in ets.rows:
                    sHTML += "<tr ecosystem_id=\"%s\">" % row["ecosystem_id"]
                    sHTML += "<td class=\"chkboxcolumn\">"
                    sHTML += "<input type=\"checkbox\" class=\"chkbox\"" \
                    " id=\"chk_%s\"" \
                    " object_id=\"%s\"" \
                    " tag=\"chk\" />" % (row["ecosystem_id"], row["ecosystem_id"])
                    sHTML += "</td>"
                    
                    sHTML += "<td class=\"selectable\">%s</td>" % row["ecosystem_name"]
                    sHTML += "<td class=\"selectable\">%s</td>" % row["ecotemplate_name"]
                    sHTML += "<td class=\"selectable\">%s</td>" % (row["ecosystem_desc"] if row["ecosystem_desc"] else "")
                    sHTML += "<td class=\"selectable\">%s</td>" % str(row["created_dt"])
                    sHTML += "<td class=\"selectable\">%s</td>" % (row["last_update_dt"])
                    sHTML += "<td class=\"selectable\">%s</td>" % row["num_objects"]
                    
                    sHTML += "</tr>"
    
            return sHTML    
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmGetEcotemplatesJSON(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sFilter = uiCommon.getAjaxArg("sFilter")
            ets = ecosystem.Ecotemplates(sFilter)
            if ets:
                return ets.AsJSON()
            #should not get here if all is well
            return "{'result':'fail','error':'Failed to get Ecotemplates using filter [" + sFilter + "].'}"
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()

    def wmCreateEcosystem(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sName = uiCommon.getAjaxArg("sName")
            sDescription = uiCommon.getAjaxArg("sDescription")
            sEcotemplateID = uiCommon.getAjaxArg("sEcotemplateID")
            sAccountID = uiCommon.getAjaxArg("sAccountID")
            sStormStatus = uiCommon.getAjaxArg("sStormStatus")
            sParameterXML = uiCommon.getAjaxArg("sCloudID")
            sCloudID = uiCommon.getAjaxArg("sCloudID")
    
            if not sAccountID:
                return "{\"info\" : \"Unable to create - No Cloud Account selected.\"}"
            if not sEcotemplateID:
                return "{\"info\" : \"Unable to create - An Ecosystem Template is required.\"}"


            e, sErr = ecosystem.Ecosystem.DBCreateNew(uiCommon.unpackJSON(sName), sEcotemplateID, sAccountID, uiCommon.unpackJSON(sDescription), sStormStatus, uiCommon.unpackJSON(sParameterXML), sCloudID)
            if sErr:
                return "{\"error\" : \"" + sErr + "\"}"
            if e == None:
                return "{\"error\" : \"Unable to create Ecosystem.\"}"

            uiCommon.WriteObjectAddLog(uiGlobals.CatoObjectTypes.Ecosystem, e.ID, e.Name, "Ecosystem created.")
            
            return "{\"id\" : \"%s\"}" % e.ID

        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()

    def wmDeleteEcosystems(self):
        try:
            sDeleteArray = uiCommon.getAjaxArg("sDeleteArray")
            if not sDeleteArray:
                return ""
    
            sDeleteArray = uiCommon.QuoteUp(sDeleteArray)

            sSQL = "delete from action_plan where ecosystem_id in (" + sDeleteArray + ")"
            if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)

            sSQL = "delete from action_schedule where ecosystem_id in (" + sDeleteArray + ")"
            if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)

            sSQL = "delete from object_registry where object_id in (" + sDeleteArray + ")"
            if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)

            sSQL = "delete from ecosystem_object where ecosystem_id in (" + sDeleteArray + ")"
            if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)

            sSQL = "delete from ecosystem_log where ecosystem_id in (" + sDeleteArray + ")"
            if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)

            sSQL = "delete from ecosystem where ecosystem_id in (" + sDeleteArray + ")"
            if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
            
            uiGlobals.request.db.tran_commit()
                
            uiCommon.WriteObjectDeleteLog(uiGlobals.CatoObjectTypes.Ecosystem, "", "", "Ecosystem(s) Deleted [" + sDeleteArray + "]")

            return "{\"result\" : \"success\"}"
            
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()
