import sys
from uiCommon import log
import uiCommon
from catocommon import catocommon
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
    sFunction = oStep.FunctionName
    sHTML = ""
    sOptionHTML = ""
    sVariableHTML = ""

    # NOTE: If you are adding a new command type, be aware that
    # you MIGHT need to modify the code in taskMethods for the wmAddStep function.
    # (depending on how your new command works)
    # 
    # IF the command populates variables, it will need a case statement added to that function
    # to ensure the output_parse_type field is properly set.
    # 


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
    elif sFunction.lower() == "if":
        sHTML = If(oStep)
    elif sFunction.lower() == "loop":
        sHTML = "Not Yet Available" #Loop(oStep)
    elif sFunction.lower() == "while":
        sHTML = "Not Yet Available" #While(oStep)
    elif sFunction.lower() == "sql_exec":
        sHTML = "Not Yet Available" #SqlExec(oStep)
    elif sFunction.lower() == "set_variable":
        sHTML = SetVariable(oStep)
    elif sFunction.lower() == "clear_variable":
        sHTML = ClearVariable(oStep)
    elif sFunction.lower() == "wait_for_tasks":
        sHTML = WaitForTasks(oStep)
    elif sFunction.lower() == "dataset":
        sHTML = Dataset(oStep)
    elif sFunction.lower() == "subtask":
        sHTML = "Not Yet Available" #Subtask(oStep)
    elif sFunction.lower() == "set_asset_registry":
        sHTML = "Not Yet Available" #SetAssetRegistry(oStep)
    elif sFunction.lower() == "run_task":
        sHTML = "Not Yet Available" #RunTask(oStep)
    elif sFunction.lower() == "transfer":
        sHTML = "Not Yet Available" #Transfer(oStep)
    elif sFunction.lower() == "exists":
        sHTML = "Not Yet Available" #Exists(oStep)
    elif sFunction.lower() == "get_ecosystem_objects":
        sHTML = "Not Yet Available" #GetEcosystemObjects(oStep)
    else:
        # We didn't find one of our built in commands.  That's ok - most commands are drawn from their XML.
        sHTML, sOptionHTML = DrawStepFromXMLDocument(oStep)
    
    # IF a command "populates variables" it will be noted in the command xml
    # is the variables xml attribute true?
    xd = oStep.FunctionXDoc
    if xd is not None:
        sPopulatesVars = xd.get("variables", "")
        log("Populates Variables?" + sPopulatesVars, 4)
        if uiCommon.IsTrue(sPopulatesVars):
            sVariableHTML += "## WOULD DRAW VARSECTION ##" #DrawVariableSectionForDisplay(oStep, true)
    
    # This returns a Tuple with three values.
    return sHTML, sOptionHTML, sVariableHTML

def DrawStepFromXMLDocument(oStep):
    sStepID = oStep.ID
    sFunction = oStep.FunctionName
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
    log("Command XML:", 4)
    log(ET.tostring(xd), 4)
    if xd is not None:
        # for each node in the function element
        # each node will become a field on the step.
        # some fields may be defined to go on an "options tab", in which case they will come back as sNodeOptionHTML
        # you'll never get back both NodeHTML and OptionHTML - one will always be blank.
        for xe in xd:
            log("Drawing [" + xe.tag + "]", 4)
            sNodeHTML, sNodeOptionHTML = DrawNode(xe, xe.tag, sStepID, sFunction)
            sHTML += sNodeHTML
            sOptionHTML += sNodeOptionHTML
            
    return sHTML, sOptionHTML
    
