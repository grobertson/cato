import sys
import traceback
from uiCommon import log
import uiCommon
import xml.etree.ElementTree as ET
import providers
from uiGlobals import ConnectionTypes
import uiGlobals
import task

# LIKE uiCommon - this isn't a class that gets instantiated ... it's just a collection of 
# all the functions used to draw the Task Steps.
def GetSingleStep(sStepID, sUserID):
    return task.Step.ByIDWithSettings(sStepID, sUserID)
    
def DrawFullStep(oStep):
    sStepID = oStep.ID
    
    # this uses a uiCommon function, because the functions were cached
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
    sSkipIcon = ("pause" if oStep.Commented else "play")
    sSkipVal = ("1" if oStep.Commented else "0")

    # pay attention
    # this overrides the 'expanded class', making the step collapsed by default if it's commented out.
    # the 'skip' overrides the saved visibility preference.
    if oStep.Commented:
        sExpandedClass = "step_collapsed"
    

    sMainHTML = ""
    
    #what's the 'label' for the step strip?
    #(hate this... wish the label was consistent across all step types)
    #hack for initial loading of the step... don't show the order if it's a "-1"... it's making a
    #strange glitch in the browser...you can see it update
    sIcon = ("" if not oStep.Function.Icon else oStep.Function.Icon)
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
            sSnip = "<img src=\"static/images/icons/flag_red.png\" />" + sSnip.replace("IMPORTANT", "")
        elif "TODO" in sSnip:
            sSnip = "<img src=\"static/images/icons/flag_yellow.png\" />" + sSnip.replace("TODO", "")
        elif "NOTE" in sSnip or "INFO" in sSnip:
            sSnip = "<img src=\"static/images/icons/flag_blue.png\" />" + sSnip.replace("NOTE", "").replace("INFO", "")
    #else:
    #    sSnip = uiCommon.GetSnip(GetValueSnip(oStep), 75)

    
    sLabel += ("" if sSnip == "" else "<span style=\"padding-left:15px; font-style:italic; font-weight:normal\">[" + sSnip + "]</span>")

    sLockClause = (" onclick=\"return false\"" if oStep.Locked else "")

    
    sMainHTML += "<li class=\"step " + sSkipStepClass + "\" id=\"" + sStepID + "\" " + sLockClause + ">"
    
    # TODO - stop doing this as a special field and just do a web method for comment/uncomment
    # the "commented" property is just a common field on all steps - it's hidden in the header.
#    sCommentFieldID = uiCommon.NewGUID()
#    sMainHTML += "<input type=\"text\"" \
#        " value=\"" + ("1" if oStep.Commented else "0") + "\"" + \
#        CommonAttribsWithID(oStep, "_common", False, "commented", sCommentFieldID, "hidden") + \
#        " />"
    
    
    # step expand image
    sExpandImage = "triangle-1-s"
    if sExpandedClass == "step_collapsed": 
        sExpandImage = "triangle-1-e"

    sMainHTML += "    <div class=\"ui-state-default step_header " + sSkipHeaderClass + "\"" \
        " id=\"step_header_" + sStepID + "\">"
    sMainHTML += "        <div class=\"step_header_title\">"
    sMainHTML += "            <span class=\"step_toggle_btn\" step_id=\"" + sStepID + "\">" \
    " <img class=\"ui-icon ui-icon-" + sExpandImage + " forceinline expand_image\" title=\"Hide/Show Step\" /></span>"
    sMainHTML += "            <span>" + sLabel + "</span>"
    sMainHTML += "        </div>"
    sMainHTML += "        <div class=\"step_header_icons\">"

    #this button will copy a step into the clipboard.
    sMainHTML += "            <span id=\"step_copy_btn_" + sStepID + "\"" \
        " class=\"ui-icon ui-icon-copy forceinline step_copy_btn\" step_id=\"" + sStepID + "\"" \
        " title=\"Copy this Step to your Clipboard\"></span>"

    #this button is data enabled.  it controls the value of the hidden field at the top of the step.
    sMainHTML += "            <span id=\"step_skip_btn_" + sStepID + "\" skip=\"" + sSkipVal + "\"" \
        " class=\"ui-icon ui-icon-" + sSkipIcon + " forceinline step_skip_btn\" step_id=\"" + sStepID + "\"" \
        " title=\"Skip this Step\"></span>"
# see above TODO        " datafield_id=\"" + sCommentFieldID + "\"" \

    sMainHTML += "            <span class=\"ui-icon ui-icon-close forceinline step_delete_btn\" remove_id=\"" + sStepID + "\">" \
        " title=\"Delete Step\"></span>"
    sMainHTML += "        </div>"
    sMainHTML += "    </div>"
    sMainHTML += "    <div id=\"step_detail_" + sStepID + "\"" \
        " class=\"ui-widget-content ui-corner-bottom step_detail " + sExpandedClass + "\" >"
    
    #!!! this returns a tuple with optional "options" and "variable" html
    sStepHTML, sOptionHTML, sVariableHTML = GetStepTemplate(oStep)
    sMainHTML += sStepHTML
    
    #comment steps don't have a common section - all others do
    if oStep.FunctionName != "comment":
        sMainHTML += DrawStepCommon(oStep, sOptionHTML, sVariableHTML)
    
    
    sMainHTML += "    </div>"

    sMainHTML += "</li>"

    return sMainHTML

def GetStepTemplate(oStep):
    if oStep.IsValid == False:
        return "This step is damaged.  Check the log file for details.  It may be necessary to delete and recreate it.", "", ""

    sFunction = oStep.FunctionName
    sHTML = ""
    sOptionHTML = ""
    sVariableHTML = ""
    bShowVarButton = True
    # NOTE: If you are adding a new command type, be aware that
    # you MIGHT need to modify the code in taskMethods for the wmAddStep function.
    # (depending on how your new command works)

    # Special Commands have their own render functions.
    # What makes 'em special?  Basically they have dynamic content, or hardcoded rules.
    # several commands have 'embedded' content, and draw a 'drop zone'
    # if a command "populates variables", it currently has to be hardcoded
    # in some cases, they even update the db on render to keep certain values clean
    
    ## PERSONAL NOTE - while converting the hardcoded ones, make use of the Draw Field function
    ## at least then things will be more consistent, and less html in the hardcoding.
    
    ## AND MAKE SURE to reference the old code when building out the xml, to make sure nothing is missed
    # (styles, etc.)

    if sFunction.lower() == "new_connection":
        sHTML = NewConnection(oStep)
    elif sFunction.lower() == "codeblock":
        sHTML = Codeblock(oStep)
    elif sFunction.lower() == "if":
        sHTML = If(oStep)
    elif sFunction.lower() == "sql_exec":
        sHTML, bShowVarButton = SqlExec(oStep)
    elif sFunction.lower() == "set_variable":
        sHTML = SetVariable(oStep)
    elif sFunction.lower() == "clear_variable":
        sHTML = ClearVariable(oStep)
    elif sFunction.lower() == "wait_for_tasks":
        sHTML = WaitForTasks(oStep)
    elif sFunction.lower() == "dataset":
        sHTML = Dataset(oStep)
    elif sFunction.lower() == "subtask":
        sHTML = Subtask(oStep)
    elif sFunction.lower() == "run_task":
        sHTML = RunTask(oStep)
    elif sFunction.lower() == "get_ecosystem_objects":
        sHTML = GetEcosystemObjects(oStep)
    elif sFunction.lower() == "transfer":
        sHTML = "Not Yet Available" #Transfer(oStep)
    elif sFunction.lower() == "set_asset_registry":
        sHTML = "Not Yet Available" #SetAssetRegistry(oStep)
    elif sFunction.lower() == "loop":
        sHTML = Loop(oStep)
    elif sFunction.lower() == "while":
        sHTML = While(oStep)
    elif sFunction.lower() == "exists":
        sHTML = Exists(oStep)
    else:
        # We didn't find one of our built in commands.  That's ok - most commands are drawn from their XML.
        sHTML, sOptionHTML = DrawStepFromXMLDocument(oStep)
    
    if bShowVarButton:
        # IF a command "populates variables" it will be noted in the command xml
        # is the variables xml attribute true?
        xd = oStep.FunctionXDoc
        if xd is not None:
            sPopulatesVars = xd.get("variables", "false")
            log("Populates Variables? " + sPopulatesVars, 4)
            if uiCommon.IsTrue(sPopulatesVars):
                sVariableHTML += DrawVariableSectionForDisplay(oStep, True)
    
    # This returns a Tuple with three values.
    return sHTML, sOptionHTML, sVariableHTML

def DrawStepFromXMLDocument(oStep):
    xd = oStep.FunctionXDoc
    # 
    # * This block reads the XML for a step and uses certain node attributes to determine how to draw the step.
    # *
    # * attributes include the type of input control to draw
    # * the size of the field,
    # * whether or not to HTML break after
    # * etc
    # *
    # 
    sHTML = ""
    sOptionHTML = ""
    #log("Command XML:", 4)
    #log(ET.tostring(xd), 4)
    if xd is not None:
        # for each node in the function element
        # each node will become a field on the step.
        # some fields may be defined to go on an "options tab", in which case they will come back as sNodeOptionHTML
        # you'll never get back both NodeHTML and OptionHTML - one will always be blank.
        for xe in xd:
            # PAY ATTENTION!
            # there are a few xml nodes inside the function_xml that are reserved for internal features.
            # these nodes WILL NOT BE DRAWN as part of the step editing area.
            
            # "variables" is a reserved node name
            if xe.tag == "step_variables": 
                continue
            
            # now, for embedded content, the step may have an xpath "prefix"
            sXPath = xe.tag
            
            log("Drawing [" + sXPath + "]", 4)
            sNodeHTML, sNodeOptionHTML = DrawNode(xe, sXPath, oStep)
            sHTML += sNodeHTML
            sOptionHTML += sNodeOptionHTML
            
    return sHTML, sOptionHTML
    
def DrawNode(xeNode, sXPath, oStep):
    sHTML = ""
    sNodeName = xeNode.tag
    
    sNodeLabel = xeNode.get("label", "")
    sIsEditable = xeNode.get("is_array", "")
    bIsEditable = uiCommon.IsTrue(sIsEditable)
    
    sOptionTab = xeNode.get("option_tab", "")
    
    #TODO 4-12-12: this is problematic - there's no easy way in elementtree to reference a parent
    # this may require iterating the tree again.
    # or rethink how we know a node is "removable"
    sIsRemovable = "" #xeNode.PARENT.get("is_array", "")
    bIsRemovable = uiCommon.IsTrue(sIsRemovable)
    
    log("-- Label: " + sNodeLabel, 4)
    log("-- Editable: " + sIsEditable + " - " + str(bIsEditable), 4)
    log("-- Removable: " + sIsRemovable + " - " + str(bIsRemovable), 4)
    log("-- Elements: " + str(len(xeNode)), 4)
    log("-- Option Field?: " + sOptionTab, 4)
    
    #if a node has children we'll draw it with some hierarchical styling.
    #AND ALSO if it's editable, even if it has no children, we'll still draw it as a container.
    
    # this dict holds the nodes that have the same name
    # meaning they are part of an array
    dictNodes = {}
    
    if len(xeNode) > 0 or bIsEditable:
        #if there is only one child, AND it's not part of an array
        #don't draw the header or the bounding box, just a composite field label.
        if len(xeNode) == 1 and not bIsEditable:
            log("-- no more children ... drawing ... ", 4)
            #get the first (and only) node
            xeOnlyChild = xeNode.find("*[1]")
            
            #call DrawNode just on the off chance it actually has children
            sChildXPath = sXPath + "/" + xeOnlyChild.tag
            # DrawNode returns a tuple, but here we only care about the first value
            # because "editable" nodes shouldn't be options.
            sNodeHTML, sOptionHTML = DrawNode(xeOnlyChild, sChildXPath, oStep)
            if sOptionTab:
                sHTML += sNodeName + "." + sOptionHTML
            else:
                sHTML += sNodeName + "." + sNodeHTML
            
            #since we're making it composite, the parents are gonna be off.  Go ahead and draw the delete link here.
            if bIsRemovable:
                sHTML += "<span class=\"fn_nodearray_remove_btn pointer\" xpath_to_delete=\"" + sXPath + "\" step_id=\"" + oStep.ID + "\">"
                sHTML += "<img style=\"width:10px; height:10px; margin-right: 4px;\" src=\"static/images/icons/fileclose.png\" alt=\"\" title=\"Remove\" /></span>"
        else: #there is more than one child... business as usual
            log("-- more children ... drawing and drilling down ... ", 4)
            sHTML += "<div class=\"ui-widget-content ui-corner-bottom step_group\">" #this section
            sHTML += "  <div class=\"ui-state-default step_group_header\">" #header
            sHTML += "      <div class=\"step_header_title\">" + sNodeLabel + "</div>"
            #look, I know this next bit is crazy... but not really.
            #if THIS NODE is an editable array, it means you can ADD CHILDREN to it.
            #so, it gets an add link.
            sHTML += "<div class=\"step_header_icons\">" #step header icons
            if bIsEditable:
                sHTML += "<div class=\"fn_nodearray_add_btn pointer\"" + " step_id=\"" + oStep.ID + "\"" \
                    " xpath=\"" + sXPath + "\">" \
                    "<img style=\"width:10px; height:10px;\" src=\"static/images/icons/edit_add.png\"" \
                    " alt=\"\" title=\"Add another...\" /></div>"
    
            #BUT, if this nodes PARENT is editable, that means THIS NODE can be deleted.
            #so, it gets a delete link
            #you can't remove unless there are more than one
            if bIsRemovable:
                sHTML += "<span class=\"fn_nodearray_remove_btn pointer\" xpath_to_delete=\"" + sXPath + "\" step_id=\"" + oStep.ID + "\">"
                sHTML += "<img style=\"width:10px; height:10px;\" src=\"static/images/icons/fileclose.png\" alt=\"\" title=\"Remove\" /></span>"
            sHTML += "</div>" #end step header icons
            sHTML += "  </div>" #end header
    
            for xeChildNode in xeNode:
                sChildNodeName = xeChildNode.tag
                sChildXPath = sXPath + "/" + sChildNodeName
    
                #here's the magic... are there any children nodes here with the SAME NAME?
                #if so they need an index on the xpath
                if len(xeNode.find(sChildNodeName)) > 1:
                    #since the document won't necessarily be in perfect order,
                    #we need to keep track of same named nodes and their indexes.
                    #so, stick each array node up in a lookup table.
                    #is it already in my lookup table?
                    iLastIndex = 0
                    if dictNodes.has_key(sChildNodeName):
                        #not there, add it
                        iLastIndex = 1
                        dictNodes[sChildNodeName] = iLastIndex
                    else:
                        #there, increment it and set it
                        iLastIndex += 1
                        dictNodes[sChildNodeName] = iLastIndex
                    sChildXPath = sChildXPath + "[" + str(iLastIndex) + "]"
                    
                # it's not possible for an 'editable' node to be in the options tab if it's parents aren't,
                # so here we ignore the options return
                sNodeHTML, sBunk = DrawNode(xeChildNode, sChildXPath, oStep)
                if sBunk:
                    log("WARNING: This shouldn't have returned 'option' html.", 2)
                sHTML += sNodeHTML
    
            sHTML += "</div>"
    else: #end section
        sHTML += DrawField(xeNode, sXPath, oStep)
        #it may be that these fields themselves are removable
        if bIsRemovable:
            sHTML += "<span class=\"fn_nodearray_remove_btn pointer\" xpath_to_delete=\"" + sXPath + "\" step_id=\"" + oStep.ID + "\">"
            sHTML += "<img style=\"width:10px; height:10px; margin-right: 4px;\" src=\"static/images/icons/fileclose.png\" alt=\"\" title=\"Remove\" /></span>"
    
    #ok, now that we've drawn it, it might be intended to go on the "options tab".
    #if so, stick it there
    if sOptionTab:
        return "", sHTML
    else:
        return sHTML, ""
        
