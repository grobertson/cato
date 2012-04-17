import uiCommon
from uiCommon import log
import uiGlobals
import taskCommands
from catocommon import catocommon
import xml.etree.ElementTree as ET

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
            sHTML = "Not Yet Available" #NewConnection(oStep)
        elif sFunction.lower() == "if":
            sHTML = "Not Yet Available" #If(oStep)
        elif sFunction.lower() == "loop":
            sHTML = "Not Yet Available" #Loop(oStep)
        elif sFunction.lower() == "while":
            sHTML = "Not Yet Available" #While(oStep)
        elif sFunction.lower() == "sql_exec":
            sHTML = "Not Yet Available" #SqlExec(oStep)
        elif sFunction.lower() == "set_variable":
            sHTML = "Not Yet Available" #SetVariable(oStep)
        elif sFunction.lower() == "clear_variable":
            sHTML = "Not Yet Available" #ClearVariable(oStep)
        elif sFunction.lower() == "wait_for_tasks":
            sHTML = "Not Yet Available" #WaitForTasks(oStep)
        elif sFunction.lower() == "dataset":
            sHTML = "Not Yet Available" #Dataset(oStep)
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
                sNodeHTML, sNodeOptionHTML = DrawNode(xe, xe.tag, sStepID, sFunction)
                sHTML += sNodeHTML
                sOptionHTML += sNodeOptionHTML
                
        return sHTML, sOptionHTML
    
def DrawNode(xeNode, sXPath, sStepID, sFunction):
        sHTML = ""
        sNodeName = xeNode.tag
        log("Drawing [" + sNodeName + "]", 4)

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
                    sHTML += "<img style=\"width:10px; height:10px; margin-right: 4px;\" src=\"../images/icons/fileclose.png\" alt=\"\" title=\"Remove\" /></span>"
            else: #there is more than one child... business as usual
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
                        "<img style=\"width:10px; height:10px;\" src=\"../images/icons/edit_add.png\"" \
                        " alt=\"\" title=\"Add another...\" /></div>"
   
                #BUT, if this nodes PARENT is editable, that means THIS NODE can be deleted.
                #so, it gets a delete link
                #you can't remove unless there are more than one
                if bIsRemovable:
                    sHTML += "<span class=\"fn_nodearray_remove_btn pointer\" xpath_to_delete=\"" + sXPath + "\" step_id=\"" + sStepID + "\">"
                    sHTML += "<img style=\"width:10px; height:10px;\" src=\"../images/icons/fileclose.png\" alt=\"\" title=\"Remove\" /></span>"
                sHTML += "</div>" #end step header icons
                sHTML += "  </div>" #end header

                for xeChildNode in xeNode:
                    sChildNodeName = xeChildNode.tag
                    sChildXPath = sXPath + "/" + sChildNodeName

                    """
                    #here's the magic... are there any children nodes here with the SAME NAME?
                    #if so they need an index on the xpath
                    if xeNode.XPathSelectElements(sChildNodeName).Count() > 1:
                        #since the document won't necessarily be in perfect order,
                        #we need to keep track of same named nodes and their indexes.
                        #so, stick each array node up in a lookup table.
                        #is it already in my lookup table?
                        iLastIndex = 0
                        dictNodes.TryGetValue(sChildNodeName, )
                        if iLastIndex == 0:
                            #not there, add it
                            iLastIndex = 1
                            dictNodes.Add(sChildNodeName, iLastIndex)
                        else:
                            #there, increment it and set it
                            iLastIndex += 1
                            dictNodes[sChildNodeName] = iLastIndex
                        sChildXPath = sChildXPath + "[" + iLastIndex + "]"
                    sHTML += self.DrawNode(xeChildNode, sChildXPath, sStepID, sFunction, )
                    """

                sHTML += "</div>"
        else: #end section
            sHTML += DrawField(xeNode, sXPath, sStepID, sFunction)
            #it may be that these fields themselves are removable
            if bIsRemovable:
                sHTML += "<span class=\"fn_nodearray_remove_btn pointer\" xpath_to_delete=\"" + sXPath + "\" step_id=\"" + sStepID + "\">"
                sHTML += "<img style=\"width:10px; height:10px; margin-right: 4px;\" src=\"../images/icons/fileclose.png\" alt=\"\" title=\"Remove\" /></span>"
        
        #ok, now that we've drawn it, it might be intended to go on the "options tab".
        #if so, stick it there
        if sOptionTab:
            return "", sHTML
        else:
            return sHTML, ""
        