def DrawNode(xeNode, sXPath, sStepID, sFunction):
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
            sNodeHTML, sOptionHTML = DrawNode(xeOnlyChild, sChildXPath, sStepID, sFunction)
            if sOptionTab:
                sHTML += sNodeName + "." + sOptionHTML
            else:
                sHTML += sNodeName + "." + sNodeHTML
            
            #since we're making it composite, the parents are gonna be off.  Go ahead and draw the delete link here.
            if bIsRemovable:
                sHTML += "<span class=\"fn_nodearray_remove_btn pointer\" xpath_to_delete=\"" + sXPath + "\" step_id=\"" + sStepID + "\">"
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
                sHTML += "<div class=\"fn_nodearray_add_btn pointer\"" + " step_id=\"" + sStepID + "\"" \
                    " xpath=\"" + sXPath + "\">" \
                    "<img style=\"width:10px; height:10px;\" src=\"static/images/icons/edit_add.png\"" \
                    " alt=\"\" title=\"Add another...\" /></div>"
    
            #BUT, if this nodes PARENT is editable, that means THIS NODE can be deleted.
            #so, it gets a delete link
            #you can't remove unless there are more than one
            if bIsRemovable:
                sHTML += "<span class=\"fn_nodearray_remove_btn pointer\" xpath_to_delete=\"" + sXPath + "\" step_id=\"" + sStepID + "\">"
                sHTML += "<img style=\"width:10px; height:10px;\" src=\"static/images/icons/fileclose.png\" alt=\"\" title=\"Remove\" /></span>"
            sHTML += "</div>" #end step header icons
            sHTML += "  </div>" #end header
    
            for xeChildNode in xeNode:
                sChildNodeName = xeChildNode.tag
                sChildXPath = sXPath + "/" + sChildNodeName
    
                #here's the magic... are there any children nodes here with the SAME NAME?
                #if so they need an index on the xpath
                if len(xeNode.find(sChildNodeName)) > 1:
                    print "1"
                    #since the document won't necessarily be in perfect order,
                    #we need to keep track of same named nodes and their indexes.
                    #so, stick each array node up in a lookup table.
                    #is it already in my lookup table?
                    iLastIndex = 0
                    if dictNodes.has_key(sChildNodeName):
                        print "2"
                        #not there, add it
                        iLastIndex = 1
                        dictNodes[sChildNodeName] = iLastIndex
                    else:
                        print "3"
                        #there, increment it and set it
                        iLastIndex += 1
                        dictNodes[sChildNodeName] = iLastIndex
                    sChildXPath = sChildXPath + "[" + str(iLastIndex) + "]"
                    
                # it's not possible for an 'editable' node to be in the options tab if it's parents aren't,
                # so here we ignore the options return
                sNodeHTML, sBunk = DrawNode(xeChildNode, sChildXPath, sStepID, sFunction)
                if sBunk:
                    log("WARNING: This shouldn't have returned 'option' html.", 2)
                sHTML += sNodeHTML
    
            sHTML += "</div>"
    else: #end section
        sHTML += DrawField(xeNode, sXPath, sStepID, sFunction)
        #it may be that these fields themselves are removable
        if bIsRemovable:
            sHTML += "<span class=\"fn_nodearray_remove_btn pointer\" xpath_to_delete=\"" + sXPath + "\" step_id=\"" + sStepID + "\">"
            sHTML += "<img style=\"width:10px; height:10px; margin-right: 4px;\" src=\"static/images/icons/fileclose.png\" alt=\"\" title=\"Remove\" /></span>"
    
    #ok, now that we've drawn it, it might be intended to go on the "options tab".
    #if so, stick it there
    if sOptionTab:
        return "", sHTML
    else:
        return sHTML, ""
        