def DrawField(xe, sXPath, oStep):
    sHTML = ""
    sNodeValue = (xe.text if xe.text else "")
    log("---- Value :" + sNodeValue, 4)
    
    sNodeLabel = xe.get("label", xe.tag)
    sLabelClasses = xe.get("label_class", "")
    sLabelStyle = xe.get("label_style", "")
    sNodeLabel = "<span class=\"" + sLabelClasses + "\" style=\"" + sLabelStyle + "\">" + sNodeLabel + ": </span>"

    sBreakBefore = xe.get("break_before", "")
    sBreakAfter = xe.get("break_after", "")
    sHRBefore = xe.get("hr_before", "")
    sHRAfter = xe.get("hr_after", "")
    sHelp = xe.get("help", "")
    sCSSClasses = xe.get("class", "")
    sStyle = xe.get("style", "")
    sInputType = xe.get("input_type", "")
    sRequired = xe.get("required", "")
    bRequired = uiCommon.IsTrue(sRequired)

    log("---- Input Type :" + sInputType, 4)
    log("---- Break Before/After : %s/%s" % (sBreakBefore, sBreakAfter), 4)
    log("---- HR Before/After : %s/%s" % (sHRBefore, sHRAfter), 4)
    log("---- Required : %s" % (str(bRequired)), 4)


    #some getting started layout possibilities
    if sBreakBefore == uiCommon.IsTrue(sBreakBefore):
        sHTML += "<br />"
    if sHRBefore == uiCommon.IsTrue(sHRBefore):
        sHTML += "<hr />"
    if sInputType == "textarea":
        #textareas have additional properties
        sRows = xe.get("rows", "2")
        sTextareaID = uiCommon.NewGUID()
        sHTML += sNodeLabel + " <textarea rows=\"" + sRows + "\"" + \
            CommonAttribsWithID(oStep, bRequired, sXPath, sTextareaID, sCSSClasses) + \
            " style=\"" + sStyle + "\"" \
            " help=\"" + sHelp + "\"" \
            ">" + sNodeValue + "</textarea>"
        #big box button
        sHTML += "<img class=\"big_box_btn pointer\" alt=\"\" src=\"static/images/icons/edit_16.png\" link_to=\"" + sTextareaID + "\" /><br />"
    elif sInputType == "dropdown":
        # the data source of a drop down can be a) an xml file, b) an internal function or web method or c) an "local" inline list
        # there is no "default" datasource... if nothing is available, it draws an empty picker
        sDatasource = xe.get("datasource", "")
        sDataSet = xe.get("dataset", "")
        sFieldStyle = xe.get("style", "")

        sHTML += sNodeLabel + " <select " + CommonAttribs(oStep, False, sXPath, sFieldStyle) + ">\n"
        
        # empty one
        sHTML += "<option " + SetOption("", sNodeValue) + " value=\"\"></option>\n"
        
        # if it's a combo, it's possible we may have a value that isn't actually in the list.
        # but we will need to add it to the list otherwise we can't select it!
        # so, first let's keep track of if we find the value anywhere in the various datasets.
        bValueWasInData = False
        
        if sDatasource == "":
            log("---- 'datasource' attribute not found, defaulting to 'local'.", 4)
        if sDatasource == "file":
            log("---- File datasource ... reading [" + sDataSet + "] ...", 4)
            try:
                # sDataset is a file name.
                # sFormat is the type of data
                # sTable is the parent node in the XML containing the data
                sFormat = xe.get("format", "")

                if sFormat == "":
                    log("---- 'format' attribute not found, defaulting to 'flat'.", 4)
            
                if sFormat.lower() == "xml":
                    sTable = xe.get("table", "")
                    sValueNode = xe.get("valuenode", "")
                    
                    if sTable == "":
                        log("---- 'table' attribute not found, defaulting to 'values'.", 4)
                    if sValueNode == "":
                        log("---- 'valuenode' attribute not found, defaulting to 'value'.", 4)
                    
                    xml = ET.parse("extensions/" + sDataSet)
                    if xml:
                        nodes = xml.findall(".//" + sValueNode)
                        if len(nodes) > 0:
                            log("---- Found data ... parsing ...", 4)
                            for node in nodes:
                                sHTML += "<option " + SetOption(node.text, sNodeValue) + " value=\"" + node.text + "\">" + node.text + "</option>\n"
                                if node.text == sNodeValue: bValueWasInData = True
                        else:
                            log("---- Dataset found but cannot find values in [" + sValueNode + "].", 4)
                    else:
                        log("---- Dataset file not found or unable to read.", 4)
                    
                else:
                    log("---- opening [" + sDataSet + "].", 4)
                    f = open("extensions/" + sDataSet, 'rb')
                    if not f:
                        log("ERROR: extensions/" + sDataSet + " not found", 0)

                    for line in f:
                        val = line.strip()
                        sHTML += "<option " + SetOption(val, sNodeValue) + " value=\"" + val + "\">" + val + "</option>\n"
                        if val == sNodeValue: bValueWasInData = True
                        
                    f.close()
            except Exception:
                uiGlobals.request.Messages.append(traceback.format_exc())
                return "Unable to render input element [" + sXPath + "]. Lookup file [" + sDataSet + "] not found or incorrect format."
        elif sDatasource == "function":
            log("---- Function datasource ... executing [" + sDataSet + "] ...", 4)
            # this executes a function to populate the drop down
            # at this time, the function must exist in this namespace
            # we expect the function to return a dictionary
            try:
                if sDataSet:
                    data = globals()[sDataSet]()
                    if data:
                        for key, val in data.iteritems():
                            sHTML += "<option " + SetOption(key, sNodeValue) + " value=\"" + key + "\">" + val + "</option>\n"
                            if key == sNodeValue: bValueWasInData = True
            except Exception:
                uiGlobals.request.Messages.append(traceback.format_exc())
        else: # default is "local"
            log("---- Inline datasource ... reading my own 'dataset' attribute ...", 4)
            # data is pipe delimited
            aValues = sDataSet.split('|')
            for sVal in aValues:
                sHTML += "<option " + SetOption(sVal, sNodeValue) + " value=\"" + sVal + "\">" + sVal + "</option>\n"

                if sVal == sNodeValue: bValueWasInData = True
        
        # NOTE: If it has the "combo" style and a value, that means we're allowing the user to enter a value that may not be 
        # in the dataset.  If that's the case, we must add the actual saved value to the list too. 
        if not bValueWasInData: # we didn't find it in the data ..
            if "combo" in sFieldStyle and sNodeValue:   # and it's a combo and not empty
                sHTML += "<option " + SetOption(sNodeValue, sNodeValue) + " value=\"" + sNodeValue + "\">" + sNodeValue + "</option>\n";            

        sHTML += "</select>"
    else: #input is the default
        sElementID = uiCommon.NewGUID() #some special cases below may need this.
        sHTML += sNodeLabel + " <input type=\"text\" " + \
            CommonAttribsWithID(oStep, bRequired, sXPath, sElementID, sCSSClasses) + \
            " style=\"" + sStyle + "\"" \
            " help=\"" + sHelp + "\"" \
            " value=\"" + sNodeValue + "\" />"
        #might this be a conn_name field?  If so, we can show the picker.
        sConnPicker = xe.get("connection_picker", "")
        if uiCommon.IsTrue(sConnPicker):
            sHTML += "<span class=\"ui-icon ui-icon-search forceinline conn_picker_btn pointer\" link_to=\"" + sElementID + "\"></span>"

    #some final layout possibilities
    if uiCommon.IsTrue(sBreakAfter):
        sHTML += "<br />"
    if uiCommon.IsTrue(sHRAfter):
        sHTML += "<hr />"

    log("---- ... done", 4)
    return sHTML

def CommonAttribsWithID(oStep, bRequired, sXPath, sElementID, sAdditionalClasses):
    # if it's embedded it will have a prefix
    sXPath = (oStep.XPathPrefix + "/" if oStep.XPathPrefix else "") + sXPath
    
    # requires a guid ID passed in - this one will be referenced client side
    return " id=\"" + sElementID + "\"" \
        " step_id=\"" + oStep.ID + "\"" \
        " function=\"" + oStep.FunctionName + "\"" \
        " xpath=\"" + sXPath + "\"" \
        " te_group=\"step_fields\"" \
        " class=\"step_input code " + sAdditionalClasses + "\"" + \
        (" is_required=\"true\"" if bRequired else "") + \
        " onchange=\"javascript:onStepFieldChange(this, '" + oStep.ID + "', '" + sXPath + "');\""

def CommonAttribs(oStep, bRequired, sXPath, sAdditionalClasses):
    # if it's embedded it will have a prefix
    sXPath = (oStep.XPathPrefix + "/" if oStep.XPathPrefix else "") + sXPath
    
    # creates a new id
    return " id=\"x" + uiCommon.NewGUID() + "\"" \
        " step_id=\"" + oStep.ID + "\"" \
        " function=\"" + oStep.FunctionName + "\"" \
        " xpath=\"" + sXPath + "\"" \
        " te_group=\"step_fields\"" \
        " class=\"step_input code " + sAdditionalClasses + "\"" + \
        (" is_required=\"true\"" if bRequired else "") + \
        " onchange=\"javascript:onStepFieldChange(this, '" + oStep.ID + "', '" + sXPath + "');\""

def DrawEmbeddedStep(oStep):
    uiCommon.log("** Embedded Step: [%s] prefix [%s]" % (oStep.FunctionName, oStep.XPathPrefix), 4)
    # JUST KNOW!
    # this isn't a "real" step ... meaning it isn't in the task_step table as an individual row
    # it's a step object we manually created.
    # so, some properties will have no values.
    sStepID = oStep.ID
    fn = oStep.Function
    
    # we need the full function, not just the inner part that's on the parent step xml.
    if fn is None:
        # the function doesn't exist (was probably deprecated)
        # we need at least a basic strip with a delete button
        sNoFunc = "<div class=\"embedded_step\">"
        sNoFunc += "    <div class=\"ui-state-default ui-state-highlight step_header\">"
        sNoFunc += "        <div class=\"step_header_title\"><img src=\"static/images/icons/status_unknown_16.png\" /></div>"
        sNoFunc += "        <div class=\"step_header_icons\">"
        sNoFunc += "            <span class=\"embedded_step_delete_btn\" remove_xpath=\"" + oStep.XPathPrefix + "\" parent_id=\"" + sStepID + "\"><img src=\"static/images/icons/fileclose.png\" alt=\"\" title=\"Remove Command\" /></span>"
        sNoFunc += "        </div>"
        sNoFunc += "    </div>"
        sNoFunc += "    <div class=\"ui-widget-content ui-state-highlight ui-corner-bottom step_detail\" >"
        sNoFunc += "Error building Step - Unable to get the details for the command type '" + oStep.FunctionName + "'.<br />"
        sNoFunc += "This command type may have been deprecated - check the latest Cato release notes.<br />"
        sNoFunc += "    </div>"
        sNoFunc += "</div>"

        return sNoFunc
    
    # invalid for embedded
    # sExpandedClass = ("step_collapsed" if oStep.UserSettings.Visible else "")

    sMainHTML = ""

    # labels are different here than in Full Steps.
    sIcon = ("" if not fn.Icon else fn.Icon)
    sLabel = "<img class=\"step_header_function_icon\" src=\"" + sIcon + "\" alt=\"\" /> " + \
        fn.Category.Label + " - " + fn.Label

    # invalid for embedded
    # sSnip = uiCommon.GetSnip(oStep.Description, 75)
    # sLabel += ("" if not oStep.Description) else "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[" + sSnip + "]")

    # sLockClause = (" onclick=\"return false;\"" if !oStep.Locked else "")


    #  step expand image
    #sExpandImage = "expand_down.png"
    #if sExpandedClass == "step_collapsed":
    #    sExpandImage = "expand_up.png"

    sMainHTML += "<div class=\"embedded_step\">"
    sMainHTML += "    <div class=\"ui-state-default step_header\">"
    sMainHTML += "        <div class=\"step_header_title\">"
