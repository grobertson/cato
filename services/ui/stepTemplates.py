import uiCommon
import uiGlobals
import taskCommands
from catocommon import catocommon

# LIKE uiCommon - this isn't a class that gets instantiated ... it's just a collection of 
# all the functions used to draw the Task Steps.

def DrawFullStep(oStep):
    sStepID = oStep.ID
    
    # this uses a uiCommon function, because the functions were cached in the session
    fn = uiCommon.GetTaskFunction(oStep.FunctionName)
    if fn:
        oStep.Function = fn
    else:
        #the function doesn't exist (was probably deprecated)
        #we need at least a basic strip with a delete button
        sNoFunc = "<li class=\"step\" id=\"" + sStepID + "\">"            
        sNoFunc += "    <div class=\"ui-state-default ui-state-highlight step_header\" id=\"step_header_" + sStepID + "\">"
        sNoFunc += "        <div class=\"step_header_title\"><img src=\"static/images/icons/status_unknown_16.png\" /></div>"
        sNoFunc += "        <div class=\"step_header_icons\">"
        sNoFunc += "            <span class=\"step_delete_btn\" remove_id=\"" + sStepID + "\"><img src=\"static/images/icons/fileclose.png\" alt=\"\" title=\"Delete Step\" /></span>"
        sNoFunc += "        </div>"
        sNoFunc += "    </div>"
        sNoFunc += "    <div id=\"step_detail_" + sStepID + "\" class=\"ui-widget-content ui-state-highlight ui-corner-bottom step_detail\" >"
        sNoFunc += "Error building Step - Unable to get the details for the command type '" + oStep.FunctionName + "'.<br />"
        sNoFunc += "This command type may have been deprecated - check the latest Cato release notes.<br />"
        sNoFunc += "    </div>"
        sNoFunc += "</li>"

        return sNoFunc

    
    sExpandedClass = ("" if oStep.UserSettings.Visible else "step_collapsed")
    sSkipStepClass = ("step_skip" if oStep.Commented else "")
    sSkipHeaderClass = ("step_header_skip" if oStep.Commented else "")
    sSkipIcon = ("static/images/icons/cnrgrey.png" if oStep.Commented else "static/images/icons/cnr.png")

    # pay attention
    # this overrides the 'expanded class', making the step collapsed by default if it's commented out.
    # the 'skip' overrides the saved visibility preference.
    if oStep.Commented:
        sExpandedClass = "step_collapsed"
    

    sMainHTML = ""
    sVariableHTML = ""
    sOptionHTML = ""
    
    #what's the 'label' for the step strip?
    #(hate this... wish the label was consistent across all step types)
    #hack for initial loading of the step... don't show the order if it's a "-1"... it's making a
    #strange glitch in the browser...you can see it update
    sIcon = ("" if not oStep.Function.Icon else "static/images/" + oStep.Function.Icon)
    sStepOrder = ("" if oStep.Order == -1 else str(oStep.Order))
    sLabel = "<img class=\"step_header_function_icon\" src=\"" + sIcon + "\" alt=\"\" />" \
        "<span class=\"step_order_label\">" + str(sStepOrder) + "</span> : " + \
        oStep.Function.Category.Label + " - " + oStep.Function.Label

    #show a useful snip in the title bar.
    #notes trump values, and not all commands show a value snip
    #but certain ones do.
    sSnip = ""
    if oStep.Description:
        sSnip = uiCommon.GetSnip(oStep.Description, 75)
        #special words get in indicator icon, but only one in highest order
        if "IMPORTANT" in sSnip:
            sSnip = "<img src=\"static/images/icons/flag_red.png\" />" + sSnip.replace("IMPORTANT","")
        elif "TODO" in sSnip:
            sSnip = "<img src=\"static/images/icons/flag_yellow.png\" />" + sSnip.replace("TODO","")
        elif "NOTE" in sSnip or "INFO" in sSnip:
            sSnip = "<img src=\"static/images/icons/flag_blue.png\" />" + sSnip.replace("NOTE","").replace("INFO","")
    #else:
    #    sSnip = uiCommon.GetSnip(GetValueSnip(oStep), 75)

    
    sLabel += ("" if sSnip == "" else "<span style=\"padding-left:15pxfont-style:italicfont-weight:normal\">[" + sSnip + "]</span>")

    sLockClause = (" onclick=\"return false\"" if oStep.Locked else "")

    
    sMainHTML += "<li class=\"step " + sSkipStepClass + "\" id=\"" + sStepID + "\" " + sLockClause + ">"
    
    # the "commented" property is just a common field on all steps - it's hidden in the header.
    sCommentFieldID = uiCommon.NewGUID()
    sMainHTML += "<input type=\"text\"" \
        " value=\"" + ("1" if oStep.Commented else "0") + "\"" + \
        CommonAttribsWithID(sStepID, "_common", False, "commented", sCommentFieldID, "hidden") + \
        " />"
    
    
    # step expand image
    sExpandImage = "expand_down.png"
    if sExpandedClass == "step_collapsed": 
        sExpandImage = "expand_up.png"

    sMainHTML += "    <div class=\"ui-state-default step_header " + sSkipHeaderClass + "\"" \
        " id=\"step_header_" + sStepID + "\">"
    sMainHTML += "        <div class=\"step_header_title\">"
    sMainHTML += "            <span class=\"step_toggle_btn\" step_id=\"" + sStepID + "\">" \
    " <img class=\"expand_image\" src=\"static/images/icons/" + sExpandImage + "\" alt=\"\" title=\"Hide/Show Step\" /></span>"
    sMainHTML += "            <span>" + sLabel + "</span>"
    sMainHTML += "        </div>"
    sMainHTML += "        <div class=\"step_header_icons\">"

    #this button will copy a step into the clipboard.
    sMainHTML += "            <span><img id=\"step_copy_btn_" + sStepID + "\"" \
        " class=\"step_copy_btn\" step_id=\"" + sStepID + "\"" \
        " src=\"static/images/icons/editcopy_16.png\" alt=\"\" title=\"Copy this Step to your Clipboard\"/></span>"

    #this button is data enabled.  it controls the value of the hidden field at the top of the step.
    sMainHTML += "            <span><img id=\"step_skip_btn_" + sStepID + "\"" \
        " class=\"step_skip_btn\" step_id=\"" + sStepID + "\"" \
        " datafield_id=\"" + sCommentFieldID + "\"" \
        " src=\"" + sSkipIcon + "\" alt=\"\" title=\"Skip this Step\"/></span>"

    sMainHTML += "            <span class=\"step_delete_btn\" remove_id=\"" + sStepID + "\">" \
        " <img src=\"static/images/icons/fileclose.png\" alt=\"\" title=\"Delete Step\" /></span>"
    sMainHTML += "        </div>"
    sMainHTML += "    </div>"
    sMainHTML += "    <div id=\"step_detail_" + sStepID + "\"" \
        " class=\"ui-widget-content ui-corner-bottom step_detail " + sExpandedClass + "\" >"
    
    """
    #!!! this is probably gonna have to return a tuple, unless we wanna get options and variables another way (not likely)
    sMainHTML += GetStepTemplate(oStep, ref sOptionHTML, ref sVariableHTML)
    """
    #comment steps don't have a common section - all others do
    if oStep.FunctionName != "comment":
        sMainHTML += DrawStepCommon(oStep, sOptionHTML, sVariableHTML)
    
    
    sMainHTML += "    </div>"

    sMainHTML += "</li>"

    return sMainHTML