def DrawField(xe, sXPath, sStepID, sFunction):
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
            CommonAttribsWithID(sStepID, sFunction, bRequired, sXPath, sTextareaID, sCSSClasses) + \
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

        sHTML += sNodeLabel + " <select " + CommonAttribs(sStepID, sFunction, False, sXPath, sFieldStyle) + ">\n"
        
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
            except Exception, ex:
                return "Unable to render input element [" + sXPath + "]. Lookup file [" + sDataSet + "] not found or incorrect format." + ex.__str__()
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
            except Exception as ex:
                uiGlobals.request.Messages.append(ex.__str__())
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
            CommonAttribsWithID(sStepID, sFunction, bRequired, sXPath, sElementID, sCSSClasses) + \
            " style=\"" + sStyle + "\"" \
            " help=\"" + sHelp + "\"" \
            " value=\"" + sNodeValue + "\" />"
        #might this be a conn_name field?  If so, we can show the picker.
        sConnPicker = xe.get("connection_picker", "")
        if uiCommon.IsTrue(sConnPicker):
            sHTML += "<img class=\"conn_picker_btn pointer\" alt=\"\" src=\"static/images/icons/search.png\" link_to=\"" + sElementID + "\" />"

    #some final layout possibilities
    if sBreakAfter == uiCommon.IsTrue(sBreakAfter):
        sHTML += "<br />"
    if sHRAfter == uiCommon.IsTrue(sHRAfter):
        sHTML += "<hr />"

    log("---- ... done", 4)
    return sHTML

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

def SetOption(s1, s2):
    return " selected=\"selected\"" if s1 == s2 else ""

def SetCheckRadio(s1, s2):
    return " checked=\"checked\"" if s1 == s2 else ""

# NOTE: the following functions are internal, but support dynamic dropdowns on step functions.
# the function name is referenced by the "dataset" value of a dropdown type of input, where the datasource="function"
# dropdowns expect a Dictionary<string,string> object return

def ddDataSource_GetAWSClouds():
    data = {}
    
    # AWS regions
    p = providers.Provider.GetFromSession("Amazon AWS")
    if p is not None:
        for c_name, c in p.Clouds.iteritems():
            data[c.Name] = c.Name
    # Eucalyptus clouds
    p = providers.Provider.GetFromSession("Eucalyptus")
    if p is not None:
        for c_name, c in p.Clouds.iteritems():
            data[c.Name] = c.Name

    return data

def AddToCommandXML(sStepID, sXPath, sXMLToAdd):
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
        if not uiCommon.IsGUID(sStepID):
            uiGlobals.request.Messages.append("Unable to modify step. Invalid or missing Step ID. [" + sStepID + "].")

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
    except Exception, ex:
        uiGlobals.request.Messages.append(ex.__str__())

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
            xd = ET.fromstring(sXML)
            if xd is None:
                uiGlobals.request.Messages.append("Error: Unable to parse XML.")

            # get the specified node from the doc, IF IT'S NOT THE ROOT
            if xd.tag == sXPath:
                xNodeToEdit = xd
            else:
                xNodeToEdit = xd.find(sXPath)
            
            if xNodeToEdit is None:
                uiGlobals.request.Messages.append("Error: XML does not contain path [" + sXPath + "].")

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
    except Exception, ex:
        uiGlobals.request.Messages.append(ex.__str__())

def SetNodeValueinCommandXML(sStepID, sNodeToSet, sValue):
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
        if not uiCommon.IsGUID(sStepID):
            uiGlobals.request.Messages.append("Unable to modify step. Invalid or missing Step ID. [" + sStepID + "] ")

        SetNodeValueinXMLColumn("task_step", "function_xml", "step_id = '" + sStepID + "'", sNodeToSet, sValue)

        return
    except Exception, ex:
        uiGlobals.request.Messages.append(ex.__str__())

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
    except Exception, ex:
        uiGlobals.request.Messages.append(ex.__str__())

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
    except Exception, ex:
        uiGlobals.request.Messages.append(ex.__str__())