#    sMainHTML += "            <span class=\"step_toggle_btn\"" \
#        " step_id=\"" + sStepID + "\">" \
#        " <img class=\"expand_image\" src=\"static/images/icons/" + sExpandImage + "\" alt=\"\" title=\"Hide/Show Step\" /></span>"
    sMainHTML += "            <span>" + sLabel + "</span>"
    sMainHTML += "        </div>"
    sMainHTML += "        <div class=\"step_header_icons\">"

    # this button will copy a step into the clipboard.
#    sMainHTML += "            <span><img id=\"step_copy_btn_" + sStepID + "\"" \
#        " class=\"step_copy_btn\" step_id=\"" + sStepID + "\"" \
#        " src=\"static/images/icons/editcopy_16.png\" alt=\"\" title=\"Copy this Step to your Clipboard\"/></span>"

    # for deleting, the codeblock_name is the step_id of the parent step.
    sMainHTML += "            <span class=\"embedded_step_delete_btn\"" \
        " remove_xpath=\"" + oStep.XPathPrefix + "\" parent_id=\"" + sStepID + "\">" \
        " <img src=\"static/images/icons/fileclose.png\" alt=\"\" title=\"Remove Command\" /></span>"
    sMainHTML += "        </div>"
    sMainHTML += "     </div>"
    sMainHTML += "     <div class=\"ui-widget-content ui-corner-bottom step_detail\" >"

    #!!! this returns a tuple with optional "options" and "variable" html
    sStepHTML, sOptionHTML, sVariableHTML = GetStepTemplate(oStep)
    sMainHTML += sStepHTML
    
    #comment steps don't have a common section - all others do
    if oStep.FunctionName != "comment":
        sMainHTML += DrawStepCommon(oStep, sOptionHTML, sVariableHTML, True)

    sMainHTML += "    </div>"
    sMainHTML += "</div>"

    return sMainHTML

def DrawStepCommon(oStep, sOptionHTML, sVariableHTML, bIsEmbedded = False):
    sStepID = oStep.ID

    # a certain combination of tests means we have nothing to draw at all
    if bIsEmbedded and not sOptionHTML and not sVariableHTML:
        return ""
    
    #this is the section that is common to all steps.
    sHTML = ""
    sHTML += "        <hr />"
    sHTML += "        <div class=\"step_common\" >"
    sHTML += "            <div class=\"step_common_header\">" # header div
    
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

    # embedded commands don't have a notes button (it's the description of the command, which doesn't apply)
    if not bIsEmbedded:
        sHTML += "                <span class=\"step_common_button " + ("step_common_button_active" if sShowOnLoad == "notes" else "") + "\"" \
            " id=\"btn_step_common_detail_" + sStepID + "_notes\"" \
            " button=\"notes\"" + " step_id=\"" + sStepID + "\">Notes</span>"

        # not showing help either... too cluttered
        sHTML += "                <span class=\"step_common_button " + ("step_common_button_active" if sShowOnLoad == "help" else "") + "\"" \
            " id=\"btn_step_common_detail_" + sStepID + "_help\"" \
            " button=\"help\"" \
            " step_id=\"" + sStepID + "\">Help</span>"
    
    
    sHTML += "            </div>" # end header div
    
    #sections
    # embedded commands don't have notes (it's the description of the command, which doesn't apply)
    if not bIsEmbedded:
        sHTML += "            <div id=\"step_common_detail_" + sStepID + "_notes\"" \
            " class=\"step_common_detail " + ("" if sShowOnLoad == "notes" else "step_common_collapsed") + "\"" \
            " style=\"height: 100px;\">"
#        sHTML += "                <textarea rows=\"4\" " + CommonAttribs(sStepID, "_common", False, "step_desc", "") + \
#            " help=\"Enter notes for this Command.\" reget_on_change=\"true\">" + oStep.Description + "</textarea>"
        sHTML += "            </div>"

        # embedded commands *could* show the help, but I don't like the look of it.
        # it's cluttered
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

def SetOption(s1, s2):
    return " selected=\"selected\"" if s1 == s2 else ""

def SetCheckRadio(s1, s2):
    return " checked=\"checked\"" if s1 == s2 else ""

# NOTE: the following functions are internal, but support dynamic dropdowns on step functions.
# the function name is referenced by the "dataset" value of a dropdown type of input, where the datasource="function"
# dropdowns expect a Dictionary<string,string> object return

def ddDataSource_GetDebugLevels():
    return {"0": "None", "1": "Minimal", "2": "Normal", "3": "Enhanced", "4": "Verbose", }

def ddDataSource_GetAWSClouds():
    data = {}
    
    # AWS regions
    p = providers.Provider.FromName("Amazon AWS")
    if p is not None:
        for c_name, c in p.Clouds.iteritems():
            data[c.Name] = c.Name
    # Eucalyptus clouds
    p = providers.Provider.FromName("Eucalyptus")
    if p is not None:
        for c_name, c in p.Clouds.iteritems():
            data[c.Name] = c.Name

    return data

def AddToCommandXML(sStepID, sXPath, sXMLToAdd):
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
        if not uiCommon.IsGUID(sStepID):
            uiGlobals.request.Messages.append("Unable to modify step. Invalid or missing Step ID. [" + sStepID + "].")

        # this select is only for logging
        sSQL = "select task_id, codeblock_name, function_name, step_order from task_step where step_id = '" + sStepID + "'"
        dr = uiGlobals.request.db.select_row_dict(sSQL)
        if uiGlobals.request.db.error:
            uiGlobals.request.Messages.append(uiGlobals.request.db.error)

        if dr is not None:
            AddNodeToXMLColumn("task_step", "function_xml", "step_id = '" + sStepID + "'", sXPath, sXMLToAdd)

            # log it
            uiCommon.WriteObjectChangeLog(uiGlobals.CatoObjectTypes.Task, dr["task_id"], dr["function_name"],
                "Added a new property to Command Type:" + dr["function_name"] + \
                " Codeblock:" + dr["codeblock_name"] + \
                " Step Order:" + str(dr["step_order"]))

        return
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())

def AddNodeToXMLColumn(sTable, sXMLColumn, sWhereClause, sXPath, sXMLToAdd):
    # BE WARNED! this function is shared by many things, and should not be enhanced
    # with sorting or other niceties.  If you need that stuff, build your own function.
    # AddRegistry:Node is a perfect example... we wanted sorting on the registries, and also we don't allow array.
    # but parameters for example are by definition arrays of parameter nodes.
    uiCommon.log("Adding node [%s] to [%s] in [%s.%s where %s]." % (sXMLToAdd, sXPath, sTable, sXMLColumn, sWhereClause), 4)
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
        sSQL = "select " + sXMLColumn + " from " + sTable + " where " + sWhereClause
        sXML = uiGlobals.request.db.select_col_noexcep(sSQL)
        if not sXML:
            uiGlobals.request.Messages.append("Unable to get xml." + uiGlobals.request.db.error)
        else:
            # parse the doc from the table
            uiCommon.log(sXML, 4)
            xd = ET.fromstring(sXML)
            if xd is None:
                uiGlobals.request.Messages.append("Error: Unable to parse XML.")

            # get the specified node from the doc, IF IT'S NOT THE ROOT
            # either a blank xpath, or a single word that matches the root, both match the root.
            # any other path DOES NOT require the root prefix.
            if sXPath == "":
                xNodeToEdit = xd
            elif xd.tag == sXPath:
                xNodeToEdit = xd
            else:
                xNodeToEdit = xd.find(sXPath)
            
            if xNodeToEdit is None:
                uiGlobals.request.Messages.append("Error: XML does not contain path [" + sXPath + "].")
                return

            # now parse the new section from the text passed in
            xNew = ET.fromstring(sXMLToAdd)
            if xNew is None:
                uiGlobals.request.Messages.append("Error: XML to be added cannot be parsed.")

            # if the node we are adding to has a text value, sadly it has to go.
            # we can't detect that, as the Value property shows the value of all children.
            # but this works, even if it seems backwards.
            # if the node does not have any children, then clear it.  that will safely clear any
            # text but not stomp the text of the children.
            if len(xNodeToEdit) == 0:
                xNodeToEdit.text = ""
            # add it to the doc
            xNodeToEdit.append(xNew)


            # then send the whole doc back to the database
            sSQL = "update " + sTable + " set " + sXMLColumn + " = '" + uiCommon.TickSlash(ET.tostring(xd)) + "'" \
                " where " + sWhereClause
            if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                uiGlobals.request.Messages.append("Unable to update XML Column [" + sXMLColumn + "] on [" + sTable + "]." + uiGlobals.request.db.error)

        return
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())

def SetNodeValueinCommandXML(sStepID, sNodeToSet, sValue):
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
        if not uiCommon.IsGUID(sStepID):
            uiGlobals.request.Messages.append("Unable to modify step. Invalid or missing Step ID. [" + sStepID + "] ")

        SetNodeValueinXMLColumn("task_step", "function_xml", "step_id = '" + sStepID + "'", sNodeToSet, sValue)

        return
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())

def SetNodeValueinXMLColumn(sTable, sXMLColumn, sWhereClause, sNodeToSet, sValue):
    uiCommon.log("Setting node [%s] to [%s] in [%s.%s where %s]." % (sNodeToSet, sValue, sTable, sXMLColumn, sWhereClause), 4)
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
        sSQL = "select " + sXMLColumn + " from " + sTable + " where " + sWhereClause
        sXML = uiGlobals.request.db.select_col_noexcep(sSQL)
        if not sXML:
            uiGlobals.request.Messages.append("Unable to get xml." + uiGlobals.request.db.error)
        else:
            # parse the doc from the table
            xd = ET.fromstring(sXML)
            if xd is None:
                uiGlobals.request.Messages.append("Error: Unable to parse XML.")

            # get the specified node from the doc, IF IT'S NOT THE ROOT
            if xd.tag == sNodeToSet:
                xNodeToSet = xd
            else:
                xNodeToSet = xd.find(sNodeToSet)

            if xNodeToSet is not None:
                xNodeToSet.text = sValue

                # then send the whole doc back to the database
                sSQL = "update " + sTable + " set " + sXMLColumn + " = '" + uiCommon.TickSlash(ET.tostring(xd)) + "' where " + sWhereClause
                if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                    uiGlobals.request.Messages.append("Unable to update XML Column [" + sXMLColumn + "] on [" + sTable + "]." + uiGlobals.request.db.error)
            else:
                uiGlobals.request.Messages.append("Unable to update XML Column ... [" + sNodeToSet + "] not found.")

        return
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())

def SetNodeAttributeinCommandXML(sStepID, sNodeToSet, sAttribute, sValue):
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
        if not uiCommon.IsGUID(sStepID):
            uiGlobals.request.Messages.append("Unable to modify step. Invalid or missing Step ID. [" + sStepID + "] ")

        SetNodeAttributeinXMLColumn("task_step", "function_xml", "step_id = '" + sStepID + "'", sNodeToSet, sAttribute, sValue)

        return
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())

def SetNodeAttributeinXMLColumn(sTable, sXMLColumn, sWhereClause, sNodeToSet, sAttribute, sValue):
    # THIS ONE WILL do adds if the attribute doesn't exist, or update it if it does.
    try:
        uiCommon.log("Setting [%s] attribute [%s] to [%s] in [%s.%s where %s]" % (sNodeToSet, sAttribute, sValue, sTable, sXMLColumn, sWhereClause), 4 )

        sXML = ""

        sSQL = "select " + sXMLColumn + " from " + sTable + " where " + sWhereClause
        sXML = uiGlobals.request.db.select_col_noexcep(sSQL)
        if uiGlobals.request.db.error:
            uiGlobals.request.Messages.append("Unable to get xml." + uiGlobals.request.db.error)
            return ""
 
        if sXML:
            # parse the doc from the table
            xd = ET.fromstring(sXML)
            if xd is None:
                uiGlobals.request.Messages.append("Unable to parse xml." + uiGlobals.request.db.error)
                return ""

            # get the specified node from the doc
            # here's the rub - the request might be or the "root" node,
            # which "find" will not, er ... find.
            # so let's first check if the root node is the name we want.
            xNodeToSet = None
            
            if xd.tag == sNodeToSet:
                xNodeToSet = xd
            else:
                xNodeToSet = xd.find(sNodeToSet)
            
            if xNodeToSet is None:
            # do nothing if we didn't find the node
                return ""
            else:
                # set it
                xNodeToSet.attrib[sAttribute] = sValue


            # then send the whole doc back to the database
            sSQL = "update " + sTable + " set " + sXMLColumn + " = '" + uiCommon.TickSlash(ET.tostring(xd)) + "'" \
                " where " + sWhereClause
            if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                uiGlobals.request.Messages.append("Unable to update XML Column [" + sXMLColumn + "] on [" + sTable + "]." + uiGlobals.request.db.error)

        return ""
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())

def RemoveFromCommandXML(sStepID, sNodeToRemove):
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
        if not uiCommon.IsGUID(sStepID):
            uiGlobals.request.Messages.append("Unable to modify step.<br />Invalid or missing Step ID. [" + sStepID + "]<br />")

        sSQL = "select task_id, codeblock_name, function_name, step_order from task_step where step_id = '" + sStepID + "'"
        dr = uiGlobals.request.db.select_row_dict(sSQL)
        if uiGlobals.request.db.error:
            uiGlobals.request.Messages.append(uiGlobals.request.db.error)

        if dr is not None:
            RemoveNodeFromXMLColumn("task_step", "function_xml", "step_id = '" + sStepID + "'", sNodeToRemove)

            # log it
            uiCommon.WriteObjectChangeLog(uiGlobals.CatoObjectTypes.Task, dr["task_id"], dr["function_name"],
                "Removed a property to Command Type:" + dr["function_name"] + \
                " Codeblock:" + dr["codeblock_name"] + \
                " Step Order:" + str(dr["step_order"]))

        return
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())