def DrawField(xe, sXPath, sStepID, sFunction):
        sHTML = ""
        sNodeValue = (xe.text if xe.text else "")
        log("-- Value :" + sNodeValue, 4)
        
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

        log("-- Input Type :" + sInputType, 4)


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
            sHTML += "##DROPDOWN##"
            """
            #the data source of a drop down can be a) an xml file, b) an internal function or web method or c) an "local" inline list
            #there is no "default" datasource... if nothing is available, it draws an empty picker
            sDatasource = xe.get("datasource", "")
            sDataSet = xe.get("dataset", "")
            sFieldStyle = xe.get("style", "")
            sHTML += sNodeLabel + " <select " + self.CommonAttribs(sStepID, sFunction, False, sXPath, sFieldStyle) + ">"
            #empty one
            sHTML += "<option " + self.SetOption("", sNodeValue) + " value=\"\"></option>"
            #if it's a combo, it's possible we may have a value that isn't actually in the list.
            #but we will need to add it to the list otherwise we can't select it!
            #so, first let's keep track of if we find the value anywhere in the various datasets.
            bValueWasInData = False
            if sDatasource == "file":
                try:
                    #sDataset is an XML file name.
                    #sTable is the parent node in the XML containing the data
                    sTable = xe.get("table", "")
                    sValueNode = xe.get("valuenode", "")
                    if sTable == "" or sValueNode == "":
                        return "Unable to render input element - missing required attribute 'table' or 'valuenode'."
                    ds = DataSet()
                    ds.ReadXml(Server.MapPath("~/pages/" + sDataSet))
                    if ds.Tables[sTable].Rows.Count > 0:
                        enumerator = ds.Tables[sTable].Rows.GetEnumerator()
                        while enumerator.MoveNext():
                            dr = enumerator.Current
                            sVal = dr[sValueNode]
                            sHTML += "<option " + self.SetOption(sVal, sNodeValue) + " value=\"" + sVal + "\">" + sVal + "</option>"
                            if sVal.Equals(sNodeValue):
                                bValueWasInData = True
                except Exception, ex:
                    return "Unable to render input element [" + sXPath + "]. Lookup file [" + sDataSet + "] not found or incorrect format." + ex.Message
                finally:
            elif sDatasource == "function":
                #this uses reflection to execute the function specified in the sDataSet property
                #at this time, the function must exist in this namespace!
                #since it's populating a dropdown, we expect the function to return a dictionary
                data = Dictionary[str, str]()
                info = self.GetType().GetMethod(sDataSet, BindingFlags.NonPublic | BindingFlags.Instance)
                if info != None:
                    data = info.Invoke(self, None)
                    if data != None:
                        enumerator = data.GetEnumerator()
                        while enumerator.MoveNext():
                            pair = enumerator.Current
                            sHTML += "<option " + self.SetOption(pair.Key, sNodeValue) + " value=\"" + pair.Key + "\">" + pair + "</option>"
                            if pair.Key.Equals(sNodeValue):
                                bValueWasInData = True
            else: #default is "local"
                #data is pipe delimited
                aValues = sDataSet.Split('|')
                enumerator = aValues.GetEnumerator()
                while enumerator.MoveNext():
                    sVal = enumerator.Current
                    sHTML += "<option " + self.SetOption(sVal, sNodeValue) + " value=\"" + sVal + "\">" + sVal + "</option>"
                    if sVal.Equals(sNodeValue):
                        bValueWasInData = True
            #NOTE: If it has the "combo" style and a value, that means we're allowing the user to enter a value that may not be 
            #in the dataset.  If that's the case, we must add the actual saved value to the list too. 
            if not bValueWasInData: #we didn't find it in the data ...
                if sFieldStyle.Contains("combo") and not str.IsNullOrEmpty(sNodeValue): #and it's a combo and not empty 
                    sHTML += "<option " + self.SetOption(sNodeValue, sNodeValue) + " value=\"" + sNodeValue + "\">" + sNodeValue + "</option>"
            sHTML += "</select>"
            """
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