def RemoveNodeFromXMLColumn(sTable, sXMLColumn, sWhereClause, sNodeToRemove):
    uiCommon.log("Removing node [%s] from [%s.%s where %s]." % (sNodeToRemove, sTable, sXMLColumn, sWhereClause), 4)
    try:
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
        sSQL = "select " + sXMLColumn + " from " + sTable + " where " + sWhereClause
        sXML = uiGlobals.request.db.select_col_noexcep(sSQL)
        if not sXML:
            uiGlobals.request.Messages.append("Unable to get xml." + uiGlobals.request.db.error)
        else:
            uiCommon.log(sXML, 4)
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

            # whack it
            xd.remove(xNodeToWhack)

            sSQL = "update " + sTable + " set " + sXMLColumn + " = '" + uiCommon.TickSlash(ET.tostring(xd)) + "'" \
                " where " + sWhereClause
            if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                uiGlobals.request.Messages.append("Unable to update XML Column [" + sXMLColumn + "] on [" + sTable + "]." + uiGlobals.request.db.error)

        return
    except Exception, ex:
        uiGlobals.request.Messages.append(ex.__str__())

def DrawDropZone(sParentStepID, sEmbeddedStepID, sFunction, sColumn, sLabel, bRequired):
    # drop zones are common for all the steps that can contain embedded steps.
    # they are a div to drop on and a hidden field to hold the embedded step id.
    sHTML = ""
    sElementID = uiCommon.NewGUID()

    # a hidden field holds the embedded step_id as the data.
    # Following this is a dropzone that actually gets the graphical representation of the embedded step.
    sHTML += "<input type=\"text\" " + \
        CommonAttribsWithID(sParentStepID, sFunction, False, sColumn, sElementID, "hidden") + \
        " value=\"" + sEmbeddedStepID + "\" />\n"

    sHTML += sLabel

    # some of our 'columns' may be complex XPaths.  XPaths have invalid characters for use in 
    # an HTML ID attribute
    # but we need it to be unique... so just 'clean up' the column name
    sColumn = sColumn.replace("[", "").replace("]", "").replace("/", "")

    # the dropzone
    sDropZone = "<div" + \
        (" is_required=\"true\" value=\"\"" if bRequired else "") + \
        " id=\"" + sFunction + "_" + sParentStepID + "_" + sColumn + "_dropzone\"" \
        " datafield_id=\"" + sElementID + "\"" \
        " step_id=\"" + sParentStepID + "\"" \
        " class=\"step_nested_drop_target " + ("is_required" if bRequired else "") + "\">Click here to add a Command.</div>"

    # GONNA RETHINK THE WHOLE EMBEDDED THING
    """
    if uiCommon.IsGUID(sEmbeddedStepID):
        oEmbeddedStep = GetSingleStep(sEmbeddedStepID, sUserID)
        if oEmbeddedStep is not None:
            sHTML += DrawEmbeddedStep(oEmbeddedStep)
        else:
            sHTML += "<span class=\"red_text\">" + db.error + "</span>"
    else:
        sHTML += sDropZone
    """
    sHTML += sDropZone # THIS IS FOR TESTING ONLY, REMOVE IT WHEN YOU UNCOMMENT THE PREVIOUS BLOCK
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

        sHTML += "<td class=\"w1pct\"><input type=\"text\" " + CommonAttribsWithID(sStepID, sFunction, True, "pair[" + str(i) + "]/key", sElementID, "") + \
            " validate_as=\"variable\"" \
            " value=\"" + uiCommon.SafeHTML(sKey) + "\"" \
            " help=\"Enter a name.\"" \
            " /></td>"

        if bShowPicker:
            sHTML += "<td class=\"w1pct\"><img class=\"key_picker_btn pointer\" alt=\"\"" \
                " src=\"static/images/icons/search.png\"" \
                " function=\"" + sFunction + "\"" \
                " target_field_id=\"" + sElementID + "\"" \
                " link_to=\"" + sElementID + "\" />\n"

            sHTML += "</td>\n"

        sHTML += "<td class=\"w1pct\">&nbsp;" + sValueLabel + ":&nbsp;</td>"

        #  we gotta get the field id first, but don't show the textarea until after
        sCommonAttribs = CommonAttribsWithID(sStepID, sFunction, True, "pair[" + str(i) + "]/value", sValueFieldID, "w90pct")

        sHTML += "<td class=\"w50pct\"><input type=\"text\" " + sCommonAttribs + \
            " value=\"" + uiCommon.SafeHTML(sVal) + "\"" \
            " help=\"Enter a value.\"" \
            " />\n"

        # big box button
        sHTML += "<img class=\"big_box_btn pointer\" alt=\"\"" \
            " src=\"static/images/icons/edit_16.png\"" \
            " link_to=\"" + sValueFieldID + "\" /></td>\n"

        # optional mask option
        if bShowMaskOption:
            sHTML += "<td>"

            sHTML += "&nbsp;Mask?: <input type=\"checkbox\" " + \
                CommonAttribs(sStepID, sFunction, True, "pair[" + str(i) + "]/mask", "") + " " + SetCheckRadio("1", sMask) + " />\n"


            sHTML += "</td>\n"

        sHTML += "<td class=\"w1pct\" align=\"right\"><span class=\"fn_pair_remove_btn pointer\" index=\"" + str(i) + "\" step_id=\"" + sStepID + "\">"
        sHTML += "<img style=\"width:10px; height:10px;\" src=\"static/images/icons/fileclose.png\"" \
            " alt=\"\" title=\"Remove\" /></span></td>"

        sHTML += "</tr></table>\n"

        i += 1

    sHTML += "<div class=\"fn_pair_add_btn pointer\"" \
        " add_to_id=\"" + sStepID + "_pairs\"" \
        " step_id=\"" + sStepID + "\">" \
        "<img style=\"width:10px; height:10px;\" src=\"static/images/icons/edit_add.png\"" \
        " alt=\"\" title=\"Add another.\" />( click to add another )</div>"
    sHTML += "</div>"

    return sHTML