def RemoveNodeFromXMLColumn(sTable, sXMLColumn, sWhereClause, sNodeToRemove):
    uiCommon.log("Removing node [%s] from [%s.%s where %s]." % (sNodeToRemove, sTable, sXMLColumn, sWhereClause), 4)
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
        sSQL = "select " + sXMLColumn + " from " + sTable + " where " + sWhereClause
        sXML = uiGlobals.request.db.select_col_noexcep(sSQL)
        if not sXML:
            uiGlobals.request.Messages.append("Unable to get xml." + uiGlobals.request.db.error)
        else:
            # parse the doc from the table
            xd = ET.fromstring(sXML)
            if xd is None:
                uiGlobals.request.Messages.append("Error: Unable to parse XML.")

            # get the specified node from the doc
            xNodeToWhack = xd.find(sNodeToRemove)
            if xNodeToWhack is None:
                uiCommon.log("INFO: attempt to remove [%s] - the element was not found." % sNodeToRemove, 3)
                # no worries... what you want to delete doesn't exist?  perfect!
                return

            # OK, here's the deal...
            # we have found the node we want to delete, but we found it using an xpath,
            # ElementTree doesn't support deleting by xpath.
            # so, we'll use a parent map to find the immediate parent of the node we found,
            # and on the parent we can call ".remove"
            parent_map = dict((c, p) for p in xd.getiterator() for c in p)
            xParentOfNodeToWhack = parent_map[xNodeToWhack]
            
            # whack it
            if xParentOfNodeToWhack is not None:
                xParentOfNodeToWhack.remove(xNodeToWhack)

            sSQL = "update " + sTable + " set " + sXMLColumn + " = '" + uiCommon.TickSlash(ET.tostring(xd)) + "'" \
                " where " + sWhereClause
            if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                uiGlobals.request.Messages.append("Unable to update XML Column [" + sXMLColumn + "] on [" + sTable + "]." + uiGlobals.request.db.error)

        return
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())

def DrawDropZone(oStep, xEmbeddedFunction, sXPath, sLabel, bRequired):
    # drop zones are common for all the steps that can contain embedded steps.
    # they are a div to drop on and a hidden field to hold the embedded step id.
    sHTML = ""
    sHTML += sLabel

    # an embedded step may actually be the child of another embedded step, so
    # check for an xpath prefix
    sXPath = (oStep.XPathPrefix + "/" if oStep.XPathPrefix else "") + sXPath
    
    # some of our 'columns' may be complex XPaths.  XPaths have invalid characters for use in 
    # an HTML ID attribute
    # but we need it to be unique... so just 'clean up' the column name
    sXPathBasedID = sXPath.replace("[", "").replace("]", "").replace("/", "")

    # the dropzone
    sDropZone = "<div" + \
        (" is_required=\"true\" value=\"\"" if bRequired else "") + \
        " id=\"" + oStep.FunctionName + "_" + oStep.ID + "_" + sXPathBasedID + "_dropzone\"" \
        " xpath=\"" + sXPath + "\"" \
        " step_id=\"" + oStep.ID + "\"" \
        " class=\"step_nested_drop_target " + ("is_required" if bRequired else "") + "\">Click here to add a Command.</div>"
#        " datafield_id=\"" + sElementID + "\"" \


    # manually create a step object, which will basically only have the function_xml.
    if xEmbeddedFunction is not None:
        sFunctionName = xEmbeddedFunction.get("name", "")

        fn = uiCommon.GetTaskFunction(sFunctionName)

        # !!!!! This isn't a new step! ... It's an extension of the parent step.
        # but, since it's a different 'function', we'll treat it like a different step for now
        oEmbeddedStep = task.Step() # a new step object
        oEmbeddedStep.ID = oStep.ID 
        oEmbeddedStep.Function = fn # a function object
        oEmbeddedStep.FunctionName = sFunctionName
        oEmbeddedStep.FunctionXDoc = xEmbeddedFunction
        # THIS IS CRITICAL - this embedded step ... all fields in it will need an xpath prefix 
        oEmbeddedStep.XPathPrefix = sXPath + "/function"
        
        sHTML += DrawEmbeddedStep(oEmbeddedStep)
    else:
        sHTML += sDropZone 
       
    return sHTML

def DrawKeyValueSection(oStep, bShowPicker, bShowMaskOption, sKeyLabel, sValueLabel):
    sStepID = oStep.ID
    sFunction = oStep.FunctionName
    xd = oStep.FunctionXDoc

    sElementID = uiCommon.NewGUID()
    sValueFieldID = uiCommon.NewGUID()
    sHTML = ""

    sHTML += "<div id=\"" + sStepID + "_pairs\">"


    xPairs = xd.findall("pair")
    i = 1
    for xe in xPairs:
        sKey = xe.findtext("key")
        sVal = xe.findtext("value", "")
        sMask = xe.findtext("mask", "")

        sHTML += "<table border=\"0\" class=\"w99pct\" cellpadding=\"0\" cellspacing=\"0\"><tr>\n"
        sHTML += "<td class=\"w1pct\">&nbsp;" + sKeyLabel + ":&nbsp;</td>\n"

        sHTML += "<td class=\"w1pct\"><input type=\"text\" " + CommonAttribsWithID(oStep, True, "pair[" + str(i) + "]/key", sElementID, "") + \
            " validate_as=\"variable\"" \
            " value=\"" + uiCommon.SafeHTML(sKey) + "\"" \
            " help=\"Enter a name.\"" \
            " /></td>"

        if bShowPicker:
            sHTML += "<td class=\"w1pct\"><span class=\"ui-icon ui-icon-search forceinline key_picker_btn pointer\"" \
                " function=\"" + sFunction + "\"" \
                " target_field_id=\"" + sElementID + "\"" \
                " link_to=\"" + sElementID + "\"></span>\n"

            sHTML += "</td>\n"

        sHTML += "<td class=\"w1pct\">&nbsp;" + sValueLabel + ":&nbsp;</td>"

        #  we gotta get the field id first, but don't show the textarea until after
        sCommonAttribs = CommonAttribsWithID(oStep, True, "pair[" + str(i) + "]/value", sValueFieldID, "w90pct")

        sHTML += "<td class=\"w50pct\"><input type=\"text\" " + sCommonAttribs + \
            " value=\"" + uiCommon.SafeHTML(sVal) + "\"" \
            " help=\"Enter a value.\"" \
            " />\n"

        # big box button
        sHTML += "<span class=\"ui-icon ui-icon-pencil forceinline big_box_btn pointer\" link_to=\"" + sValueFieldID + "\"></span></td>\n"

        # optional mask option
        if bShowMaskOption:
            sHTML += "<td>"

            sHTML += "&nbsp;Mask?: <input type=\"checkbox\" " + \
                CommonAttribs(oStep, True, "pair[" + str(i) + "]/mask", "") + " " + SetCheckRadio("1", sMask) + " />\n"


            sHTML += "</td>\n"

        sHTML += "<td class=\"w1pct\" align=\"right\"><span class=\"ui-icon ui-icon-close forceinline fn_pair_remove_btn pointer\" index=\"" + str(i) + "\" step_id=\"" + sStepID + "\">"
        sHTML += "</span></td>"

        sHTML += "</tr></table>\n"

        i += 1

    sHTML += "<div class=\"fn_pair_add_btn pointer\"" \
        " add_to_id=\"" + sStepID + "_pairs\"" \
        " step_id=\"" + sStepID + "\">" \
        "<span class=\"ui-icon ui-icon-close forceinline\" title=\"Add another.\"></span>( click to add another )</div>"
    sHTML += "</div>"

    return sHTML

def RemoveStepVars(sStepID):
    RemoveFromCommandXML(sStepID, "variables")

def DrawVariableSectionForDisplay(oStep, bShowEditLink):
    sStepID = oStep.ID

    # we go check if there are vars first, so that way we don't waste space displaying nothing
    # if there are none
    # BUT only hide this empty section on the 'view' page.
    # if it's an edit page, we still show the empty table!

    sVariableHTML = GetVariablesForStepForDisplay(oStep)

    if not bShowEditLink and not sVariableHTML:
        return ""

    iParseType = oStep.OutputParseType
    iRowDelimiter = oStep.OutputRowDelimiter
    iColumnDelimiter = oStep.OutputColumnDelimiter
    uiCommon.log("Parse Type [%d], Row Delimiter [%d], Col Delimiter [%d]" % (iParseType, iRowDelimiter, iColumnDelimiter), 4)

    sHTML = ""
    if bShowEditLink:
        sHTML += "<span class=\"variable_popup_btn\" step_id=\"" + sStepID + "\">" \
            "<img src=\"static/images/icons/kedit_16.png\"" \
            " title=\"Manage Variables\" alt=\"\" /> Manage Variables</span>"

    # some types may only have one of the delimiters
    bRowDelimiterVisibility = (True if iParseType == 2 else False)
    bColDelimiterVisibility = (True if iParseType == 2 else False)

    if bRowDelimiterVisibility:
        sHTML += "<br />Row Break Indicator: " \
            " <span class=\"code 100px\">" + LabelNonprintable(iRowDelimiter) + "</span>"

    if bColDelimiterVisibility:
        sHTML += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Field Break Indicator: " \
            " <span class=\"code 100px\">" + LabelNonprintable(iColumnDelimiter) + "</span>"

    sHTML += sVariableHTML

    return sHTML

def GetVariablesForStepForDisplay(oStep):
    sStepID = oStep.ID
    xDoc = oStep.FunctionXDoc

    sHTML = ""
    if xDoc is not None:
        # uiCommon.log("Command Variable XML:\n%s" % ET.tostring(xDoc), 4)
        xVars = xDoc.findall("step_variables/variable")
        if xVars is None:
            return "Variable XML data for step [" + sStepID + "] does not contain any 'variable' elements."
        
        if len(xVars) > 0:
            uiCommon.log("-- Rendering [%d] variables ..." % len(xVars), 4)
            # build the HTML
            sHTML += "<table class=\"step_variables\" width=\"99%\" border=\"0\">\n"
            sHTML += "<tbody>"
            
            # loop
            for xVar in xVars:
                sName = uiCommon.SafeHTML(xVar.findtext("name", ""))
                sType = xVar.findtext("type", "").lower()
                
                uiCommon.log("---- Variable [%s] is type [%s]" % (sName, sType), 4)
                
                sHTML += "<tr>"
                sHTML += "<td class=\"row\"><span class=\"code\">" + sName + "</span></td>"
                
                if sType == "range":
                    sLProp = ""
                    sRProp = ""
                    # the markers can be a range indicator or a string.
                    if xVar.find("range_begin") is not None:
                        sLProp = " Position [" + xVar.findtext("range_begin", "") + "]"
                    elif xVar.find("prefix") is not None:
                        sLProp = " Prefix [" + xVar.findtext("prefix", "") + "]"
                    else:
                        return "Variable XML data for step [" + sStepID + "] does not contain a valid begin marker."

                    if xVar.find("range_end") is not None:
                        sRProp = " Position [" + xVar.findtext("range_end", "") + "]"
                    elif xVar.find("suffix") is not None:
                        sRProp = " Suffix [" + xVar.findtext("suffix", "") + "]"
                    else:
                        return "Variable XML data for step [" + sStepID + "] does not contain a valid end marker."

                    sHTML += "<td class=\"row\">Characters in Range:</td><td class=\"row\"><span class=\"code\">" + uiCommon.SafeHTML(sLProp) + " - " + uiCommon.SafeHTML(sRProp) + "</span></td>"
                elif sType == "delimited":
                    sHTML += "<td class=\"row\">Value at Index Position:</td><td class=\"row\"><span class=\"code\">" + uiCommon.SafeHTML(xVar.findtext("position", "")) + "</span></td>"
                elif sType == "regex":
                    sHTML += "<td class=\"row\">Regular Expression:</td><td class=\"row\"><span class=\"code\">" + uiCommon.SafeHTML(xVar.findtext("regex", "")) + "</span></td>"
                elif sType == "xpath":
                    sHTML += "<td class=\"row\">Xpath:</td><td class=\"row\"><span class=\"code\">" + uiCommon.SafeHTML(xVar.findtext("xpath", "")) + "</span></td>"
                else:
                    sHTML += "INVALID TYPE"
                
                sHTML += "</tr>"
                 
            # close it out
            sHTML += "</tbody></table>\n"
        return sHTML
    else:
        # yes this is valid. "null" in the database may translate to having no xml.  That's ok.
        return ""