def CommonAttribsWithID(sStepID, sFunction, bRequired, sXPath, sElementID, sAdditionalClasses):
    # requires a guid ID passed in - this one will be referenced client side
    return " id=\"" + sElementID + "\"" \
        " step_id=\"" + sStepID + "\"" \
        " function=\"" + sFunction + "\"" \
        " xpath=\"" + sXPath + "\"" \
        " te_group=\"step_fields\"" \
        " class=\"step_input code " + sAdditionalClasses + "\"" + \
        (" is_required=\"true\"" if bRequired else "") + \
        " onchange=\"javascript:onStepFieldChange(this, '" + sStepID + "', '" + sXPath + "');\""

def CommonAttribs(sStepID, sFunction, bRequired, sXPath, sAdditionalClasses):
    # creates a new id
    return " id=\"x" + uiCommon.NewGUID() + "\"" \
        " step_id=\"" + sStepID + "\"" \
        " function=\"" + sFunction + "\"" \
        " xpath=\"" + sXPath + "\"" \
        " te_group=\"step_fields\"" \
        " class=\"step_input code " + sAdditionalClasses + "\"" + \
        (" is_required=\"true\"" if bRequired else "") + \
        " onchange=\"javascript:onStepFieldChange(this, '" + sStepID + "', '" + sXPath + "');\""