"""
From here to the bottom are the hardcoded commands.
"""

def WaitForTasks(oStep):
    sStepID = oStep.ID
    sFunction = oStep.FunctionName
    xd = oStep.FunctionXDoc

    sHTML = ""

    sHTML += "<div id=\"v" + sStepID + "_handles\">"
    sHTML += "Task Handles:<br />"

    xPairs = xd.findall("handle")
    i = 1
    for xe in xPairs:
        sKey = xe.findtext("name", "")

        sHTML += "&nbsp;&nbsp;&nbsp;<input type=\"text\" " + CommonAttribs(sStepID, sFunction, True, "handle[" + str(i) + "]/name", "") + \
            " validate_as=\"variable\"" \
            " value=\"" + sKey + "\"" \
            " help=\"Enter a Handle name.\"" \
            " />\n"

        sHTML += "<span class=\"fn_handle_remove_btn pointer\" index=\"" + str(i) + "\" step_id=\"" + sStepID + "\">"
        sHTML += "<img style=\"width:10px; height:10px;\" src=\"static/images/icons/fileclose.png\"" \
            " alt=\"\" title=\"Remove\" /></span>"

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

def Dataset(oStep):
    return DrawKeyValueSection(oStep, True, True, "Key", "Value")

def ClearVariable(oStep):
    sStepID = oStep.ID
    sFunction = oStep.FunctionName
    xd = oStep.FunctionXDoc

    sHTML = ""

    sHTML += "<div id=\"v" + sStepID + "_vars\">"
    sHTML += "Variables to Clear:<br />"

    xPairs = xd.findall("variable")
    i = 1