def DrawVariableSectionForEdit(oStep):
    sHTML = ""
    # sStepID = drStep["step_id"]
    # sFunction = drStep["function_name"]
    sParseType = oStep.OutputParseType
    iRowDelimiter = oStep.OutputRowDelimiter
    iColumnDelimiter = oStep.OutputColumnDelimiter

    # now, some sections or items may or may not be available.
    sDelimiterSectionVisiblity = ""
    # only 'parsed' types show delimiter pickers.  The hardcoded "delimited" (1) 
    # type does not allow changes to the delimiter.
    sRowDelimiterVisibility = ("" if sParseType == 2 else "hidden")
    sColDelimiterVisibility = ("" if sParseType == 2 else "hidden")

    # some code here will replace non-printable delimiters with a token string
    sRowDelimiterLabel = LabelNonprintable(iRowDelimiter)
    sColumnDelimiterLabel = LabelNonprintable(iColumnDelimiter)

    sHTML += "<div class=\"" + sDelimiterSectionVisiblity + "\" id=\"div_delimiters\">"
    sHTML += "<span id=\"row_delimiter\" class=\"" + sRowDelimiterVisibility + "\">"
    sHTML += "Row Break Indicator: " \
        " <span id=\"output_row_delimiter_label\"" \
        " class=\"delimiter_label code\">" + sRowDelimiterLabel + "</span>"
    sHTML += "<img class=\"pointer\" src=\"static/images/icons/search.png\" alt=\"\" title=\"Select a Delimiter\" name=\"delimiter_picker_btn\" target=\"row\" />"
    sHTML += "<img class=\"pointer\" src=\"static/images/icons/fileclose.png\" alt=\"\" title=\"Clear this Delimiter\" name=\"delimiter_clear_btn\" target=\"row\" style=\"width:12px;height:12px;\" />"; sHTML += "</span>"

    sHTML += "<span id=\"col_delimiter\" class=\"" + sColDelimiterVisibility + "\">"
    sHTML += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Field Break Indicator: " \
        " <span id=\"output_col_delimiter_label\"" \
        " class=\"delimiter_label code\">" + sColumnDelimiterLabel + "</span>"
    sHTML += "<img class=\"pointer\" src=\"static/images/icons/search.png\" alt=\"\" title=\"Select a Delimiter\" name=\"delimiter_picker_btn\" target=\"col\" />"
    sHTML += "<img class=\"pointer\" src=\"static/images/icons/fileclose.png\" alt=\"\" title=\"Clear this Delimiter\" name=\"delimiter_clear_btn\" target=\"col\" style=\"width:12px;height:12px;\" />"; sHTML += "</span>"
    sHTML += "</span>"
    sHTML += "</div>"

    sHTML += "</div>"
    # END DELIMITER SECTION


    sHTML += "<div id=\"div_variables\">"
    sHTML += "<div><span id=\"variable_add_btn\">" \
        "<img src=\"static/images/icons/bookmark_add_32.png\" width=\"16\" height=\"16\"" \
        " alt=\"Add Variable\" title=\"Add Variable\"/> Add a Variable</span><span id=\"variable_clearall_btn\">" \
        "<img src=\"static/images/icons/bookmark_delete_32.png\" width=\"16\" height=\"16\"" \
        " alt=\"Clear All Variables\" title=\"Clear All Variables\"/> Clear All Variables</span></div><hr />"
    sHTML += GetVariablesForStepForEdit(oStep)
    sHTML += "</div>"

    return sHTML

def GetVariablesForStepForEdit(oStep):
    sStepID = oStep.ID

    sHTML = ""
    
    # build the HTML
    sHTML += "<ul id=\"edit_variables\" class=\"variables\">"
    
    # if the xml is empty, we still need to return the UL so the gui will work.
    xDoc = oStep.FunctionXDoc
    if xDoc is None:
        return sHTML + "</ul>\n"

    # if the document is missing the root node, we still need to return the UL.
    xVars = xDoc.findall("step_variables/variable")
    if xVars is None:
        return sHTML + "</ul>\n"
    
    if len(xVars) > 0:
        # loop
        for xVar in xVars:
            sName = xVar.findtext("name", "")
            sType = xVar.findtext("type", "").lower()
            sVarStrip = sName
            sDetailStrip = ""
            sLProp = ""
            sRProp = ""
            sLIdxChecked = ""
            sRIdxChecked = ""
            sLPosChecked = ""
            sRPosChecked = ""
            sVarGUID = "v" + uiCommon.NewGUID()
            
            if sType == "range":
                # the markers can be a range indicator or a string.
                if xVar.findtext("range_begin") is not None:
                    sLProp = uiCommon.SafeHTML(xVar.findtext("range_begin", ""))
                    sLIdxChecked = " checked=\"checked\""
                elif xVar.findtext("prefix") is not None:
                    sLProp = uiCommon.SafeHTML(xVar.findtext("prefix", ""))
                    sLPosChecked = " checked=\"checked\""
                else:
                    return "Variable XML data for step [" + sStepID + "] does not contain a valid begin marker."
                if xVar.findtext("range_end") is not None:
                    sRProp = uiCommon.SafeHTML(xVar.findtext("range_end", ""))
                    sRIdxChecked = " checked=\"checked\""
                elif xVar.findtext("suffix") is not None:
                    sRProp = uiCommon.SafeHTML(xVar.findtext("suffix", ""))
                    sRPosChecked = " checked=\"checked\""
                else:
                    return "Variable XML data for step [" + sStepID + "] does not contain a valid end marker."
                sVarStrip = "Variable: " \
                    " <input type=\"text\" class=\"var_name code var_unique\" id=\"" + sVarGUID + "_name\"" \
                        " validate_as=\"variable\"" \
                        " value=\"" + sName + "\" />"
                sDetailStrip = " will contain the output found between <br />" \
                    "<input type=\"radio\" name=\"" + sVarGUID + "_l_mode\" value=\"index\" " + sLIdxChecked + " class=\"prop\" refid=\"" + sVarGUID + "\" />" \
                        " position / " \
                        " <input type=\"radio\" name=\"" + sVarGUID + "_l_mode\" value=\"string\" " + sLPosChecked + " class=\"prop\" refid=\"" + sVarGUID + "\" />" \
                        " prefix " \
                        " <input type=\"text\" class=\"w100px code prop\" id=\"" + sVarGUID + "_l_prop\"" \
                        " value=\"" + sLProp + "\" refid=\"" + sVarGUID + "\" />" \
                        " and " \
                        "<input type=\"radio\" name=\"" + sVarGUID + "_r_mode\" value=\"index\" " + sRIdxChecked + " class=\"prop\" refid=\"" + sVarGUID + "\" />" \
                        " position / " \
                        " <input type=\"radio\" name=\"" + sVarGUID + "_r_mode\" value=\"string\" " + sRPosChecked + " class=\"prop\" refid=\"" + sVarGUID + "\" />" \
                        " suffix " \
                        " <input type=\"text\" class=\"w100px code prop\" id=\"" + sVarGUID + "_r_prop\"" \
                        " value=\"" + sRProp + "\" refid=\"" + sVarGUID + "\" />."
                
            elif sType == "delimited":
                sLProp = xVar.findtext("position", "")
                sVarStrip = "Variable: " \
                    " <input type=\"text\" class=\"var_name code var_unique\" id=\"" + sVarGUID + "_name\"" \
                        " validate_as=\"variable\"" \
                        " value=\"" + sName + "\" />"
                sDetailStrip += "" \
                    " will contain the data from column position" \
                        " <input type=\"text\" class=\"w100px code\" id=\"" + sVarGUID + "_l_prop\"" \
                        " value=\"" + sLProp + "\" validate_as=\"posint\" />."
                
            elif sType == "regex":
                sLProp = uiCommon.SafeHTML(xVar.findtext("regex", ""))
                sVarStrip = "Variable: " \
                    " <input type=\"text\" class=\"var_name code var_unique\" id=\"" + sVarGUID + "_name\"" \
                        " validate_as=\"variable\"" \
                        " value=\"" + sName + "\" />"
                sDetailStrip += "" \
                    " will contain the result of the following regular expression: " \
                        " <br /><input type=\"text\" class=\"w98pct code\"" \
                        " id=\"" + sVarGUID + "_l_prop\"" \
                        " value=\"" + sLProp + "\" />."
            elif sType == "xpath":
                sLProp = uiCommon.SafeHTML(xVar.findtext("xpath", ""))
                sVarStrip = "Variable: " \
                    " <input type=\"text\" class=\"var_name code var_unique\" id=\"" + sVarGUID + "_name\"" \
                        " validate_as=\"variable\"" \
                        " value=\"" + sName + "\" />"
                sDetailStrip += "" \
                    " will contain the Xpath: " \
                        " <br /><input type=\"text\" class=\"w98pct code\"" \
                        " id=\"" + sVarGUID + "_l_prop\"" \
                        " value=\"" + sLProp + "\" />."
            else:
                sHTML += "INVALID TYPE"
            
            
            sHTML += "<li id=\"" + sVarGUID + "\" class=\"variable\" var_type=\"" + sType + "\">"
            sHTML += "<span class=\"variable_name\">" + sVarStrip + "</span>"
            sHTML += "<span class=\"variable_delete_btn\" remove_id=\"" + sVarGUID + "\">" \
                " <img src=\"static/images/icons/fileclose.png\"" \
                    "  alt=\"Delete Variable\" title=\"Delete Variable\" /></span>"
            sHTML += "<span class=\"variable_detail\">" + sDetailStrip + "</span>"
            # an error message placeholder
            sHTML += "<br /><span id=\"" + sVarGUID + "_msg\" class=\"var_error_msg\"></span>"
            
            sHTML += "</li>\n"
            

    sHTML += "</ul>\n"

    return sHTML

def LabelNonprintable(iVal):
    if iVal == 0:
        return "N/A"
    elif iVal == 9:
        return "TAB"
    elif iVal == 10:
        return "LF"
    elif iVal == 12:
        return "FF"
    elif iVal == 13:
        return "CR"
    elif iVal == 27:
        return "ESC"
    elif iVal == 32:
        return "SP"
    else:
        return "&#" + str(iVal) + ";"

    

"""
From here to the bottom are the hardcoded commands.
"""

def GetEcosystemObjects(oStep):
    """
        This one could easily be moved out of hardcode and into the commands.xml using a function based lookup.
    """
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
            
        xd = oStep.FunctionXDoc

        sObjectType = xd.findtext("object_type", "")
        sHTML = ""

        sHTML += "Select Object Type:\n"
        sHTML += "<select " + CommonAttribs(oStep, True, "object_type", "") + ">\n"
        sHTML += "  <option " + SetOption("", sObjectType) + " value=\"\"></option>\n"

        
        cp = providers.CloudProviders()
        if cp is not None:
            for p_name, p in cp.iteritems():
                cots = p.GetAllObjectTypes()
                for cot_name, cot in cots.iteritems():
                    sHTML += "<option " + SetOption(cot.ID, sObjectType) + " value=\"" + cot.ID + "\">" + p.Name + " - " + cot.Label + "</option>\n";            
        
        sHTML += "</select>\n"

        sCloudFilter = xd.findtext("cloud_filter", "")
        sHTML += "Cloud Filter: \n" + "<input type=\"text\" " + \
        CommonAttribs(oStep, False, "cloud_filter", "") + \
        " help=\"Enter all or part of a cloud name to filter the results.\" value=\"" + sCloudFilter + "\" />\n"

        sResultName = xd.findtext("result_name", "")
        sHTML += "<br />Result Variable: \n" + "<input type=\"text\" " + \
        CommonAttribs(oStep, False, "result_name", "") + \
        " help=\"This variable array will contain the ID of each Ecosystem Object.\" value=\"" + sResultName + "\" />\n"

        sCloudName = xd.findtext("cloud_name", "")
        sHTML += " Cloud Name Variable: \n" + "<input type=\"text\" " + \
        CommonAttribs(oStep, False, "cloud_name", "") + \
        " help=\"This variable array will contain the name of the Cloud for each Ecosystem Object.\" value=\"" + sCloudName + "\" />\n"

        return sHTML
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())
        return "Unable to draw Step - see log for details."

def SqlExec(oStep):
    """
        This should return a tuple, the html and a flag of whether or not to draw the variable button
    """
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
            
        sStepID = oStep.ID
        xd = oStep.FunctionXDoc

        """TAKE NOTE:
        * 
        * Similar to the windows command...
        * ... we are updating a record here when we GET the data.
        * 
        * Why?  Because this command has modes.
        * The data has different meaning depending on the 'mode'.
        * 
        * So, on the client if the user changes the 'mode', the new command may not need all the fields
        * that the previous selection needed.
        * 
        * So, we just wipe any unused fields based on the current mode.
        * """
        sCommand = xd.findtext("sql", "")
        sConnName = xd.findtext("conn_name", "")
        sMode = xd.findtext("mode", "")
        sHandle = xd.findtext("handle", "")

        sHTML = ""
        sElementID = uiCommon.NewGUID()
        sFieldID = uiCommon.NewGUID()
        bDrawVarButton = False
        bDrawSQLBox = False
        bDrawHandle = False
        bDrawKeyValSection = False

        sHTML += "Connection:\n"
        sHTML += "<input type=\"text\" " + CommonAttribsWithID(oStep, True, "conn_name", sElementID, "")
        sHTML += " help=\"Enter an active connection where this SQL will be executed.\" value=\"" + sConnName + "\" />"
        sHTML += "<span class=\"ui-icon ui-icon-search forceinline conn_picker_btn pointer\" link_to=\"" + sElementID + "\"></span>\n"

        sHTML += "Mode:\n"
        sHTML += "<select " + CommonAttribs(oStep, True, "mode", "") + " reget_on_change=\"true\">\n"
        sHTML += "  <option " + SetOption("SQL", sMode) + " value=\"SQL\">SQL</option>\n"
        sHTML += "  <option " + SetOption("BEGIN", sMode) + " value=\"BEGIN\">BEGIN</option>\n"
        sHTML += "  <option " + SetOption("COMMIT", sMode) + " value=\"COMMIT\">COMMIT</option>\n"
        # sHTML += "  <option " + SetOption("COMMIT / BEGIN", sMode) + " value=\"COMMIT / BEGIN\">COMMIT / BEGIN</option>\n"
        sHTML += "  <option " + SetOption("ROLLBACK", sMode) + " value=\"ROLLBACK\">ROLLBACK</option>\n"
        sHTML += "  <option " + SetOption("EXEC", sMode) + " value=\"EXEC\">EXEC</option>\n"
        sHTML += "  <option " + SetOption("PL/SQL", sMode) + " value=\"PL/SQL\">PL/SQL</option>\n"
        sHTML += "  <option " + SetOption("PREPARE", sMode) + " value=\"PREPARE\">PREPARE</option>\n"
        sHTML += "  <option " + SetOption("RUN", sMode) + " value=\"RUN\">RUN</option>\n"
        sHTML += "</select>\n"


        # here we go!
        # certain modes show different fields.

        if sMode == "BEGIN" or sMode == "COMMIT" or sMode == "ROLLBACK":
            # these modes have no SQL or pairs or variables
            SetNodeValueinCommandXML(sStepID, "sql", "")
            SetNodeValueinCommandXML(sStepID, "handle", "")
            RemoveFromCommandXML(sStepID, "pair")
            RemoveStepVars(sStepID)
        elif sMode == "PREPARE":
            bDrawSQLBox = True
            bDrawHandle = True

            # this mode has no pairs or variables
            RemoveFromCommandXML(sStepID, "pair")
            RemoveStepVars(sStepID)
        elif sMode == "RUN":
            bDrawVarButton = True
            bDrawHandle = True
            bDrawKeyValSection = True

            # this mode has no SQL
            SetNodeValueinCommandXML(sStepID, "sql", "")
        else:
            bDrawVarButton = True
            bDrawSQLBox = True

            SetNodeValueinCommandXML(sStepID, "handle", "")
            # the default mode has no pairs
            RemoveFromCommandXML(sStepID, "pair")

        if bDrawHandle:
            sHTML += "Handle:\n"
            sHTML += "<input type=\"text\" " + CommonAttribs(oStep, True, "handle", "")
            sHTML += " help=\"Enter a handle for this prepared statement.\" value=\"" + sHandle + "\" />"

        if bDrawKeyValSection:
            sHTML += DrawKeyValueSection(oStep, False, False, "Bind", "Value")

        if bDrawSQLBox:
            #  we gotta get the field id first, but don't show the textarea until after
            sCommonAttribsForTA = CommonAttribsWithID(oStep, True, "sql", sFieldID, "")

            sHTML += "<br />SQL:\n"
            # big box button
            sHTML += "<img class=\"big_box_btn pointer\" alt=\"\"" \
                " src=\"static/images/icons/edit_16.png\"" \
                " link_to=\"" + sFieldID + "\" /><br />\n"

            sHTML += "<textarea " + sCommonAttribsForTA + " help=\"Enter a SQL query or procedure.\">" + sCommand + "</textarea>"
        return sHTML, bDrawVarButton
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())
        return "Unable to draw Step - see log for details."