def DrawStepCommon(oStep, sOptionHTML, sVariableHTML):
    sStepID = oStep.ID
    
    #this is the section that is common to all steps.
    sHTML = ""
    sHTML += "        <hr />"
    sHTML += "        <div class=\"step_common\" >"
    sHTML += "            <div class=\"step_common_header\">"
    sShowOnLoad = oStep.UserSettings.Button
    
    #pill buttons
    if sVariableHTML != "":
        sHTML += "                <span class=\"step_common_button " + ("step_common_button_active" if sShowOnLoad == "variables" else "") + "\"" \
            " id=\"btn_step_common_detail_" + sStepID + "_variables\"" \
            " button=\"variables\"" \
            " step_id=\"" + sStepID + "\">Variables</span>"
    if sOptionHTML != "":
        sHTML += "                <span class=\"step_common_button " + ("step_common_button_active" if sShowOnLoad == "options" else "") + "\"" \
            " id=\"btn_step_common_detail_" + sStepID + "_options\"" \
            " button=\"options\"" + " step_id=\"" + sStepID + "\">Options</span>"
    sHTML += "                <span class=\"step_common_button " + ("step_common_button_active" if sShowOnLoad == "notes" else "") + "\"" \
        " id=\"btn_step_common_detail_" + sStepID + "_notes\"" \
        " button=\"notes\"" + " step_id=\"" + sStepID + "\">Notes</span>"
    sHTML += "                <span class=\"step_common_button " + ("step_common_button_active" if sShowOnLoad == "help" else "") + "\"" \
        " id=\"btn_step_common_detail_" + sStepID + "_help\"" \
        " button=\"help\"" \
        " step_id=\"" + sStepID + "\">Help</span>"
    sHTML += "            </div>"
    
    #sections
    sHTML += "            <div id=\"step_common_detail_" + sStepID + "_notes\"" \
        " class=\"step_common_detail " + ("" if sShowOnLoad == "notes" else "step_common_collapsed") + "\"" \
        " style=\"height: 100px;\">"
    sHTML += "                <textarea rows=\"4\" " + CommonAttribs(sStepID, "_common", False, "step_desc", "") + \
        " help=\"Enter notes for this Command.\" reget_on_change=\"true\">" + oStep.Description + "</textarea>"
    sHTML += "            </div>"
    sHTML += "            <div id=\"step_common_detail_" + sStepID + "_help\"" \
        " class=\"step_common_detail " + ("" if sShowOnLoad == "help" else "step_common_collapsed") + "\"" \
        " style=\"height: 200px;\">"
    sHTML += oStep.Function.Help
    sHTML += "            </div>"
    
    #some steps generate custom options we want in this pane
    #but we don't show the panel if there aren't any
    if sOptionHTML != "":
        sHTML += "          <div id=\"step_common_detail_" + sStepID + "_options\"" \
            " class=\"step_common_detail " + ("" if sShowOnLoad == "options" else "step_common_collapsed") + "\">"
        sHTML += "              <div>"
        sHTML += sOptionHTML
        sHTML += "              </div>"
        sHTML += "          </div>"
    
    #some steps have variables
    #but we don't show the panel if there aren't any
    if sVariableHTML != "":
        sHTML += "          <div id=\"step_common_detail_" + sStepID + "_variables\"" \
            " class=\"step_common_detail " + ("" if sShowOnLoad == "variables" else "step_common_collapsed") + "\">"
        sHTML += "              <div>"
        sHTML += sVariableHTML
        sHTML += "              </div>"
        sHTML += "          </div>"
    #close it out
    sHTML += "        </div>"
    
    return sHTML