### CHECK NEXT LINE for type declarations !!!
    for xe in xPairs:
        sKey = xe.findtext("name", "")

        # Trac#389 - Make sure variable names are trimmed of whitespace if it exists
        # hokey, but doing it here because the field update function is global.
        if sKey.strip() != sKey:
            SetNodeValueinCommandXML(sStepID, "variable[" + str(i) + "]/name", sKey.strip())

        sHTML += "&nbsp;&nbsp;&nbsp;<input type=\"text\" " + CommonAttribs(sStepID, sFunction, True, "variable[" + str(i) + "]/name", "") + \
            " validate_as=\"variable\"" \
            " value=\"" + sKey + "\"" \
            " help=\"Enter a Variable name.\"" \
            " />\n"

        sHTML += "<span class=\"fn_var_remove_btn pointer\" index=\"" + str(i) + "\" step_id=\"" + sStepID + "\">"
        sHTML += "<img style=\"width:10px; height:10px;\" src=\"static/images/icons/fileclose.png\"" \
            " alt=\"\" title=\"Remove\" /></span>"

        # break it every three fields
        if i % 3 == 0 and i >= 3:
            sHTML += "<br />"

        i += 1

    sHTML += "<div class=\"fn_clearvar_add_btn pointer\"" \
        " add_to_id=\"v" + sStepID + "_vars\"" \
        " step_id=\"" + sStepID + "\">" \
        "<img style=\"width:10px; height:10px;\" src=\"static/images/icons/edit_add.png\"" \
        " alt=\"\" title=\"Add another.\" />( click to add another )</div>"
    sHTML += "</div>"

    return sHTML

def SetVariable(oStep):
    uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
    sStepID = oStep.ID
    sFunction = oStep.FunctionName
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
        sHTML += "<td class=\"w1pct\"><input type=\"text\" " + CommonAttribs(sStepID, sFunction, True, "variable[" + str(i) + "]/name", "") + \
            " validate_as=\"variable\"" \
            " value=\"" + sKey + "\"" \
            " help=\"Enter a Variable name.\"" \
            " /></td>\n"
        sHTML += "<td class=\"w1pct\">&nbsp;Value:&nbsp;</td>"

        #  we gotta get the field id first, but don't show the textarea until after
        sValueFieldID = uiCommon.NewGUID()
        sCommonAttribs = CommonAttribsWithID(sStepID, sFunction, True, "variable[" + str(i) + "]/value", sValueFieldID, "w90pct")

        sHTML += "<td class=\"w75pct\" style=\"vertical-align: bottom;\"><textarea rows=\"1\" style=\"height: 18px;\" " + sCommonAttribs + \
            " help=\"Enter a value for the Variable.\"" \
            ">" + uiCommon.SafeHTML(sVal) + "</textarea>\n"

        # big box button
        sHTML += "<img class=\"big_box_btn pointer\" alt=\"\"" \
            " src=\"static/images/icons/edit_16.png\"" \
            " link_to=\"" + sValueFieldID + "\" /></td>\n"


        sHTML += "<td class=\"w1pct\">&nbsp;Modifier:&nbsp;</td>"
        sHTML += "<td class=\"w75pct\">"
        sHTML += "<select " + CommonAttribs(sStepID, sFunction, False, "variable[" + str(i) + "]/modifier", "") + ">\n"
        sHTML += "  <option " + SetOption("", sMod) + " value=\"\">--None--</option>\n"
        sHTML += "  <option " + SetOption("TO_UPPER", sMod) + " value=\"TO_UPPER\">UPPERCASE</option>\n"
        sHTML += "  <option " + SetOption("TO_LOWER", sMod) + " value=\"TO_LOWER\">lowercase</option>\n"
        sHTML += "  <option " + SetOption("TO_BASE64", sMod) + " value=\"TO_BASE64\">base64 encode</option>\n"
        sHTML += "  <option " + SetOption("FROM_BASE64", sMod) + " value=\"FROM_BASE64\">base64 decode</option>\n"
        sHTML += "  <option " + SetOption("TO_JSON", sMod) + " value=\"TO_JSON\">Write JSON</option>\n"
        sHTML += "  <option " + SetOption("FROM_JSON", sMod) + " value=\"FROM_JSON\">Read JSON</option>\n"
        sHTML += "</select></td>\n"

        sHTML += "<td class=\"w1pct\"><span class=\"fn_var_remove_btn pointer\" index=\"" + str(i) + "\" step_id=\"" + sStepID + "\">"
        sHTML += "<img style=\"width:10px; height:10px;\" src=\"static/images/icons/fileclose.png\"" \
            " alt=\"\" title=\"Remove\" /></span></td>"

        sHTML += "</tr>\n"

        i += 1

    sHTML += "</table>\n"

    sHTML += "<div class=\"fn_setvar_add_btn pointer\"" \
        " add_to_id=\"v" + sStepID + "_vars\"" \
        " step_id=\"" + sStepID + "\">" \
        "<img style=\"width:10px; height:10px;\" src=\"static/images/icons/edit_add.png\"" \
        " alt=\"\" title=\"Add another.\" />( click to add another )</div>"
    sHTML += "</div>"

    return sHTML