def RunTask(oStep):
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
            
        sStepID = oStep.ID
        xd = oStep.FunctionXDoc
    
        sActualTaskID = ""
        # sOnSuccess = ""
        # sOnError = ""
        sAssetID = ""
        sAssetName = ""
        sLabel = ""
        sHTML = ""
        sParameterXML = ""
        
        sOriginalTaskID = xd.findtext("original_task_id", "")
        sVersion = xd.findtext("version")
        sHandle = xd.findtext("handle", "")
        sTime = xd.findtext("time_to_wait", "")
        sAssetID = xd.findtext("asset_id", "")
    
        # xSuccess = xd.find("# on_success")
        # if xSuccess is None) return "Error: XML does not contain on_success:
        # sOnSuccess = xSuccess.findtext(value, "")
    
        # xError = xd.find("# on_error")
        # if xError is None) return "Error: XML does not contain on_error:
        # sOnError = xError.findtext(value, "")
    
        # get the name and code for belonging to this otid and version
        if uiCommon.IsGUID(sOriginalTaskID):
            sSQL = "select task_id, task_code, task_name, parameter_xml from task" \
                " where original_task_id = '" + sOriginalTaskID + "'" + \
                (" and default_version = 1" if not sVersion else " and version = '" + sVersion + "'")
    
            dr = uiGlobals.request.db.select_row_dict(sSQL)
            if uiGlobals.request.db.error:
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
                return "Error retrieving target Task.(1)" + uiGlobals.request.db.error
    
            if dr is not None:
                sLabel = dr["task_code"] + " : " + dr["task_name"]
                sActualTaskID = dr["task_id"]
                sParameterXML = (dr["parameter_xml"] if dr["parameter_xml"] else "")
            else:
                # It's possible that the user changed the task from the picker but had 
                # selected a version, which is still there now but may not apply to the new task.
                # so, if the above SQL failed, try: again by resetting the version box to the default.
                sSQL = "select task_id, task_code, task_name, parameter_xml from task" \
                    " where original_task_id = '" + sOriginalTaskID + "'" \
                    " and default_version = 1"
    
                dr = uiGlobals.request.db.select_row_dict(sSQL)
                if uiGlobals.request.db.error:
                    uiGlobals.request.Messages.append(uiGlobals.request.db.error)
                    return "Error retrieving target Task.(2)<br />" + uiGlobals.request.db.error
    
                if dr is not None:
                    sLabel = dr["task_code"] + " : " + dr["task_name"]
                    sActualTaskID = dr["task_id"]
                    sParameterXML = (dr["parameter_xml"] if dr["parameter_xml"] else "")
    
                    # oh yeah, and set the version field to null since it was wrong.
                    SetNodeValueinCommandXML(sStepID, "//version", "")
                else:
                    # a default doesnt event exist, really fail...
                    return "Unable to find task [" + sOriginalTaskID + "] version [" + sVersion + "]." + uiGlobals.request.db.error
    
    
        # IF IT's A GUID...
        #  get the asset name belonging to this asset_id
        #  OTHERWISE
        #  make the sAssetName value be what's in sAssetID (a literal value in [[variable]] format)
        if uiCommon.IsGUID(sAssetID):
            sSQL = "select asset_name from asset where asset_id = '" + sAssetID + "'"
    
            sAssetName = uiGlobals.request.db.select_col_noexcep(sSQL)
            if uiGlobals.request.db.error:
                return "Error retrieving Run Task Asset Name." + uiGlobals.request.db.error
    
            if sAssetName == "":
                return "Unable to find Asset by ID - [" + sAssetID + "]." + uiGlobals.request.db.error
        else:
            sAssetName = sAssetID
    
    
    
    
        # all good, draw the widget
        sOTIDField = uiCommon.NewGUID()
    
        sHTML += "<input type=\"text\" " + \
            CommonAttribsWithID(oStep, True, "original_task_id", sOTIDField, "hidden") + \
            " value=\"" + sOriginalTaskID + "\"" + " reget_on_change=\"true\" />"
    
        sHTML += "Task: \n"
        sHTML += "<input type=\"text\"" \
            " onkeydown=\"return false;\"" \
            " onkeypress=\"return false;\"" \
            " is_required=\"true\"" \
            " step_id=\"" + sStepID + "\"" \
            " class=\"code w75pct\"" \
            " id=\"fn_run_task_taskname_" + sStepID + "\"" \
            " value=\"" + sLabel + "\" />\n"
        sHTML += "<span class=\"ui-icon ui-icon-search forceinline task_picker_btn pointer\" title=\"Pick Task\"" \
            " target_field_id=\"" + sOTIDField + "\"" \
            " step_id=\"" + sStepID + "\"></span>\n"
        if sActualTaskID != "":
            sHTML += "<span class=\"ui-icon ui-icon-pencil forceinline task_open_btn pointer\" title=\"Edit Task\"" \
                " task_id=\"" + sActualTaskID + "\"></span>\n"
            sHTML += "<span class=\"ui-icon ui-icon-print forceinline task_print_btn pointer\" title=\"View Task\"" \
                " task_id=\"" + sActualTaskID + "\"></span>\n"
    
        # versions
        if uiCommon.IsGUID(sOriginalTaskID):
            sHTML += "<br />"
            sHTML += "Version: \n"
            sHTML += "<select " + CommonAttribs(oStep, False, "version", "") + " reget_on_change=\"true\">\n"
            # default
            sHTML += "<option " + SetOption("", sVersion) + " value=\"\">Default</option>\n"
    
            sSQL = "select version from task" \
                " where original_task_id = '" + sOriginalTaskID + "'" \
                " order by version"
            dt = uiGlobals.request.db.select_all_dict(sSQL)
            if uiGlobals.request.db.error:
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
                return "Database Error:" + uiGlobals.request.db.error
    
            if dt:
                for dr in dt:
                    sHTML += "<option " + SetOption(str(dr["version"]), sVersion) + " value=\"" + str(dr["version"]) + "\">" + str(dr["version"]) + "</option>\n"
            else:
                return "Unable to continue - Cannot find Version for Task [" + sOriginalTaskID + "]."
    
            sHTML += "</select></span>\n"
    
    
    
        sHTML += "<br />"

        #  asset
        sHTML += "<input type=\"text\" " + \
            CommonAttribsWithID(oStep, False, "asset_id", sOTIDField, "hidden") + \
            " value=\"" + sAssetID + "\" />"
    
        sHTML += "Asset: \n"
        sHTML += "<input type=\"text\"" \
            " help=\"Select an Asset or enter a variable.\"" + \
            ("" if uiCommon.IsGUID(sAssetID) else " syntax=\"variable\"") + \
            " step_id=\"" + sStepID + "\"" \
            " class=\"code w75pct\"" \
            " id=\"fn_run_task_assetname_" + sStepID + "\"" + \
            (" disabled=\"disabled\"" if uiCommon.IsGUID(sAssetID) else "") + \
            " onchange=\"javascript:pushStepFieldChangeVia(this, '" + sOTIDField + "');\"" \
            " value=\"" + sAssetName + "\" />\n"
    
        sHTML += "<span class=\"ui-icon ui-icon-close forceinline fn_field_clear_btn pointer\" clear_id=\"fn_run_task_assetname_" + sStepID + "\"" \
            " title=\"Clear\"></span>"
    
        sHTML += "<span class=\"ui-icon ui-icon-search forceinline asset_picker_btn pointer\" title=\"Select\"" \
            " link_to=\"" + sOTIDField + "\"" \
            " target_field_id=\"fn_run_task_assetname_" + sStepID + "\"" \
            " step_id=\"" + sStepID + "\"></span>\n"
    
        sHTML += "<br />"
        sHTML += "Task Handle: <input type=\"text\" " + CommonAttribs(oStep, True, "handle", "") + \
            " value=\"" + sHandle + "\" />\n"
    
        sHTML += "Time to Wait: <input type=\"text\" " + CommonAttribs(oStep, False, "time_to_wait", "") + \
            " value=\"" + sTime + "\" />\n"
    
        # sHTML += "<br />"
        # sHTML += "The following Command will be executed on Success:<br />\n"
        # # enable the dropzone for the Success action
        # sHTML += DrawDropZone(sStepID, sOnSuccess, sFunction, "on_success", "", False)
    
        # sHTML += "The following Command will be executed on Error:<br />\n"
        # # enable the dropzone for the Error action
        # sHTML += DrawDropZone(sStepID, sOnError, sFunction, "on_error", "", False)
        
        
        # edit parameters link - not available unless a task is selected
        if sActualTaskID:
            # this is cheating but it's faster than parsing xml
            # count the occurences of "</parameter>" in the parameter_xml
            x = sParameterXML.count("</parameter>")
            r = sParameterXML.count("required=\"true\"")
            if x:
                icon = ("alert" if r else "pencil")
                sHTML += "<hr />"
                sHTML += "<div class=\"fn_runtask_edit_parameters_btn pointer\"" \
                    " task_id=\"" + sActualTaskID + "\"" \
                    " step_id=\"" + sStepID + "\">" \
                    "<span class=\"ui-icon ui-icon-%s forceinline \"></span> Edit Parameters (%s)</div>" % (icon, str(x))
        
        return sHTML
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())
        return "Unable to draw Step - see log for details."

def Subtask(oStep):
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
            
        sStepID = oStep.ID
        xd = oStep.FunctionXDoc
    
        sActualTaskID = ""
        sLabel = ""
        sHTML = ""
    
        sOriginalTaskID = xd.findtext("original_task_id", "")
        sVersion = xd.findtext("version", "")
    
        # get the name and code for belonging to this otid and version
        if uiCommon.IsGUID(sOriginalTaskID):
            sSQL = "select task_id, task_code, task_name from task" \
                " where original_task_id = '" + sOriginalTaskID + "'" + \
                (" and default_version = 1" if not sVersion else " and version = '" + sVersion + "'")
    
            dr = uiGlobals.request.db.select_row_dict(sSQL)
            if uiGlobals.request.db.error:
                uiGlobals.request.Messages.append("Error retrieving subtask.(1)<br />" + uiGlobals.request.db.error)
                return "Error retrieving subtask.(1)<br />" + uiGlobals.request.db.error

            if dr is not None:
                sLabel = dr["task_code"] + " : " + dr["task_name"]
                sActualTaskID = dr["task_id"]
            else:
                # It's possible that the user changed the task from the picker but had 
                # selected a version, which is still there now but may not apply to the new task.
                # so, if the above SQL failed, try: again by resetting the version box to the default.
                sSQL = "select task_id, task_code, task_name from task" \
                    " where original_task_id = '" + sOriginalTaskID + "'" \
                    " and default_version = 1"
    
                dr = uiGlobals.request.db.select_row_dict(sSQL)
                if uiGlobals.request.db.error:
                    uiGlobals.request.Messages.append("Error retrieving subtask.(2)<br />" + uiGlobals.request.db.error)
                    return "Error retrieving subtask.(2)<br />" + uiGlobals.request.db.error
    
                if dr is not None:
                    sLabel = dr["task_code"] + " : " + dr["task_name"]
                    sActualTaskID = dr["task_id"]
    
                    # oh yeah, and set the version field to null since it was wrong.
                    SetNodeValueinCommandXML(sStepID, "version", "")
                else:
                    # a default doesnt event exist, really fail...
                    uiGlobals.request.Messages.append("Unable to find task [" + sOriginalTaskID + "] version [" + sVersion + "].")
                    return "Unable to find task [" + sOriginalTaskID + "] version [" + sVersion + "]."
    
        # all good, draw the widget
        sOTIDField = uiCommon.NewGUID()
    
        sHTML += "<input type=\"text\" " + \
            CommonAttribsWithID(oStep, True, "original_task_id", sOTIDField, "hidden") + \
            " value=\"" + sOriginalTaskID + "\" reget_on_change=\"true\" />\n"
    
        sHTML += "Task: \n"
        sHTML += "<input type=\"text\"" \
            " onkeydown=\"return false;\"" \
            " onkeypress=\"return false;\"" \
            " is_required=\"true\"" \
            " step_id=\"" + sStepID + "\"" \
            " class=\"code w75pct\"" \
            " id=\"fn_subtask_taskname_" + sStepID + "\"" \
            " value=\"" + sLabel + "\" />\n"
        sHTML += "<span class=\"ui-icon ui-icon-search forceinline task_picker_btn pointer\"" \
            " target_field_id=\"" + sOTIDField + "\"" \
            " step_id=\"" + sStepID + "\"></span>\n"
        if sActualTaskID != "":
            sHTML += "<span class=\"ui-icon ui-icon-pencil forceinline task_open_btn pointer\" title=\"Edit Task\"" \
                " task_id=\"" + sActualTaskID + "\"></span>\n"
            sHTML += "<span class=\"ui-icon ui-icon-print forceinline task_print_btn pointer\" title=\"View Task\"" \
                " task_id=\"" + sActualTaskID + "\"></span>\n"
        # versions
        if uiCommon.IsGUID(sOriginalTaskID):
            sHTML += "<br />"
            sHTML += "Version: \n"
            sHTML += "<select " + CommonAttribs(oStep, False, "version", "") + \
                " reget_on_change=\"true\">\n"
            # default
            sHTML += "<option " + SetOption("", sVersion) + " value=\"\">Default</option>\n"
    
            sSQL = "select version from task" \
                " where original_task_id = '" + sOriginalTaskID + "'" \
                " order by version"
            dt = uiGlobals.request.db.select_all_dict(sSQL)
            if uiGlobals.request.db.error:
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
    
            if dt:
                for dr in dt:
                    sHTML += "<option " + SetOption(str(dr["version"]), sVersion) + " value=\"" + str(dr["version"]) + "\">" + str(dr["version"]) + "</option>\n"
            else:
                return "Unable to continue - no connection types defined in the database."
    
            sHTML += "</select></span>\n"
    
        # let's display a div for the parameters
        sHTML += "<div class=\"subtask_view_parameters pointer\" id=\"stvp_" + sActualTaskID + "\">"
        sHTML += "<img src=\"static/images/icons/kedit_16.png\" alt=\"Parameters\"> ( click to view parameters )"
        sHTML += "</div>"
    
        return sHTML
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())
        return "Unable to draw Step - see log for details."

def WaitForTasks(oStep):
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
            
        sStepID = oStep.ID
        xd = oStep.FunctionXDoc
    
        sHTML = ""
    
        sHTML += "<div id=\"v" + sStepID + "_handles\">"
        sHTML += "Task Handles:<br />"
    
        xPairs = xd.findall("handle")
        i = 1
        for xe in xPairs:
            sKey = xe.findtext("name", "")
    
            sHTML += "&nbsp;&nbsp;&nbsp;<input type=\"text\" " + CommonAttribs(oStep, True, "handle[" + str(i) + "]/name", "") + \
                " validate_as=\"variable\"" \
                " value=\"" + sKey + "\"" \
                " help=\"Enter a Handle name.\"" \
                " />\n"
    
            sHTML += "<span class=\"ui-icon ui-icon-close forceinline fn_handle_remove_btn pointer\" index=\"" + str(i) + "\" step_id=\"" + sStepID + "\"></span>"
    
            # break it every three fields
            if i % 3 == 0 and i >= 3:
                sHTML += "<br />"
    
            i += 1
    
        sHTML += "<div class=\"fn_wft_add_btn pointer\"" \
            " add_to_id=\"v" + sStepID + "_handles\"" \
            " step_id=\"" + sStepID + "\">" \
            "<img style=\"width:10px; height:10px;\" src=\"static/images/icons/edit_add.png\"" \
            " alt=\"\" title=\"Add another.\" />( click to add another )</div>"
        sHTML += "</div>"
    
        return sHTML
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())
        return "Unable to draw Step - see log for details."

def Dataset(oStep):
    return DrawKeyValueSection(oStep, True, True, "Key", "Value")

def ClearVariable(oStep):
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
            
        sStepID = oStep.ID
        xd = oStep.FunctionXDoc
    
        sHTML = ""
    
        sHTML += "<div id=\"v" + sStepID + "_vars\">"
        sHTML += "Variables to Clear:<br />"
    
        xPairs = xd.findall("variable")
        i = 1
        for xe in xPairs:
            sKey = xe.findtext("name", "")
    
            # Trac#389 - Make sure variable names are trimmed of whitespace if it exists
            # hokey, but doing it here because the field update function is global.
            if sKey.strip() != sKey:
                SetNodeValueinCommandXML(sStepID, "variable[" + str(i) + "]/name", sKey.strip())
    
            sHTML += "&nbsp;&nbsp;&nbsp;<input type=\"text\" " + CommonAttribs(oStep, True, "variable[" + str(i) + "]/name", "") + \
                " validate_as=\"variable\"" \
                " value=\"" + sKey + "\"" \
                " help=\"Enter a Variable name.\"" \
                " />\n"
    
            sHTML += "<span class=\"ui-icon ui-icon-close forceinline fn_var_remove_btn pointer\" index=\"" + str(i) + "\" step_id=\"" + sStepID + "\" title=\"Remove\"></span>"
    
            # break it every three fields
            if i % 3 == 0 and i >= 3:
                sHTML += "<br />"
    
            i += 1
    
        sHTML += "<div class=\"fn_clearvar_add_btn pointer\"" \
            " add_to_id=\"v" + sStepID + "_vars\"" \
            " step_id=\"" + sStepID + "\">" \
            "<span class=\"ui-icon ui-icon-close forceinline\" title=\"Add another.\"></span>( click to add another )</div>"
        sHTML += "</div>"
    
        return sHTML
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())
        return "Unable to draw Step - see log for details."

def SetVariable(oStep):
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
            
        sStepID = oStep.ID
        xd = oStep.FunctionXDoc
    
        sHTML = ""
    
        sHTML += "<div id=\"v" + sStepID + "_vars\">"
        sHTML += "<table border=\"0\" class=\"w99pct\" cellpadding=\"0\" cellspacing=\"0\">\n"
    
        xPairs = xd.findall("variable")
        i = 1
        for xe in xPairs:
    
            sKey = xe.findtext("name", "")
            sVal = xe.findtext("value", "")
            sMod = xe.findtext("modifier", "")
    
            # Trac#389 - Make sure variable names are trimmed of whitespace if it exists
            # hokey, but doing it here because the field update function is global.
            if sKey.strip() != sKey:
                SetNodeValueinCommandXML(sStepID, "variable[" + str(i) + "]/name", sKey.strip())
    
            sHTML += "<tr>\n"
            sHTML += "<td class=\"w1pct\">&nbsp;Variable:&nbsp;</td>\n"
            sHTML += "<td class=\"w1pct\"><input type=\"text\" " + CommonAttribs(oStep, True, "variable[" + str(i) + "]/name", "") + \
                " validate_as=\"variable\"" \
                " value=\"" + sKey + "\"" \
                " help=\"Enter a Variable name.\"" \
                " /></td>\n"
            sHTML += "<td class=\"w1pct\">&nbsp;Value:&nbsp;</td>"
    
            #  we gotta get the field id first, but don't show the textarea until after
            sValueFieldID = uiCommon.NewGUID()
            sCommonAttribs = CommonAttribsWithID(oStep, True, "variable[" + str(i) + "]/value", sValueFieldID, "w90pct")
    
            sHTML += "<td class=\"w75pct\" style=\"vertical-align: bottom;\"><textarea rows=\"1\" style=\"height: 18px;\" " + sCommonAttribs + \
                " help=\"Enter a value for the Variable.\"" \
                ">" + uiCommon.SafeHTML(sVal) + "</textarea>\n"
    
            # big box button
            sHTML += "<span class=\"ui-icon ui-icon-pencil forceinline big_box_btn pointer\" link_to=\"" + sValueFieldID + "\"></span></td>\n"
    
    
            sHTML += "<td class=\"w1pct\">&nbsp;Modifier:&nbsp;</td>"
            sHTML += "<td class=\"w75pct\">"
            sHTML += "<select " + CommonAttribs(oStep, False, "variable[" + str(i) + "]/modifier", "") + ">\n"
            sHTML += "  <option " + SetOption("", sMod) + " value=\"\">--None--</option>\n"
            sHTML += "  <option " + SetOption("TO_UPPER", sMod) + " value=\"TO_UPPER\">UPPERCASE</option>\n"
            sHTML += "  <option " + SetOption("TO_LOWER", sMod) + " value=\"TO_LOWER\">lowercase</option>\n"
            sHTML += "  <option " + SetOption("TO_BASE64", sMod) + " value=\"TO_BASE64\">base64 encode</option>\n"
            sHTML += "  <option " + SetOption("FROM_BASE64", sMod) + " value=\"FROM_BASE64\">base64 decode</option>\n"
            sHTML += "  <option " + SetOption("TO_JSON", sMod) + " value=\"TO_JSON\">Write JSON</option>\n"
            sHTML += "  <option " + SetOption("FROM_JSON", sMod) + " value=\"FROM_JSON\">Read JSON</option>\n"
            sHTML += "</select></td>\n"
    
            sHTML += "<td class=\"w1pct\"><span class=\"ui-icon ui-icon-close forceinline fn_var_remove_btn pointer\" index=\"" + str(i) + "\" step_id=\"" + sStepID + "\">"
            sHTML += "</span></td>"
    
            sHTML += "</tr>\n"
    
            i += 1
    
        sHTML += "</table>\n"
    
        sHTML += "<div class=\"fn_setvar_add_btn pointer\"" \
            " add_to_id=\"v" + sStepID + "_vars\"" \
            " step_id=\"" + sStepID + "\">" \
            "<span class=\"ui-icon ui-icon-plus forceinline\" title=\"Add another.\" />( click to add another )</div>"
        sHTML += "</div>"
    
        return sHTML
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())
        return "Unable to draw Step - see log for details."

def NewConnection(oStep):
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
            
        log("New Connection command:", 4)
        sStepID = oStep.ID
        xd = oStep.FunctionXDoc
        xAsset = xd.find("asset")
        xConnName = xd.find("conn_name")
        xConnType = xd.find("conn_type")
        xCloudName = xd.find("cloud_name")
        sAssetID = ("" if xAsset is None else ("" if xAsset.text is None else xAsset.text))
        sConnType = ("" if xConnType is None else ("" if xConnType.text is None else xConnType.text))
        sCloudName = ("" if xCloudName is None else ("" if xCloudName.text is None else xCloudName.text))
    
        sHTML = ""
        sHTML += "Connect via: \n"
        sHTML += "<select " + CommonAttribs(oStep, True, "conn_type", "") + " reget_on_change=\"true\">\n"
    
        for ct in ConnectionTypes:
            sHTML += "<option " + SetOption(ct, sConnType) + " value=\"" + ct + "\">" + ct + "</option>\n"
    
        sHTML += "</select>\n"
    
        # now, based on the type, we might show or hide certain things
        if sConnType == "ssh - ec2":
            # if the assetid is a guid, it means the user switched from another connection type... wipe it.
            if uiCommon.IsGUID(sAssetID):
                SetNodeValueinCommandXML(sStepID, "asset", "")
                sAssetID = ""
            
            sHTML += " to Instance \n"
            sHTML += "<input type=\"text\" " + \
                CommonAttribs(oStep, True, "asset", "w300px code") + \
                " is_required=\"true\"" \
                " value=\"" + sAssetID + "\"" + " />\n"
    
            sHTML += " in Cloud \n"
            
            sHTML += "<select " + CommonAttribs(oStep, False, "cloud_name", "combo") + ">\n"
            # empty one
            sHTML += "<option " + SetOption("", sCloudName) + " value=\"\"></option>\n"
            
            bValueWasInData = False
            data = ddDataSource_GetAWSClouds()

            if data is not None:
                for k, v in data.iteritems():
                    sHTML += "<option " + SetOption(k, sCloudName) + " value=\"" + k + "\">" + v + "</option>\n"
    
                    if k == sCloudName: bValueWasInData = True
            
            # NOTE: we're allowing the user to enter a value that may not be 
            # in the dataset.  If that's the case, we must add the actual saved value to the list too. 
            if not bValueWasInData: #we didn't find it in the data ..:
                if sCloudName: #and it's a combo and not empty
                    sHTML += "<option " + SetOption(sCloudName, sCloudName) + " value=\"" + sCloudName + "\">" + sCloudName + "</option>\n";            
            
            sHTML += "</select>"
    
        else:
            # clear out the cloud_name property... it's not relevant for these types
            if sCloudName:
                SetNodeValueinCommandXML(sStepID, "cloud_name", "")
            
            # ASSET
            # IF IT's A GUID...
            #  get the asset name belonging to this asset_id
            #  OTHERWISE
            #  make the sAssetName value be what's in sAssetID (a literal value in [[variable]] format)
            if uiCommon.IsGUID(sAssetID):
                sSQL = "select asset_name from asset where asset_id = '" + sAssetID + "'"
                sAssetName = uiGlobals.request.db.select_col_noexcep(sSQL)
                if not sAssetName:
                    if uiGlobals.request.db.error:
                        uiGlobals.request.Messages.append("Unable to look up Asset name." + uiGlobals.request.db.error)
                    else:
                        SetNodeValueinCommandXML(sStepID, "asset", "")
            else:
                sAssetName = sAssetID
    
            sElementID = uiCommon.NewGUID()
    
            sHTML += " to Asset \n"
            sHTML += "<input type=\"text\" " + \
                CommonAttribsWithID(oStep, False, "asset", sElementID, "hidden") + \
                " value=\"" + sAssetID + "\"" + " />\n"
            sHTML += "<input type=\"text\"" \
                " help=\"Select an Asset or enter a variable.\"" \
                " step_id=\"" + sStepID + "\"" \
                " class=\"code w400px\"" \
                " is_required=\"true\"" \
                " id=\"fn_new_connection_assetname_" + sStepID + "\"" \
                " onchange=\"javascript:pushStepFieldChangeVia(this, '" + sElementID + "');\"" \
                " value=\"" + sAssetName + "\" />\n"
    
            
            sHTML += "<span class=\"ui-icon ui-icon-close forceinline fn_field_clear_btn pointer\" clear_id=\"fn_new_connection_assetname_" + sStepID + "\"" \
                " title=\"Clear\"></span>"
    
            sHTML += "<span class=\"ui-icon ui-icon-search forceinline asset_picker_btn pointer\"" \
                " link_to=\"" + sElementID + "\"" \
                " target_field_id=\"fn_new_connection_assetname_" + sStepID + "\"" \
                " step_id=\"" + sStepID + "\"></span>\n"
            
        # nothing special here, just draw the field.
        sHTML += DrawField(xConnName, "conn_name", oStep)
    
        return sHTML
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())
        return "Unable to draw Step - see log for details."