def NewConnection(oStep):
    uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
    log("New Connection command:", 4)
    sStepID = oStep.ID
    sFunction = oStep.FunctionName
    xd = oStep.FunctionXDoc
    xAsset = xd.find("asset")
    xConnName = xd.find("conn_name")
    xConnType = xd.find("conn_type")
    xCloudName = xd.find("cloud_name")
    sAssetID = ("" if xAsset is None else ("" if xAsset.text is None else xAsset.text))
    sConnName = ("" if xConnName is None else ("" if xConnName.text is None else xConnName.text))
    sConnType = ("" if xConnType is None else ("" if xConnType.text is None else xConnType.text))
    sCloudName = ("" if xCloudName is None else ("" if xCloudName.text is None else xCloudName.text))

    sHTML = ""
    sHTML += "Connect via: \n"
    sHTML += "<select " + CommonAttribs(sStepID, sFunction, True, "conn_type", "") + " reget_on_change=\"true\">\n"

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
            CommonAttribs(sStepID, sFunction, True, "asset", "w300px code") + \
            " is_required=\"true\"" \
            " value=\"" + sAssetID + "\"" + " /><br />\n"

        sHTML += " in Cloud \n"
        
        sHTML += "<select " + CommonAttribs(sStepID, sFunction, False, "cloud_name", "combo") + ">\n"
        # empty one
        sHTML += "<option " + SetOption("", sCloudName) + " value=\"\"></option>\n"
        
        bValueWasInData = False
        data = ddDataSource_GetAWSClouds()
        
        if data is not None:
            for k, v in data:
                sHTML += "<option " + SetOption(k, sCloudName) + " value=\"" + k + "\">" + v + "</option>\n"

                if k ==sCloudName: bValueWasInData = True
        
        # NOTE: we're allowing the user to enter a value that may not be 
        # in the dataset.  If that's the case, we must add the actual saved value to the list too. 
        if not bValueWasInData: #we didn't find it in the data ..:
            if sCloudName: #and it's a combo and not empty
                sHTML += "<option " + SetOption(sCloudName, sCloudName) + " value=\"" + sCloudName + "\">" + sCloudName + "</option>\n";            
        
        sHTML += "</select>"

    else:
        # clear out the cloud_name property... it's not relevant for these types
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
            CommonAttribsWithID(sStepID, sFunction, False, "asset", sElementID, "hidden") + \
            " value=\"" + sAssetID + "\"" + " />\n"
        sHTML += "<input type=\"text\"" \
            " help=\"Select an Asset or enter a variable.\"" \
            " step_id=\"" + sStepID + "\"" \
            " class=\"code w400px\"" \
            " is_required=\"true\"" \
            " id=\"fn_new_connection_assetname_" + sStepID + "\"" \
            " onchange=\"javascript:pushStepFieldChangeVia(this, '" + sElementID + "');\"" \
            " value=\"" + sAssetName + "\" />\n"

        
        sHTML += "<img class=\"fn_field_clear_btn pointer\" clear_id=\"fn_new_connection_assetname_" + sStepID + "\"" \
            " style=\"width:10px; height:10px;\" src=\"static/images/icons/fileclose.png\"" \
            " alt=\"\" title=\"Clear\" />"

        sHTML += "<img class=\"asset_picker_btn pointer\" alt=\"\"" \
            " link_to=\"" + sElementID + "\"" \
            " target_field_id=\"fn_new_connection_assetname_" + sStepID + "\"" \
            " step_id=\"" + sStepID + "\"" \
            " src=\"static/images/icons/search.png\" />\n"
        
    sHTML += " as \n"
    sHTML += "<input type=\"text\" " + CommonAttribs(sStepID, sFunction, True, "conn_name", "w200px") + \
        " help=\"Name this connection for reference in the Task.\" value=\"" + sConnName + "\" />\n"
    sHTML += "\n"


    return sHTML