def If(oStep):
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
            
        sStepID = oStep.ID
        xd = oStep.FunctionXDoc
    
        sHTML = ""
    
        xTests = xd.findall("tests/test")
        sHTML += "<div id=\"if_" + sStepID + "_conditions\" number=\"" + str(len(xTests)) + "\">"
    
        i = 1 # because XPath starts at "1"
        for xTest in xTests:
            sEval = xTest.findtext("eval", None)
            xAction = xTest.find("action", None)
    
            #  we gotta get the field id first, but don't show the textarea until after
            sFieldID = uiCommon.NewGUID()
            sCol = "tests/test[" + str(i) + "]/eval"
            sCommonAttribsForTA = CommonAttribsWithID(oStep, True, sCol, sFieldID, "")
    
            # a way to delete the section you just added
            if i == 1:
                xGlobals = ET.parse("luCompareTemplates.xml")
    
                if xGlobals is None:
                    sHTML += "(No Compare templates file available)<br />"
                else:
                    sHTML += "Comparison Template: <select class=\"compare_templates\" textarea_id=\"" + sFieldID + "\">\n"
                    sHTML += "  <option value=\"\"></option>\n"
    
                    xTemplates = xGlobals.findall("template")
                    for xEl in xTemplates:
                        sHTML += "  <option value=\"" + xEl.findtext("value", "") + "\">" + xEl.findtext("name", "") + "</option>\n"
                    sHTML += "</select> <br />\n"
    
    
                sHTML += "If:<br />"
            else:
                sHTML += "<div id=\"if_" + sStepID + "_else_" + str(i) + "\" class=\"fn_if_else_section\">"
                sHTML += "<span class=\"ui-icon ui-icon-close forceinline fn_if_remove_btn pointer\" number=\"" + str(i) + "\" step_id=\"" + sStepID + "\" title=\"Remove this Else If condition.\"></span> "
                sHTML += "&nbsp;&nbsp;&nbsp;Else If:<br />"
    
    
            if sEval is not None:
                sHTML += "<textarea " + sCommonAttribsForTA + " help=\"Enter a test condition.\">" + sEval + "</textarea><br />\n"
            else:
                sHTML += "ERROR: Malformed XML for Step ID [" + sStepID + "].  Missing '" + sCol + "' element."
    
    
            # here's the embedded content
            sCol = "tests/test[" + str(i) + "]/action"

            if xAction is not None:
                xEmbeddedFunction = xAction.find("function")
                # xEmbeddedFunction might be None, but we pass it anyway to get the empty zone drawn
                sHTML += DrawDropZone(oStep, xEmbeddedFunction, sCol, "Action:<br />", True)
            else:
                sHTML += "ERROR: Malformed XML for Step ID [" + sStepID + "].  Missing '" + sCol + "' element."
    
    
            if i != 1:
                sHTML += "</div>"
    
            i += 1
    
        sHTML += "</div>"
    
    
        # draw an add link.  The rest will happen on the client.
        sHTML += "<div class=\"fn_if_add_btn pointer\" add_to_id=\"if_" + sStepID + "_conditions\" step_id=\"" + sStepID + "\" next_index=\"" + str(i) + "\"><span class=\"ui-icon ui-icon-plus forceinline\" title=\"Add another Else If section.\"></span>( click to add another 'Else If' section )</div>"
    
    
        sHTML += "<div id=\"if_" + sStepID + "_else\" class=\"fn_if_else_section\">"
    
        # the final 'else' area
        xElse = xd.find("else", "")
        if xElse is not None:
            sHTML += "<span class=\"fn_if_removeelse_btn pointer\" step_id=\"" + sStepID + "\">" \
               "<span class=\"ui-icon ui-icon-close forceinline\" title=\"Remove this Else condition.\"></span></span> "
            sHTML += "Else (no 'If' conditions matched):"

            xEmbeddedFunction = xElse.find("function")
            # xEmbeddedFunction might be None, but we pass it anyway to get the empty zone drawn
            sHTML += DrawDropZone(oStep, xEmbeddedFunction, "else", "", True)
        else:
            # draw an add link.  The rest will happen on the client.
            sHTML += "<div class=\"fn_if_addelse_btn pointer\" add_to_id=\"if_" + sStepID + "_else\" step_id=\"" + sStepID + "\"><span class=\"ui-icon ui-icon-plus forceinline\" title=\"Add an Else section.\"></span>( click to add a final 'Else' section )</div>"
    
        sHTML += "</div>"
    
        return sHTML
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())
        return "Unable to draw Step - see log for details."

def Loop(oStep):
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
            
        xd = oStep.FunctionXDoc
    
        sStart = xd.findtext("start", "")
        sIncrement = xd.findtext("increment", "")
        sCounter = xd.findtext("counter", "")
        sTest = xd.findtext("test", "")
        sCompareTo = xd.findtext("compare_to", "")
        sMax = xd.findtext("max", "")
    
        xAction = xd.find("action")
    
        sHTML = ""
    
    
        sHTML += "Counter variable \n"
        sHTML += "<input type=\"text\" " + CommonAttribs(oStep, True, "counter", "") + \
            " validate_as=\"variable\" help=\"Variable to increment.\" value=\"" + sCounter + "\" />\n"
    
        sHTML += " begins at\n"
        sHTML += "<input type=\"text\" " + CommonAttribs(oStep, True, "start", "w100px")
        sHTML += " help=\"Enter an integer value where the loop will begin.\" value=\"" + sStart + "\" />\n"
    
        sHTML += " and increments by \n"
        sHTML += "<input type=\"text\" " + CommonAttribs(oStep, True, "increment", "w100px") + \
            " help=\"The integer value to increment the counter after each loop.\" value=\"" + sIncrement + "\" />.<br />\n"
    
        sHTML += "Loop will continue while variable is \n"
        sHTML += "<select " + CommonAttribs(oStep, False, "test", "") + ">\n"
        sHTML += "  <option " + SetOption("==", sTest) + " value=\"==\">==</option>\n"
        sHTML += "  <option " + SetOption("!=", sTest) + " value=\"!=\">!=</option>\n"
        sHTML += "  <option " + SetOption("<=", sTest) + " value=\"<=\">&lt;=</option>\n"
        sHTML += "  <option " + SetOption("<", sTest) + " value=\"<\">&lt;</option>\n"
        sHTML += "  <option " + SetOption(">=", sTest) + " value=\">=\">&gt;=</option>\n"
        sHTML += "  <option " + SetOption(">", sTest) + " value=\">\">&gt;</option>\n"
        sHTML += "</select>\n"
    
        sHTML += "<input type=\"text\" " + CommonAttribs(oStep, True, "compare_to", "w400px") + \
            " help=\"Loop until variable compared with this value becomes 'false'.\" value=\"" + sCompareTo + "\" />\n"
    
    
        sHTML += "<br /> or \n"
        sHTML += "<input type=\"text\" " + CommonAttribs(oStep, False, "max", "w50px") + \
            " help=\"For safety, enter a maximum number of times to loop before aborting.\" value=\"" + sMax + "\" /> loops have occured.\n"
    
        sHTML += "<hr />\n"
    
        # enable the dropzone for the Action
        if xAction is not None:
            xEmbeddedFunction = xAction.find("function")
            # xEmbeddedFunction might be None, but we pass it anyway to get the empty zone drawn
            sHTML += DrawDropZone(oStep, xEmbeddedFunction, "action", "Action:<br />", True)
        else:
            sHTML += "ERROR: Malformed XML for Step ID [" + oStep.ID + "].  Missing 'action' element."
    
    
        return sHTML
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())
        return "Unable to draw Step - see log for details."

def While(oStep):
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
            
        xd = oStep.FunctionXDoc
    
        sTest = xd.findtext("test", "")
        xAction = xd.find("action")
    
        sHTML = ""
        sHTML += "While: \n"
        sHTML += "<td class=\"w75pct\" style=\"vertical-align: bottom;\"><textarea rows=\"10\" style=\"height: 18px;\" " + \
            CommonAttribs(oStep, False, "test", "") + " help=\"\"" \
            ">" + uiCommon.SafeHTML(sTest) + "</textarea>\n"
    
    
        # enable the dropzone for the Action
        if xAction is not None:
            xEmbeddedFunction = xAction.find("function")
            # xEmbeddedFunction might be None, but we pass it anyway to get the empty zone drawn
            sHTML += DrawDropZone(oStep, xEmbeddedFunction, "action", "<hr />Action:<br />", True)
        else:
            sHTML += "ERROR: Malformed XML for Step ID [" + oStep.ID + "].  Missing 'action' element."
    
    
        return sHTML
    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())
        return "Unable to draw Step - see log for details."

def Exists(oStep):
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
            
        xd = oStep.FunctionXDoc
    
        sHTML = ""
        sHTML += "<div id=\"v" + oStep.ID + "_vars\">"
        sHTML += "Variables to Test:<br />"
    
        xPairs = xd.findall("variable")
        i = 1
        for xe in xPairs:
            sKey = xe.findtext("name", "")
            sIsTrue = xe.findtext("is_true", "")
    
            # Trac#389 - Make sure variable names are trimmed of whitespace if it exists
            # hokey, but doing it here because the field update function is global.
            if sKey.strip() != sKey:
                SetNodeValueinCommandXML(oStep.ID, "variable[" + str(i) + "]/name", sKey.strip())
    
            sHTML += "&nbsp;&nbsp;&nbsp;<input type=\"text\" " + \
                CommonAttribs(oStep, True, "variable[" + str(i) + "]/name", "") + \
                " validate_as=\"variable\"" \
                " value=\"" + sKey + "\"" \
                " help=\"Enter a Variable name.\"" \
                " />"
    
            sHTML += "&nbsp; Is True:<input type=\"checkbox\" " + \
                CommonAttribs(oStep, True, "variable[" + str(i) + "]/is_true", "") + " " + SetCheckRadio("1", sIsTrue) + " />\n"
    
            sHTML += "<span class=\"ui-icon ui-icon-close forceinline fn_var_remove_btn pointer\" index=\"" + str(i) + "\" step_id=\"" + oStep.ID + "\" title=\"Remove\"></span>"
    
            # break it every three fields
            # if i % 3 == 0 and i >= 3:
            sHTML += "<br />"
    
            i += 1
    
        sHTML += "<div class=\"fn_exists_add_btn pointer\"" \
            " add_to_id=\"v" + oStep.ID + "_vars\"" \
            " step_id=\"" + oStep.ID + "\">" \
            "<span class=\"ui-icon ui-icon-plus forceinline\" title=\"Add another.\"></span>( click to add another )</div>"
        sHTML += "</div>"
    
        #  Exists have a Positive and Negative action
        xPositiveAction = xd.find("actions/positive_action")
        if xPositiveAction is None:
            return "Error: XML does not contain positive_action"
    
        xNegativeAction = xd.find("actions/negative_action")
        if xNegativeAction is None:
            return "Error: XML does not contain negative_action"
    
        sCol = ""
    
        # here's the embedded content
        sCol = "actions/positive_action"
    
        if xPositiveAction is not None:
            xEmbeddedFunction = xPositiveAction.find("function")
            sHTML += DrawDropZone(oStep, xEmbeddedFunction, sCol, "Positive Action:<br />", True)
        else:
            sHTML += "ERROR: Malformed XML for Step ID [" + oStep.ID + "].  Missing '" + sCol + "' element."
    
    
        sCol = "actions/negative_action"
    
        if xNegativeAction is not None:
            xEmbeddedFunction = xNegativeAction.find("function")
            sHTML += DrawDropZone(oStep, xEmbeddedFunction, sCol, "Negative Action:<br />", True)
        else:
            sHTML += "ERROR: Malformed XML for Step ID [" + oStep.ID + "].  Missing '" + sCol + "' element."
    
        #  The End.
        return sHTML

    except Exception:
        uiGlobals.request.Messages.append(traceback.format_exc())
        return "Unable to draw Step - see log for details."

def Codeblock(oStep):
    xd = oStep.FunctionXDoc

    sCB = xd.findtext("codeblock", "")
    sHTML = ""
    sElementID = uiCommon.NewGUID()

    sHTML += "Codeblock: \n"
    sHTML += "<input type=\"text\" " + CommonAttribsWithID(oStep, True, "codeblock", sElementID, "") + \
        " reget_on_change=\"true\"" \
        " help=\"Enter a Codeblock Name or variable, or select a Codeblock from the picker.\"" \
        " value=\"" + sCB + "\" />\n"
    sHTML += "<span class=\"ui-icon ui-icon-search forceinline codeblock_picker_btn pointer\" title=\"Pick a Codeblock\"" \
        " link_to=\"" + sElementID + "\"></span>\n"

    if sCB != "":
        # don't enable the jump link if it isn't a valid codeblock on this task.
        # and DON'T CRASH if there isn't a list of codeblocks. (sometimes step objects may not have a full task parent)
        if oStep.Task:
            if oStep.Task.Codeblocks:
                for cb in oStep.Task.Codeblocks:
                    if sCB == cb:
                        sHTML += "<span class=\"ui-icon ui-icon-link forceinline codeblock_goto_btn pointer\" title=\"Go To Codeblock\"" \
                            " codeblock=\"" + sCB + "\"></span>\n"
                        break

    return sHTML