def If(oStep):
    uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
    sStepID = oStep.ID
    sFunction = oStep.FunctionName
    xd = oStep.FunctionXDoc

    sHTML = ""

    xTests = xd.findall("tests/test")
    sHTML += "<div id=\"if_" + sStepID + "_conditions\" number=\"" + str(len(xTests)) + "\">"

    i = 1 # because XPath starts at "1"

    for xTest in xTests:
        sEval = xTest.findtext("eval", None)
        sAction = xTest.findtext("action", None)

        #  we gotta get the field id first, but don't show the textarea until after
        sFieldID = uiCommon.NewGUID()
        sCol = "tests/test[" + str(i) + "]/eval"
        sCommonAttribsForTA = CommonAttribsWithID(sStepID, sFunction, True, sCol, sFieldID, "")

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
            sHTML += "<span class=\"fn_if_remove_btn pointer\" number=\"" + str(i) + "\" step_id=\"" + sStepID + "\">" \
                "<img style=\"width:10px; height:10px;\" src=\"static/images/icons/fileclose.png\" alt=\"\" title=\"Remove this Else If condition.\" /></span> "
            sHTML += "&nbsp;&nbsp;&nbsp;Else If:<br />"


        print sEval
        if sEval is not None:
            sHTML += "<textarea " + sCommonAttribsForTA + " help=\"Enter a test condition.\">" + sEval + "</textarea><br />\n"
        else:
            sHTML += "ERROR: Malformed XML for Step ID [" + sStepID + "].  Missing '" + sCol + "' element."


        # here's the embedded content
        sCol = "tests/test[" + str(i) + "]/action"

        if sAction is not None:
            sHTML += DrawDropZone(sStepID, sAction, sFunction, sCol, "Action:<br />", True)
        else:
            sHTML += "ERROR: Malformed XML for Step ID [" + sStepID + "].  Missing '" + sCol + "' element."


        if i != 1:
            sHTML += "</div>"

        i += i

    sHTML += "</div>"


    # draw an add link.  The rest will happen on the client.
    sHTML += "<div class=\"fn_if_add_btn pointer\" add_to_id=\"if_" + sStepID + "_conditions\" step_id=\"" + sStepID + "\" next_index=\"" + str(i) + "\"><img style=\"width:10px; height:10px;\" src=\"static/images/icons/edit_add.png\" alt=\"\" title=\"Add another Else If section.\" />( click to add another 'Else If' section )</div>"


    sHTML += "<div id=\"if_" + sStepID + "_else\" class=\"fn_if_else_section\">"

    # the final 'else' area
    sElse = xd.findtext("else", "")
    if sElse is not None:
        sHTML += "<span class=\"fn_if_removeelse_btn pointer\" step_id=\"" + sStepID + "\">" \
           "<img style=\"width:10px; height:10px;\" src=\"static/images/icons/fileclose.png\" alt=\"\" title=\"Remove this Else condition.\" /></span> "
        sHTML += "Else (no 'If' conditions matched):"
        sHTML += DrawDropZone(sStepID, sElse, sFunction, "else", "", True)
    else:
        # draw an add link.  The rest will happen on the client.
        sHTML += "<div class=\"fn_if_addelse_btn pointer\" add_to_id=\"if_" + sStepID + "_else\" step_id=\"" + sStepID + "\"><img style=\"width:10px; height:10px;\" src=\"static/images/icons/edit_add.png\" alt=\"\" title=\"Add an Else section.\" />( click to add a final 'Else' section )</div>"

    sHTML += "</div>"

    return sHTML
