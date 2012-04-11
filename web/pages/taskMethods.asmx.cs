//Copyright 2011 Cloud Sidekick
// 
//Licensed under the Apache License, Version 2.0 (the "License");
//you may not use this file except in compliance with the License.
//You may obtain a copy of the License at
// 
//    http://www.apache.org/licenses/LICENSE-2.0
// 
//Unless required by applicable law or agreed to in writing, software
//distributed under the License is distributed on an "AS IS" BASIS,
//WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//See the License for the specific language governing permissions and
//limitations under the License.
//
using System;
using System.Collections;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Web.Services;
using System.Xml.Linq;
using System.Xml.XPath;
using System.IO;
using Globals;

namespace ACWebMethods
{
    /// <summary>
    /// taskMethods: web methods specifically for Task related operations.
    /// Just to keep uiMethods from becoming so huge.
    /// </summary>
    [WebService(Namespace = "ACWebMethods")]
    [WebServiceBinding(ConformsTo = WsiProfiles.BasicProfile1_1)]
    [System.ComponentModel.ToolboxItem(false)]
    // To allow this Web Service to be called from script, using ASP.NET AJAX, uncomment the following line. 
    [System.Web.Script.Services.ScriptService]

	public class taskMethods : System.Web.Services.WebService
    {

        #region "Steps"
		[WebMethod(EnableSession = true)]
        public string wmGetCodeblocks(string sTaskID)
        {
            try
            {
				acUI.acUI ui = new acUI.acUI();
				string sErr = "";
				//instantiate the new Task object
				Task oTask = new Task(sTaskID, false, ref sErr);
				if (oTask == null)
                    return "{\"error\" : \"wmGetCodeblocks: Unable to get Task for ID [" + sTaskID + "]. " + sErr + "\"}";

				string sCBHTML = "";
				
				foreach (Codeblock cb in oTask.Codeblocks.Values)
				{
					//if it's a guid it's a bogus codeblock (for export only)
					if (ui.IsGUID(cb.Name))
						continue;

					sCBHTML += "<li class=\"ui-widget-content codeblock\" id=\"cb_" + cb.Name + "\">";
					sCBHTML += "<div>";
					sCBHTML += "<div class=\"codeblock_title\" name=\"" + cb.Name + "\">";
					sCBHTML += "<span>" + cb.Name + "</span>";
					sCBHTML += "</div>";
					sCBHTML += "<div class=\"codeblock_icons pointer\">";
					sCBHTML += "<span id=\"codeblock_rename_btn_" + cb.Name + "\">";
					sCBHTML += "<img class=\"codeblock_rename\" codeblock_name=\"" + cb.Name + "\"";
					sCBHTML += " src=\"../images/icons/edit_16.png\" alt=\"\" /></span><span class=\"codeblock_copy_btn\"";
					sCBHTML += " codeblock_name=\"" + cb.Name + "\">";
					sCBHTML += "<img src=\"../images/icons/editcopy_16.png\" alt=\"\" /></span><span id=\"codeblock_delete_btn_" + cb.Name + "\"";
					sCBHTML += " class=\"codeblock_delete_btn codeblock_icon_delete\" remove_id=\"" + cb.Name + "\">";
					sCBHTML += "<img src=\"../images/icons/fileclose.png\" alt=\"\" /></span>";
					sCBHTML += "</div>";
					sCBHTML += "</div>";
					sCBHTML += "</li>";
				}
				return sCBHTML;
            }
            catch (Exception ex)
            {
                return "{\"error\" : \"" + ex.Message + "\"}";
            }
        }

		[WebMethod(EnableSession = true)]
        public void wmAddCodeblock(string sTaskID, string sNewCodeblockName)
        {
            dataAccess dc = new dataAccess();
            acUI.acUI ui = new acUI.acUI();

			try
            {
                string sErr = "";
                string sSQL = "";

                if (sNewCodeblockName != "")
                {
                    sSQL = "insert into task_codeblock (task_id, codeblock_name)" +
                           " values (" + "'" + sTaskID + "'," +
                           "'" + sNewCodeblockName + "'" +
                           ")";

                    if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                        throw new Exception("Unable to add Codeblock [" + sNewCodeblockName + "]. " + sErr);

					ui.WriteObjectChangeLog(Globals.acObjectTypes.Task, sTaskID, sNewCodeblockName,
					                        "Added Codeblock.");

				}
                else
                {
					throw new Exception("Unable to add Codeblock. Invalid or missing Codeblock Name.");
                }
            }
            catch (Exception ex)
            {
				throw new Exception("Unable to add Codeblock. " + ex.Message);
            }
        }

		[WebMethod(EnableSession = true)]
        public void wmDeleteCodeblock(string sTaskID, string sCodeblockID)
        {
            try
            {
                string sErr = "";

                dataAccess.acTransaction oTrans = new dataAccess.acTransaction(ref sErr);
				acUI.acUI ui = new acUI.acUI();

                //first, delete any steps that are embedded content on steps in this codeblock
                //(because embedded steps have their parent step_id as the codeblock name.)
                oTrans.Command.CommandText = "delete em from task_step em" +
                    " join task_step p on em.task_id = p.task_id" +
                    " and em.codeblock_name = p.step_id" +
                    " where p.task_id = '" + sTaskID + "'" +
                    " and p.codeblock_name = '" + sCodeblockID + "'";
                if (!oTrans.ExecUpdate(ref sErr))
					throw new Exception("Unable to delete embedded Steps from Codeblock." + sErr);

                oTrans.Command.CommandText = "delete u from task_step_user_settings u" +
                    " join task_step ts on u.step_id = ts.step_id" +
                    " where ts.task_id = '" + sTaskID + "'" +
                    " and ts.codeblock_name = '" + sCodeblockID + "'";
                if (!oTrans.ExecUpdate(ref sErr))
					throw new Exception("Unable to delete Steps user settings for Steps in Codeblock." + sErr);

                oTrans.Command.CommandText = "delete from task_step" +
                    " where task_id = '" + sTaskID + "'" +
                    " and codeblock_name = '" + sCodeblockID + "'";
                if (!oTrans.ExecUpdate(ref sErr))
					throw new Exception("Unable to delete Steps from Codeblock." + sErr);

                oTrans.Command.CommandText = "delete from task_codeblock" +
                    " where task_id = '" + sTaskID + "'" +
                    " and codeblock_name = '" + sCodeblockID + "'";
                if (!oTrans.ExecUpdate(ref sErr))
					throw new Exception("Unable to delete Codeblock." + sErr);

                oTrans.Commit();

				ui.WriteObjectChangeLog(Globals.acObjectTypes.Task, sTaskID, sCodeblockID,
				                        "Deleted Codeblock.");

            }
            catch (Exception ex)
            {
                throw new Exception("Exception: " + ex.Message);
            }
        }

		[WebMethod(EnableSession = true)]
        public string wmUpdateStep(string sStepID, string sFunction, string sXPath, string sValue)
        {
            dataAccess dc = new dataAccess();
            acUI.acUI ui = new acUI.acUI();
            string sErr = "";
            string sSQL = "";

            //we encoded this in javascript before the ajax call.
            //the safest way to unencode it is to use the same javascript lib.
            //(sometimes the javascript and .net libs don't translate exactly, google it.)
            sValue = ui.unpackJSON(sValue);

            //if the function type is "_common" that means this is a literal column on the step table.
            if (sFunction == "_common")
            {
                sValue = ui.TickSlash(sValue); //escape single quotes for the SQL insert
                sSQL = "update task_step set " +
                    sXPath + " = '" + sValue + "'" +
                    " where step_id = '" + sStepID + "';";

                if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                {
                    throw new Exception(sErr);
                }

            }
            else
            {
                //XML processing
                //get the xml from the step table and update it
                string sXMLTemplate = "";

                sSQL = "select function_xml from task_step where step_id = '" + sStepID + "'";

                if (!dc.sqlGetSingleString(ref sXMLTemplate, sSQL, ref sErr))
                {
                    throw new Exception("Unable to get XML data for step [" + sStepID + "].");
                }

                XDocument xDoc = XDocument.Parse(sXMLTemplate);
                if (xDoc == null)
                    throw new Exception("XML data for step [" + sStepID + "] is invalid.");

                XElement xRoot = xDoc.Element("function");
                if (xRoot == null)
                    throw new Exception("XML data for step [" + sStepID + "] does not contain 'function' root node.");

                try
                {
                    XElement xNode = xRoot.XPathSelectElement(sXPath);
                    if (xNode == null)
                        throw new Exception("XML data for step [" + sStepID + "] does not contain '" + sXPath + "' node.");

                    xNode.SetValue(sValue);
                }
                catch (Exception)
                {
                    try
                    {
                        //here's the deal... given an XPath statement, we simply cannot add a new node if it doesn't exist.
                        //why?  because xpath is a query language.  It doesnt' describe exactly what to add due to wildcards and //foo syntax.

                        //but, what we can do is make an assumption in our specific case... 
                        //that we are only wanting to add because we changed an underlying command XML template, and there are existing commands.

                        //so... we will split the xpath into segments, and traverse upward until we find an actual node.
                        //once we have it, we will need to add elements back down.

                        //string[] nodes = sXPath.Split('/');

                        //foreach (string node in nodes)
                        //{
                        //    //try to select THIS one, and stick it on the backwards stack
                        //    XElement xNode = xRoot.XPathSelectElement("//" + node);
                        //    if (xNode == null)
                        //        throw new Exception("XML data for step [" + sStepID + "] does not contain '" + sXPath + "' node.");

                        //}

                        XElement xFoundNode = null;
                        ArrayList aMissingNodes = new ArrayList();

                        //if there are no slashes we'll just add this one explicitly as a child of root
						if (sXPath.IndexOf("/") == -1) {
							xRoot.Add(new XElement(sXPath));
						}
						else {
							//and if there are break it down
							string sWorkXPath = sXPath;
	                        while (sWorkXPath.LastIndexOf("/") > -1)
	                        {
	                            aMissingNodes.Add(sWorkXPath.Substring(sWorkXPath.LastIndexOf("/") + 1));
	                            sWorkXPath = sWorkXPath.Substring(0, sWorkXPath.LastIndexOf("/"));
	
	                            xFoundNode = xRoot.XPathSelectElement(sWorkXPath);
	                            if (xFoundNode != null)
	                            {
	                                //Found one! stop looping
	                                break;
	                            }
	                        }

							//now that we know where to start (xFoundNode), we can use that as a basis for adding
	                        foreach (string sNode in aMissingNodes)
	                        {
	                            xFoundNode.Add(new XElement(sNode));
	                        }
						}

                        //now we should be good to stick the value on the final node.
                        XElement xNode = xRoot.XPathSelectElement(sXPath);
                        if (xNode == null)
                            throw new Exception("XML data for step [" + sStepID + "] does not contain '" + sXPath + "' node.");

                        xNode.SetValue(sValue);

                        //xRoot.Add(new XElement(sXPath, sValue));
                        //xRoot.SetElementValue(sXPath, sValue);
                    }
                    catch (Exception)
                    {
                        throw new Exception("Error Saving Step [" + sStepID + "].  Could not find and cannot create the [" + sXPath + "] property in the XML.");
                    }

                }


                sSQL = "update task_step set " +
                    " function_xml = '" + ui.TickSlash(xDoc.ToString(SaveOptions.DisableFormatting)) + "'" +
                    " where step_id = '" + sStepID + "';";

                if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                {
                    throw new Exception(sErr);
                }

            }

            sSQL = "select task_id, codeblock_name, step_order from task_step where step_id = '" + sStepID + "'";
            DataRow dr = null;
            if (!dc.sqlGetDataRow(ref dr, sSQL, ref sErr))
                throw new Exception(sErr);

            if (dr != null)
            {
                ui.WriteObjectChangeLog(Globals.acObjectTypes.Task, dr["task_id"].ToString(), sFunction,
                    "Codeblock:" + dr["codeblock_name"].ToString() +
                    " Step Order:" + dr["step_order"].ToString() +
                    " Command Type:" + sFunction +
                    " Property:" + sXPath +
                    " New Value: " + sValue);
            }

            return "";
        }

        [WebMethod(EnableSession = true)]
        public void wmDeleteStep(string sStepID)
        {
            dataAccess dc = new dataAccess();
            acUI.acUI ui = new acUI.acUI();

            try
            {
                string sErr = "";
                string sSQL = "";

                dataAccess.acTransaction oTrans = new dataAccess.acTransaction(ref sErr);

                //you have to know which one we are removing
                string sDeletedStepOrder = "0";
                string sTaskID = "";
                string sCodeblock = "";
                string sFunction = "";
                string sFunctionXML = "";

                sSQL = "select task_id, codeblock_name, step_order, function_name, function_xml" +
                    " from task_step where step_id = '" + sStepID + "'";

                DataRow dr = null;
                if (!dc.sqlGetDataRow(ref dr, sSQL, ref sErr)) {
					oTrans.RollBack();
					throw new Exception("Unable to get details for step." + sErr);
				}
                if (dr != null)
                {
                    sDeletedStepOrder = dr["step_order"].ToString();
                    sTaskID = dr["task_id"].ToString();
                    sCodeblock = dr["codeblock_name"].ToString();
                    sFunction = dr["function_name"].ToString();
                    sFunctionXML = dr["function_xml"].ToString();

                    //for logging, we'll stick the whole command XML into the log
                    //so we have a complete record of the step that was just deleted.
                    ui.WriteObjectDeleteLog(Globals.acObjectTypes.Task, sTaskID, sFunction,
                        "Codeblock:" + sCodeblock +
                        " Step Order:" + sDeletedStepOrder +
                        " Command Type:" + sFunction +
                        " Details:" + sFunctionXML);
                }

                //"embedded" steps have a codeblock name referencing their "parent" step.
                //if we're deleting a parent, whack all the children
                sSQL = "delete from task_step where codeblock_name = '" + sStepID + "'";
                oTrans.Command.CommandText = sSQL;
                if (!oTrans.ExecUpdate(ref sErr))
                    throw new Exception("Unable to delete step." + sErr);

                //step might have user_settings
                sSQL = "delete from task_step_user_settings where step_id = '" + sStepID + "'";
                oTrans.Command.CommandText = sSQL;
                if (!oTrans.ExecUpdate(ref sErr))
                    throw new Exception("Unable to delete step user settings." + sErr);

                //now whack the parent
                sSQL = "delete from task_step where step_id = '" + sStepID + "'";
                oTrans.Command.CommandText = sSQL;
                if (!oTrans.ExecUpdate(ref sErr))
                    throw new Exception("Unable to delete step." + sErr);


                sSQL = "update task_step set step_order = step_order - 1" +
                    " where task_id = '" + sTaskID + "'" +
                    " and codeblock_name = '" + sCodeblock + "'" +
                    " and step_order > " + sDeletedStepOrder;
                oTrans.Command.CommandText = sSQL;
                if (!oTrans.ExecUpdate(ref sErr))
                    throw new Exception("Unable to reorder steps after deletion." + sErr);

                oTrans.Commit();

            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public string wmReorderSteps(string sSteps)
        {
            dataAccess dc = new dataAccess();

            try
            {
                int i = 0;

                string[] aSteps = sSteps.Split(',');
                for (i = 0; i <= aSteps.Length - 1; i++)
                {
                    string sErr = "";
                    string sSQL = "update task_step" +
                            " set step_order = " + (i + 1) +
                            " where step_id = '" + aSteps[i] + "'";

                    //there will be no sSQL if there were no steps, so just skip it.
                    if (!string.IsNullOrEmpty(sSQL))
                    {
                        if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                        {
                            throw new Exception("Unable to update steps." + sErr);
                        }
                    }
                }

                //System.Threading.Thread.Sleep(2000);
                return "";
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public string wmAddStep(string sTaskID, string sCodeblockName, string sItem)
        {
            dataAccess dc = new dataAccess();
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
            acUI.acUI ui = new acUI.acUI();

            try
            {
                string sUserID = ui.GetSessionUserID();

                string sStepHTML = "";
                string sErr = "";
                string sSQL = "";
                string sNewStepID = "";
				
				//in some cases, we'll have some special values to go ahead and set in the function_xml
				//when it's added
				//it's content will be xpath, value
				Dictionary<string, string> dValues = new Dictionary<string, string>();

                if (!ui.IsGUID(sTaskID))
                    throw new Exception("Unable to add step. Invalid or missing Task ID. [" + sTaskID + "]" + sErr);


                //now, the sItem variable may have a function name (if it's a new command)
                //or it may have a guid (if it's from the clipboard)

                //so, if it's a guid after stripping off the prefix, it's from the clipboard

                //the function has a fn_ or clip_ prefix on it from the HTML.  Strip it off.
                //FIX... test the string to see if it BEGINS with fn_ or clip_
                //IF SO... cut off the beginning... NOT a replace operation.
				if (sItem.StartsWith("fn_")) sItem = sItem.Remove(0, 3);
                if (sItem.StartsWith("clip_")) sItem = sItem.Remove(0, 5);

				//could also beging with cb_, which means a codeblock was dragged and dropped.
				//this special case will result in a codeblock command.
				if (sItem.StartsWith("cb_")) {
					//so, the sItem becomes "codeblock"
					string sCBName = sItem.Remove(0, 3);
					dValues.Add("//codeblock", sCBName);
					sItem = "codeblock";
				}
                //NOTE: !! yes we are adding the step with an order of -1
                //the update event on the client does not know the index at which it was dropped.
                //so, we have to insert it first to get the HTML... but the very next step
                //will serialize and update the entire sortable... 
                //immediately replacing this -1 with the correct position

                if (ui.IsGUID(sItem))
                {
                    sNewStepID = sItem;

                    //copy from the clipboard (using the root_step_id to get ALL associated steps)
                    sSQL = "insert into task_step (step_id, task_id, codeblock_name, step_order, step_desc," +
                        " commented, locked, output_parse_type, output_row_delimiter, output_column_delimiter," +
                        " function_name, function_xml, variable_xml)" +
                        " select step_id, '" + sTaskID + "'," +
                        " case when codeblock_name is null then '" + sCodeblockName + "' else codeblock_name end," +
                        "-1,step_desc," +
                        "0,0,output_parse_type,output_row_delimiter,output_column_delimiter," +
                        "function_name,function_xml,variable_xml" +
                        " from task_step_clipboard" +
                        " where user_id = '" + sUserID + "'" +
                        " and root_step_id = '" + sItem + "'";

                    if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                        throw new Exception("Unable to add step." + sErr);

                    ui.WriteObjectChangeLog(Globals.acObjectTypes.Task, sTaskID, sItem,
                        "Added Command from Clipboard to Codeblock:" + sCodeblockName);
                }
                else
                {
					//THE NEW CLASS CENTRIC WAY
					//1) Get a Function object for the sItem (function_name)
					//2) use those values to construct an insert statement
					
					Function func = Function.GetFunctionByName(sItem);
					if (func == null)
						throw new Exception("Unable to add step.  Can't find a Function definition for [" + sItem + "]");
					
					//add a new command
                    sNewStepID = ui.NewGUID();

                    //NOTE: !! yes we are doing some command specific logic here.
                    //Certain commands have different 'default' values for delimiters, etc.
                    //sOPM: 0=none, 1=delimited, 2=parsed
                    string sOPM = "0";

					//gotta do a few things to the templatexml
					XDocument xdTemplate = XDocument.Parse(func.TemplateXML);
					if (xdTemplate != null) {
						if (xdTemplate.XPathSelectElement("//function") != null)
						{
							XElement xe = xdTemplate.XPathSelectElement("//function");
							if (xe != null) {
								//get the OPM
								sOPM = (xe.Attribute("parse_method") == null ? "0" : xe.Attribute("parse_method").Value);
								//it's possible that variables=true and parse_method=0..
								//(don't know why you'd do that on purpose, but whatever.)
								//but if there's NO parse method attribute, and yet there is a 'variables=true' attribute
								//well, we can't let the absence of a parse_method negate it,
								//so the default is "2".
								if (xe.Attribute("variables") != null)
									if (dc.IsTrue(xe.Attribute("variables").Value) && sOPM == "0")
										sOPM = "2";
								
								
								//there may be some provided values ... so alter the func.TemplateXML accordingly
								foreach (string sXPath in dValues.Keys) {
									XElement xNode = xe.XPathSelectElement(sXPath);
									if (xNode != null) {
										xNode.SetValue(dValues[sXPath]);
									}
								}
							}
						}
					}
					
					sSQL = "insert into task_step (step_id, task_id, codeblock_name, step_order," +
						" commented, locked, output_parse_type, output_row_delimiter, output_column_delimiter," +
						" function_name, function_xml)" +
						" values (" +
						"'" + sNewStepID + "'," +
						"'" + sTaskID + "'," +
						(string.IsNullOrEmpty(sCodeblockName) ? "NULL" : "'" + sCodeblockName + "'") + "," +
						"-1," +
						"0,0," + sOPM + ",0,0," +
						"'" + func.Name + "'," +
						"'" + xdTemplate.ToString(SaveOptions.DisableFormatting) + "'" +
						")";

                    if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                        throw new Exception("Unable to add step." + sErr);

                    ui.WriteObjectChangeLog(Globals.acObjectTypes.Task, sTaskID, sItem,
                        "Added Command Type:" + sItem + " to Codeblock:" + sCodeblockName);
                }

                if (!string.IsNullOrEmpty(sNewStepID))
                {
                    //now... get the newly inserted step and draw it's HTML
                    Step oNewStep = ft.GetSingleStep(sNewStepID, sUserID, ref sErr);
                    if (oNewStep != null && sErr == "")
                        sStepHTML += ft.DrawFullStep(oNewStep);
                    else
                        sStepHTML += "<span class=\"red_text\">" + sErr + "</span>";

                    //return the html
                    return sNewStepID + sStepHTML;
                }
                else
                {
                    throw new Exception("Unable to add step.  No new step_id." + sErr);
                }
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public string wmGetSteps(string sTaskID, string sCodeblockName)
        {
			FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
			
			//so, for this change our jquery will need to set the StepSectionTitle with the new codeblock name
			//and update a div with the complete steps document
            string sErr = "";
            string sHTML = "";
			
			try
            {
				//instantiate the new Task object
				Task oTask = new Task(sTaskID, true, ref sErr);
				
				if (oTask == null)
                    return "{\"error\" : \"wmGetSteps: Unable to get Task for ID [" + sTaskID + "].\"}";
				
                //if the codeblock is empty, die.
                if (string.IsNullOrEmpty(sCodeblockName))
                    return "{\"error\" : \"No Codeblock specified for wmGetSteps.\"}";

				//set the text of the step 'add' message...
	            string sAddHelpMsg =  "No Commands have been defined in this Codeblock. Drag a Command here to add it.";
	
	            if (oTask.Codeblocks[sCodeblockName].Steps.Count > 0)
	            {
	                //we always need the no_step item to be there, we just hide it if we have other items
	                //it will get unhidden if someone deletes the last step.
	                sHTML = "<li id=\"no_step\" class=\"ui-widget-content ui-corner-all ui-state-active ui-droppable no_step hidden\">" + sAddHelpMsg + "</li>";
	
	                foreach (Step oStep in oTask.Codeblocks[sCodeblockName].Steps.Values)
	                {
						sHTML += ft.DrawFullStep(oStep);
	                }
	            }
	            else
	            {
	                sHTML = "<li id=\"no_step\" class=\"ui-widget-content ui-corner-all ui-state-active ui-droppable no_step\">" + sAddHelpMsg + "</li>";
	            }
	            return sHTML;

            }
            catch (Exception ex)
            {
				return "{\"error\" : \"" + ex.Message + "\"}";
			}
        }
		
        [WebMethod(EnableSession = true)]
        public string wmGetStep(string sStepID)
        {
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
            acUI.acUI ui = new acUI.acUI();

            try
            {

                string sStepHTML = "";
                string sErr = "";

                if (!ui.IsGUID(sStepID))
                    throw new Exception("Unable to get step. Invalid or missing Step ID. [" + sStepID + "]" + sErr);

                string sUserID = ui.GetSessionUserID();

                Step oStep = ft.GetSingleStep(sStepID, sUserID, ref sErr);
                if (oStep != null && sErr == "")
                {
                    //embedded steps...
                    //if the step_order is -1 and the codeblock_name is a guid, this step is embedded 
                    //within another step
                    if (oStep.Order == -1 && ui.IsGUID(oStep.Codeblock))
                        sStepHTML += ft.DrawEmbeddedStep(oStep);
                    else
                        sStepHTML += ft.DrawFullStep(oStep);
                }
                else
                    sStepHTML += "<span class=\"red_text\">" + sErr + "</span>";

                //return the html
                return sStepHTML;
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public void wmToggleStep(string sStepID, string sVisible)
        {
            dataAccess dc = new dataAccess();
            acUI.acUI ui = new acUI.acUI();

            sVisible = (sVisible == "1" ? "1" : "0");

            try
            {
                if (ui.IsGUID(sStepID))
                {
                    string sErr = "";
                    dataAccess.acTransaction oTrans = new dataAccess.acTransaction(ref sErr);

                    string sUserID = ui.GetSessionUserID();

                    //is there a row?
                    int iRowCount = 0;
                    dc.sqlGetSingleInteger(ref iRowCount, "select count(*) from task_step_user_settings" +
                                " where user_id = '" + sUserID + "'" +
                                " and step_id = '" + sStepID + "'", ref sErr);

                    if (iRowCount == 0)
                    {
                        oTrans.Command.CommandText = "insert into task_step_user_settings" +
                            " (user_id, step_id, visible, breakpoint, skip)" +
                            " values ('" + sUserID + "','" + sStepID + "', " + sVisible + ", 0, 0)";

                        if (!oTrans.ExecUpdate(ref sErr))
                            throw new Exception("Unable to toggle step (0) [" + sStepID + "]." + sErr);
                    }
                    else
                    {
                        oTrans.Command.CommandText = " update task_step_user_settings set visible = '" + sVisible + "'" +
                            " where step_id = '" + sStepID + "'";
                        if (!oTrans.ExecUpdate(ref sErr))
                            throw new Exception("Unable to toggle step (1) [" + sStepID + "]." + sErr);
                    }


                    oTrans.Commit();

                    return;
                }
                else
                {
                    throw new Exception("Unable to toggle step. Missing or invalid step_id.");
                }

            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public void wmToggleStepCommonSection(string sStepID, string sButton)
        {
            dataAccess dc = new dataAccess();

            acUI.acUI ui = new acUI.acUI();

            try
            {
                if (ui.IsGUID(sStepID))
                {
                    string sUserID = ui.GetSessionUserID();

                    sButton = (sButton == "" ? "null" : "'" + sButton + "'");

                    string sErr = "";

                    //is there a row?
                    int iRowCount = 0;
                    dc.sqlGetSingleInteger(ref iRowCount, "select count(*) from task_step_user_settings" +
                                " where user_id = '" + sUserID + "'" +
                                " and step_id = '" + sStepID + "'", ref sErr);

                    if (iRowCount == 0)
                    {
                        string sSQL = "insert into task_step_user_settings" +
                            " (user_id, step_id, visible, breakpoint, skip, button)" +
                            " values ('" + sUserID + "','" + sStepID + "', 1, 0, 0, " + sButton + ")";
                        if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                            throw new Exception("Unable to toggle step button (0) [" + sStepID + "]." + sErr);
                    }
                    else
                    {
                        string sSQL = " update task_step_user_settings set button = " + sButton +
                            " where step_id = '" + sStepID + "';";
                        if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                            throw new Exception("Unable to toggle step button (1) [" + sStepID + "]." + sErr);
                    }


                    return;
                }
                else
                {
                    throw new Exception("Unable to toggle step button. Missing or invalid step_id or button.");
                }

            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public void wmCopyCodeblockStepsToClipboard(string sTaskID, string sCodeblockName)
        {
            dataAccess dc = new dataAccess();

            try
            {
                if (sCodeblockName != "")
                {
                    string sErr = "";
                    string sSQL = "select step_id" +
                        " from task_step" +
                        " where task_id = '" + sTaskID + "'" +
                        " and codeblock_name = '" + sCodeblockName + "'" +
                        " order by step_order desc";

                    DataTable dt = new DataTable();
                    if (!dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
                        throw new Exception(sErr);

                    foreach (DataRow dr in dt.Rows)
                    {
                        wmCopyStepToClipboard(dr["step_id"].ToString());
                    }

                    return;
                }
                else
                {
                    throw new Exception("Unable to copy Codeblock. Missing or invalid codeblock_name.");
                }

            }
            catch (Exception ex)
            {
                throw ex;
            }
        }
        [WebMethod(EnableSession = true)]
        public void wmCopyStepToClipboard(string sStepID)
        {
            dataAccess dc = new dataAccess();

            acUI.acUI ui = new acUI.acUI();

            try
            {
                if (ui.IsGUID(sStepID))
                {

                    // should also do this whole thing in a transaction.



                    string sUserID = ui.GetSessionUserID();
                    string sErr = "";

                    //stuff gets new ids when copied into the clpboard.
                    //what way when adding, we don't have to loop
                    //(yes, I know we have to loop here, but adding is already a long process
                    //... so we can better afford to do it here than there.)
                    string sNewStepID = ui.NewGUID();

                    //it's a bit hokey, but if a step already exists in the clipboard, 
                    //and we are copying that step again, 
                    //ALWAYS remove the old one.
                    //we don't want to end up with lots of confusing copies
                    string sSQL = "delete from task_step_clipboard" +
                        " where user_id = '" + sUserID + "'" +
                        " and src_step_id = '" + sStepID + "'";
                    if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                        throw new Exception("Unable to clean clipboard." + sErr);

                    sSQL = " insert into task_step_clipboard" +
                        " (user_id, clip_dt, src_step_id, root_step_id, step_id, function_name, function_xml, step_desc," +
                            " output_parse_type, output_row_delimiter, output_column_delimiter, variable_xml)" +
                        " select '" + sUserID + "', now(), step_id, '" + sNewStepID + "', '" + sNewStepID + "'," +
                            " function_name, function_xml, step_desc," +
                            " output_parse_type, output_row_delimiter, output_column_delimiter, variable_xml" +
                        " from task_step" +
                        " where step_id = '" + sStepID + "'";
                    if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                        throw new Exception("Unable to copy step [" + sStepID + "]." + sErr);


                    //now, if the step we just copied has embedded steps,
                    //we need to get them too, but stick them in the clipboard table
                    //in a hidden fashion. (So they are preserved there, but not visible in the list.)

                    //we are doing it in a recursive call since the nested steps may themselves have nested steps.
                    AlsoCopyEmbeddedStepsToClipboard(sUserID, sStepID, sNewStepID, sNewStepID, ref sErr);

                    return;
                }
                else
                {
                    throw new Exception("Unable to copy step. Missing or invalid step_id.");
                }

            }
            catch (Exception ex)
            {
                throw ex;
            }
        }
        private void AlsoCopyEmbeddedStepsToClipboard(string sUserID, string sSourceStepID, string sRootStepID, string sNewParentStepID, ref string sErr)
        {
            dataAccess dc = new dataAccess();
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
			acUI.acUI ui = new acUI.acUI();
			
            //get all the steps that have the calling stepid as a parent (codeblock)
            string sSQL = "select step_id" +
                " from task_step" +
                " where codeblock_name = '" + sSourceStepID + "'";

            DataTable dt = new DataTable();
            if (!dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
                throw new Exception(sErr);

            foreach (DataRow dr in dt.Rows)
            {
                string sThisStepID = dr["step_id"].ToString();
                string sThisNewID = ui.NewGUID();

                //put them in the table
                sSQL = "delete from task_step_clipboard" +
                    " where user_id = '" + sUserID + "'" +
                    " and src_step_id = '" + sThisStepID + "'";
                if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                    throw new Exception("Unable to clean embedded steps of [" + sSourceStepID + "]." + sErr);
				
				//3-14-2011 NSC - removed the PK from the table, replaced with an index.
				//The only downside to this approach is - first copying an embedded step, then the parent, will remove the 
				//embedded step from the clipboard.
				
                sSQL = " insert into task_step_clipboard" +
                " (user_id, clip_dt, src_step_id, root_step_id, step_id, function_name, function_xml, step_desc," +
                " output_parse_type, output_row_delimiter, output_column_delimiter, variable_xml, codeblock_name)" +
                " select '" + sUserID + "', now(), step_id, '" + sRootStepID + "', '" + sThisNewID + "'," +
                " function_name, function_xml, step_desc," +
                " output_parse_type, output_row_delimiter, output_column_delimiter, variable_xml, '" + sNewParentStepID + "'" +
                " from task_step" +
                " where step_id = '" + sThisStepID + "'";

                if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                    throw new Exception("Unable to copy embedded steps of [" + sSourceStepID + "]." + sErr);


                //we need to update the "action" XML of the parent too...

                /*OK here's the deal..I'm out of time
                 
                 This should not be hardcoded, it should be smart enough to find an XML node with a specific
                 value and update that node.
                 
                 I just don't know enought about xpath to figure it out, and don't have time to do it before
                 I gotta start chilling at tmo.
                 
                 So, I've hardcoded it to the known cases so it will work.
                 
                 Add a new dynamic command type that has embedded steps, and this will probably no longer work.
                 */

                ft.SetNodeValueinXMLColumn("task_step_clipboard", "function_xml", "user_id = '" + sUserID + "'" +
                    " and step_id = '" + sNewParentStepID + "'", "//action[text() = '" + sThisStepID + "']", sThisNewID);

                ft.SetNodeValueinXMLColumn("task_step_clipboard", "function_xml", "user_id = '" + sUserID + "'" +
                    " and step_id = '" + sNewParentStepID + "'", "//else[text() = '" + sThisStepID + "']", sThisNewID);

                ft.SetNodeValueinXMLColumn("task_step_clipboard", "function_xml", "user_id = '" + sUserID + "'" +
                    " and step_id = '" + sNewParentStepID + "'", "//positive_action[text() = '" + sThisStepID + "']", sThisNewID);

                ft.SetNodeValueinXMLColumn("task_step_clipboard", "function_xml", "user_id = '" + sUserID + "'" +
                    " and step_id = '" + sNewParentStepID + "'", "//negative_action[text() = '" + sThisStepID + "']", sThisNewID);

                //END OF HARDCODED HACK


                // and check this one for children too
                AlsoCopyEmbeddedStepsToClipboard(sUserID, sThisStepID, sRootStepID, sThisNewID, ref sErr);
            }
        }

        [WebMethod(EnableSession = true)]
        public void wmRemoveFromClipboard(string sStepID)
        {
            dataAccess dc = new dataAccess();

            acUI.acUI ui = new acUI.acUI();

            try
            {
                string sUserID = ui.GetSessionUserID();
                string sErr = "";

                //if the sStepID is a guid, we are removing just one
                //otherwise, if it's "ALL" we are whacking them all
                if (ui.IsGUID(sStepID))
                {
                    string sSQL = "delete from task_step_clipboard" +
                        " where user_id = '" + sUserID + "'" +
                        " and root_step_id = '" + sStepID + "'";
                    if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                        throw new Exception("Unable to remove step [" + sStepID + "] from clipboard." + sErr);

                    return;
                }
                else if (sStepID == "ALL")
                {
                    string sSQL = "delete from task_step_clipboard where user_id = '" + sUserID + "'";
                    if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                        throw new Exception("Unable to remove step [" + sStepID + "] from clipboard." + sErr);

                    return;
                }
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public string wmGetClips()
        {
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
            acUI.acUI ui = new acUI.acUI();

            try
            {
                string sUserID = ui.GetSessionUserID();
                string sHTML = "";
				
				ClipboardSteps oCSteps = new ClipboardSteps(sUserID);
				if (oCSteps != null)
				{
	                foreach (ClipboardStep cs in oCSteps.Values)
					{
						Function fn = ui.GetTaskFunction(cs.FunctionName);
						if (fn == null)
							return "Error building Clip - Unable to get the details for the Command type '" + cs.FunctionName + "'.";
			
						string sStepID = cs.ID;
						string sLabel = fn.Label;
						string sIcon = fn.Icon;
						string sDesc = ui.GetSnip(cs.Description, 75);
						string sClipDT = cs.ClipDT;
						
						sHTML += "<li" +
							" id=\"clip_" + sStepID + "\"" +
								" name=\"clip_" + sStepID + "\"" +
								" class=\"command_item function clip\"" +
								">";
						
						//a table for the label so the clear icon can right align
						sHTML += "<table width=\"99%\" border=\"0\"><tr>";
						sHTML += "<td width=\"1px\"><img alt=\"\" src=\"../images/" + sIcon + "\" /></td>";
						sHTML += "<td style=\"vertical-align: middle; padding-left: 5px;\">" + sLabel + "</td>";
						sHTML += "<td width=\"1px\" style=\"vertical-align: middle;\">";
						
						//view icon
						//due to the complexity of telling the core routines to look in the clipboard table, it 
						//it not possible to easily show the complex command types
						// without a redesign of how this works.  NSC 4-19-2011
						//due to several reasons, most notable being that the XML node for each of those commands 
						//that contains the step_id is hardcoded and the node names differ.
						//and GetSingleStep requires a step_id which must be mined from the XML.
						//so.... don't show a preview icon for them
						string sFunction = fn.Name;
						
						if (!"loop,exists,if,while".Contains(sFunction))
						{
							sHTML += "<span id=\"btn_view_clip\" view_id=\"v_" + sStepID + "\">" +
								"<img src=\"../images/icons/search.png\" style=\"width: 16px; height: 16px;\" alt=\"\" />" +
									"</span>";
						}
						sHTML += "</td></tr>";
						
						sHTML += "<tr><td>&nbsp;</td><td><span class=\"code\">" + sClipDT + "</span></td>";
						sHTML += "<td>";
						//delete icon
						sHTML += "<span id=\"btn_clear_clip\" remove_id=\"" + sStepID + "\">" +
							"<img src=\"../images/icons/fileclose.png\" style=\"width: 16px; height: 16px;\" alt=\"\" />" +
								"</span>";
						sHTML += "</td></tr></table>";
						
						
						sHTML += "<div class=\"hidden\" id=\"help_text_clip_" + sStepID + "\">" + sDesc + "</div>";
						
						//we use this function because it draws a smaller version than DrawReadOnlyStep
						string sStepHTML = "";
						//and don't draw those complex ones either
						if (!"loop,exists,if,while".Contains(sFunction))
							sStepHTML = ft.DrawClipboardStep(cs, true);
						
						sHTML += "<div class=\"hidden\" id=\"v_" + sStepID + "\">" + sStepHTML + "</div>";
						sHTML += "</li>";
	                }
				}
                return sHTML;
            }
            catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }
        }
        #endregion

        #region "Tasks"
		[WebMethod(EnableSession = true)]
        public string wmApproveTask(string sTaskID, string sMakeDefault)
        {
            dataAccess dc = new dataAccess();

            acUI.acUI ui = new acUI.acUI();

            try
            {
                string sUserID = ui.GetSessionUserID();

                if (ui.IsGUID(sTaskID) && ui.IsGUID(sUserID))
                {
                    string sErr = "";
                    string sSQL = "";

                    //check to see if this is the first task to be approved.
                    //if it is, we will make it default.
                    sSQL = "select count(*) from task" +
                        " where original_task_id = " +
                        " (select original_task_id from task where task_id = '" + sTaskID + "')" +
                        " and task_status = 'Approved'";

                    int iCount = 0;
                    if (!dc.sqlGetSingleInteger(ref iCount, sSQL, ref sErr))
                    {
                        throw new Exception("Unable to count Tasks in this family.." + sErr);
                    }

                    if (iCount == 0)
                        sMakeDefault = "1";



                    dataAccess.acTransaction oTrans = new dataAccess.acTransaction(ref sErr);


                    //flag all the other tasks as not default if this one is meant to be
                    if (sMakeDefault == "1")
                    {
                        sSQL = "update task set" +
                            " default_version = 0" +
                            " where original_task_id =" +
                            " (select original_task_id from (select original_task_id from task where task_id = '" + sTaskID + "') as x)";
                        oTrans.Command.CommandText = sSQL;
                        if (!oTrans.ExecUpdate(ref sErr))
                        {
                            throw new Exception("Unable to update task [" + sTaskID + "]." + sErr);
                        }
                        sSQL = "update task set" +
                        " task_status = 'Approved'," +
                        " default_version = 1" +
                        " where task_id = '" + sTaskID + "';";
                    }
                    else
                    {
                        sSQL = "update task set" +
                            " task_status = 'Approved'" +
                            " where task_id = '" + sTaskID + "'";
                    }

                    oTrans.Command.CommandText = sSQL;
                    if (!oTrans.ExecUpdate(ref sErr))
                    {
                        throw new Exception("Unable to update task [" + sTaskID + "]." + sErr);
                    }

                    oTrans.Commit();

                    ui.WriteObjectPropertyChangeLog(Globals.acObjectTypes.Task, sTaskID, "Status", "Development", "Approved");
                    if (sMakeDefault == "1")
                        ui.WriteObjectChangeLog(Globals.acObjectTypes.Task, sTaskID, "Default", "Set as Default Version.");

                }
                else
                {
                    throw new Exception("Unable to update task. Missing or invalid task id. [" + sTaskID + "]");
                }

            }
            catch (Exception ex)
            {
                throw ex;
            }
            return "";
        }

        [WebMethod(EnableSession = true)]
        public void wmSaveTestAsset(string sTaskID, string sAssetID)
        {
            wmSaveTaskUserSetting(sTaskID, "asset_id", sAssetID);
        }

        [WebMethod(EnableSession = true)]
        public string wmRerunTask(int iInstanceID, string sClearLog)
        {
            dataAccess dc = new dataAccess();

            acUI.acUI ui = new acUI.acUI();

            try
            {
                string sUserID = ui.GetSessionUserID();

                if (iInstanceID > 0 && ui.IsGUID(sUserID))
                {

                    string sInstance = "";
                    string sErr = "";
                    string sSQL = "";

                    if (dc.IsTrue(sClearLog))
                    {
                        sSQL = "delete from task_instance_log" +
                            " where task_instance = '" + iInstanceID.ToString() + "'";

                        if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                        {
                            throw new Exception("Unable to clear task instance log for [" + iInstanceID.ToString() + "]." + sErr);
                        }
                    }
                    sSQL = "update task_instance set task_status = 'Submitted'," +
                        " submitted_by = '" + sUserID + "'" +
                        " where task_instance = '" + iInstanceID.ToString() + "'";

                    if (!dc.sqlGetSingleString(ref sInstance, sSQL, ref sErr))
                    {
                        throw new Exception("Unable to rerun task instance [" + iInstanceID.ToString() + "]." + sErr);
                    }

                    return sInstance;
                }
                else
                {
                    throw new Exception("Unable to run task. Missing or invalid task instance [" + iInstanceID.ToString() + "]");
                }

            }
            catch (Exception ex)
            {
                throw ex;
            }
        }
		
		//SIMILAR FUNCTION WARNING - one requires a userid the other uses the session
        [WebMethod(EnableSession = true)]
        public string wmRunTask(string sTaskID, string sEcosystemID, string sAccountID, string sAssetID, string sParameterXML, int iDebugLevel)
        {
            acUI.acUI ui = new acUI.acUI();
			string sUserID = ui.GetSessionUserID();
			return AddTaskInstance(sUserID, sTaskID, sEcosystemID, sAccountID, sAssetID, sParameterXML, iDebugLevel);
        }
        [WebMethod()]
        public string wmRunTaskByUser(string sUserID, string sTaskID, string sEcosystemID, string sAccountID, string sAssetID, string sParameterXML, int iDebugLevel)
        {
			return AddTaskInstance(sUserID, sTaskID, sEcosystemID, sAccountID, sAssetID, sParameterXML, iDebugLevel);
        }
		
		private string AddTaskInstance(string sUserID, string sTaskID, string sEcosystemID, string sAccountID, string sAssetID, string sParameterXML, int iDebugLevel) {
            dataAccess dc = new dataAccess();
            acUI.acUI ui = new acUI.acUI();
			uiMethods um = new uiMethods();
			
            //we encoded this in javascript before the ajax call.
            //the safest way to unencode it is to use the same javascript lib.
            //(sometimes the javascript and .net libs don't translate exactly, google it.)
            sParameterXML = ui.unpackJSON(sParameterXML);
							
			//we gotta peek into the XML and encrypt any newly keyed values
			um.PrepareAndEncryptParameterXML(ref sParameterXML);				

            try
            {
                if (ui.IsGUID(sTaskID) && ui.IsGUID(sUserID))
                {

                    string sInstance = "";
                    string sErr = "";

                    string sSQL = "call addTaskInstance ('" + sTaskID + "','" + 
						sUserID + "',NULL," + 
						iDebugLevel + ",NULL,'" + 
						ui.TickSlash(sParameterXML) + "','" + 
						sEcosystemID + "','" + 
						sAccountID + "')";

                    if (!dc.sqlGetSingleString(ref sInstance, sSQL, ref sErr))
                    {
                        throw new Exception("Unable to run task [" + sTaskID + "]." + sErr);
                    }

                    return sInstance;
                }
                else
                {
                    throw new Exception("Unable to run task. Missing or invalid task [" + sTaskID + "] or user [" + sUserID + "] id.");
                }

            }
            catch (Exception ex)
            {
                throw ex;
            }
		}
		
        [WebMethod(EnableSession = true)]
        public void wmStopTask(string sInstance)
        {
            dataAccess dc = new dataAccess();

            try
            {
                if (sInstance != "")
                {
                    string sErr = "";
                    string sSQL = "update task_instance set task_status = 'Aborting'" +
                        " where task_instance = '" + sInstance + "'" +
                        " and task_status in ('Processing');";

                    if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                    {
                        throw new Exception("Unable to stop task instance [" + sInstance + "]." + sErr);
                    }

                    sSQL = "update task_instance set task_status = 'Cancelled'" +
                        " where task_instance = '" + sInstance + "'" +
                        " and task_status in ('Submitted','Queued','Staged')";

                    if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                    {
                        throw new Exception("Unable to stop task instance [" + sInstance + "]." + sErr);
                    }

                    return;
                }
                else
                {
                    throw new Exception("Unable to stop task. Missing or invalid task_instance.");
                }

            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public string wmTaskSearch(string sSearchText)
        {
            try
            {
                dataAccess dc = new dataAccess();
                string sErr = "";
                string sWhereString = "";

                if (sSearchText.Length > 0)
                {
                    sWhereString = " and (a.task_name like '%" + sSearchText +
                                   "%' or a.task_desc like '%" + sSearchText +
                                   "%' or a.task_code like '%" + sSearchText + "%' ) ";
                }

                string sSQL = "select a.original_task_id, a.task_id, a.task_name, a.task_code," +
                    " left(a.task_desc, 255) as task_desc, a.version" +
                       " from task a  " +
                       " where default_version = 1" +
                       sWhereString +
                       " order by task_name, default_version desc, version";

                DataTable dt = new DataTable();
                if (!dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
                {
                    throw new Exception(sErr);
                }

                string sHTML = "<hr />";
                if (dt.Rows.Count == 0)
                {
                    sHTML += "No results found";
                }
                else
                {
                    int iRowsToGet = dt.Rows.Count;
                    if (iRowsToGet >= 100)
                    {
                        sHTML += "<div>Search found " + dt.Rows.Count + " results.  Displaying the first 100.</div>";
                        iRowsToGet = 99;
                    }
                    sHTML += "<ul id=\"search_task_ul\" class=\"search_dialog_ul\">";

                    for (int i = 0; i < iRowsToGet; i++)
                    {
                        string sTaskName = dt.Rows[i]["task_name"].ToString().Replace("\"", "\\\"");
                        string sLabel = dt.Rows[i]["task_code"].ToString() + " : " + sTaskName;
                        string sDesc = dt.Rows[i]["task_desc"].ToString().Replace("\"", "").Replace("'", "");

                        sHTML += "<li class=\"ui-widget-content ui-corner-all search_dialog_value\" tag=\"task_picker_row\"" +
                            " original_task_id=\"" + dt.Rows[i]["original_task_id"].ToString() + "\"" +
                            " task_label=\"" + sLabel + "\"" +
                            "\">";
                        sHTML += "<div class=\"step_header_title search_dialog_value_name\">" + sLabel + "</div>";

                        sHTML += "<div class=\"step_header_icons\">";

                        //if there's a description, show a tooltip
                        if (!string.IsNullOrEmpty(sDesc))
                            sHTML += "<img src=\"../images/icons/info.png\" class=\"search_dialog_tooltip trans50\" title=\"" + sDesc + "\" />";

                        sHTML += "</div>";
                        sHTML += "<div class=\"clearfloat\"></div>";
                        sHTML += "</li>";
                    }
                }
                sHTML += "</ul>";

                return sHTML;
            }
            catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }
        }

        [WebMethod(EnableSession = true)]
        public string wmGetTaskConnections(string sTaskID)
        {
            dataAccess dc = new dataAccess();

            acUI.acUI ui = new acUI.acUI();

            try
            {
                if (ui.IsGUID(sTaskID))
                {
                    string sErr = "";
                    string sSQL = "select conn_name from (" +
                        "select distinct ExtractValue(function_xml, '//conn_name[1]') as conn_name" +
                        " from task_step" +
                            " where function_name = 'new_connection'" +
                            " and task_id = '" + sTaskID + "'" +
                            " ) foo" +
                        " where ifnull(conn_name,'') <> ''" +
                        " order by conn_name";

                    DataTable dt = new DataTable();
                    if (!dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
                    {
                        throw new Exception("Unable to get connections for task." + sErr);
                    }

                    string sHTML = "";

                    foreach (DataRow dr in dt.Rows)
                    {
                        sHTML += "<div class=\"ui-widget-content ui-corner-all value_picker_value\">" + dr["conn_name"].ToString() + "</div>";
                    }

                    return sHTML;
                }
                else
                {
                    throw new Exception("Unable to get connections for task. Missing or invalid task_id.");
                }

            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public string wmGetTaskCodeblocks(string sTaskID, string sStepID)
        {
            dataAccess dc = new dataAccess();

            acUI.acUI ui = new acUI.acUI();

            try
            {
                if (ui.IsGUID(sTaskID))
                {
                    string sErr = "";
                    string sSQL = "select codeblock_name from task_codeblock where task_id = '" + sTaskID + "'" +
                        " and codeblock_name not in (select codeblock_name from task_step where step_id = '" + sStepID + "')" +
                        " order by codeblock_name";

                    DataTable dt = new DataTable();
                    if (!dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
                    {
                        throw new Exception("Unable to get codeblocks for task." + sErr);
                    }

                    string sHTML = "";

                    foreach (DataRow dr in dt.Rows)
                    {
                        sHTML += "<div class=\"ui-widget-content ui-corner-all value_picker_value\">" + dr["codeblock_name"].ToString() + "</div>";
                    }

                    return sHTML;
                }
                else
                {
                    throw new Exception("Unable to get codeblocks for task. Missing or invalid task_id.");
                }

            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public string wmRenameCodeblock(string sTaskID, string sOldCodeblockName, string sNewCodeblockName)
        {
            dataAccess dc = new dataAccess();

            acUI.acUI ui = new acUI.acUI();
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();

            try
            {
                if (ui.IsGUID(sTaskID))
                {

                    // first make sure we are not trying to rename it something that already exists.
                    string sErr = "";
                    string sSQL = "select count(*) from task_codeblock where task_id = '" + sTaskID + "'" +
                        " and codeblock_name = '" + sNewCodeblockName + "'";
                    int iCount = 0;

                    if (!dc.sqlGetSingleInteger(ref iCount, sSQL, ref sErr))
                    {
                        throw new Exception("Unable to check codeblock names for task." + sErr);
                    }
                    if (iCount != 0)
                    {
                        return ("Codeblock Name already in use, choose another.");
                    }

                    // do it
                    dataAccess.acTransaction oTrans = new dataAccess.acTransaction(ref sErr);

                    //update the codeblock table
                    sSQL = "update task_codeblock set codeblock_name = '" + sNewCodeblockName +
                        "' where codeblock_name = '" + sOldCodeblockName +
                        "' and task_id = '" + sTaskID + "'";

                    oTrans.Command.CommandText = sSQL;
                    if (!oTrans.ExecUpdate(ref sErr))
                    {
                        throw new Exception(sErr);
                    }

                    //and any steps in that codeblock
                    sSQL = "update task_step set codeblock_name = '" + sNewCodeblockName +
                        "' where codeblock_name = '" + sOldCodeblockName +
                        "' and task_id = '" + sTaskID + "'";

                    oTrans.Command.CommandText = sSQL;
                    if (!oTrans.ExecUpdate(ref sErr))
                    {
                        throw new Exception(sErr);
                    }

                    //the fun part... rename it where it exists in any steps
                    //but this must be in a loop of only the steps where that codeblock reference exists.
                    sSQL = "select step_id from task_step" +
                        " where task_id = '" + sTaskID + "'" +
                        " and ExtractValue(function_xml, '//codeblock[1]') = '" + sOldCodeblockName + "'";
                    oTrans.Command.CommandText = sSQL;
                    DataTable dtSteps = new DataTable();
                    if (!oTrans.ExecGetDataTable(ref dtSteps, ref sErr))
                    {
                        throw new Exception("Unable to get steps referencing the Codeblock." + sErr);
                    }

                    foreach (DataRow dr in dtSteps.Rows)
                    {
                        ft.SetNodeValueinXMLColumn("task_step", "function_xml", "step_id = '" + dr["step_id"].ToString() + "'", "//codeblock[. = '" + sOldCodeblockName + "']", sNewCodeblockName);
                    }



                    //all done
                    oTrans.Commit();

                    return sErr;

                }
                else
                {
                    throw new Exception("Unable to get codeblocks for task. Missing or invalid task_id.");
                }

            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public string wmGetTaskVariables(string sTaskID)
        {
            dataAccess dc = new dataAccess();

            acUI.acUI ui = new acUI.acUI();

            try
            {
                if (ui.IsGUID(sTaskID))
                {
                    string sErr = "";
                    string sHTML = "";

                    //VARIABLES
                    string sSQL = "select distinct var_name from (" +
                        "select ExtractValue(function_xml, '//function/counter[1]') as var_name" +
                        " from task_step" +
                        " where task_id = '" + sTaskID + "'" +
                        " and function_name = 'loop'" +
                        " UNION" +
                        " select ExtractValue(variable_xml, '//variable/name[1]') as var_name" +
                        " from task_step" +
                        " where task_id = '" + sTaskID + "'" +
                        " UNION" +
                        " select ExtractValue(function_xml, '//variable/name[1]') as var_name" +
                        " from task_step" +
                        " where task_id = '" + sTaskID + "'" +
                        " and function_name in ('set_variable','substring')" +
                        " ) foo" +
                        " where ifnull(var_name,'') <> ''" +
                        " order by var_name";

                    DataTable dtVars = new DataTable();
                    dtVars.Columns.Add("var_name");
                    DataTable dtStupidVars = new DataTable();
                    if (!dc.sqlGetDataTable(ref dtStupidVars, sSQL, ref sErr))
                        throw new Exception("Unable to get variables for task." + sErr);

                    if (dtStupidVars.Rows.Count > 0)
                    {
                        foreach (DataRow drStupidVars in dtStupidVars.Rows)
                        {
                            if (drStupidVars["var_name"].ToString().IndexOf(' ') > -1)
                            {
                                //split it on the space
                                string[] aVars = drStupidVars["var_name"].ToString().Split(' ');
                                foreach (string sVar in aVars)
                                {
                                    dtVars.Rows.Add(sVar);
                                }
                            }
                            else
                            {
                                dtVars.Rows.Add(drStupidVars["var_name"].ToString());
                            }
                        }
                    }

                    //now that we've manually added some rows, resort it
                    DataView dv = dtVars.DefaultView;
                    dv.Sort = "var_name";
                    dtVars = dv.ToTable();



                    //Finally, we have a table with all the vars!
                    if (dtVars.Rows.Count > 0)
                    {

                        sHTML += "<div target=\"var_picker_group_vars\" class=\"ui-widget-content ui-corner-all value_picker_group\"><img alt=\"\" src=\"../images/icons/expand.png\" style=\"width:12px;height:12px;\" /> Variables</div>";
                        sHTML += "<div id=\"var_picker_group_vars\" class=\"hidden\">";

                        foreach (DataRow drVars in dtVars.Rows)
                        {
                            sHTML += "<div class=\"ui-widget-content ui-corner-all value_picker_value\">" + drVars["var_name"].ToString() + "</div>";
                        }

                        sHTML += "</div>";
                    }

                    //PARAMETERS
                    sSQL = "select parameter_xml from task where task_id = '" + sTaskID + "'";

                    string sParameterXML = "";

                    if (!dc.sqlGetSingleString(ref sParameterXML, sSQL, ref sErr))
                    {
                        throw new Exception(sErr);
                    }

                    if (sParameterXML != "")
                    {
                        XDocument xDoc = XDocument.Parse(sParameterXML);
                        if (xDoc == null)
                            throw new Exception("Parameter XML data for task [" + sTaskID + "] is invalid.");

                        XElement xParams = xDoc.XPathSelectElement("/parameters");
                        if (xParams != null)
                        {
                            sHTML += "<div target=\"var_picker_group_params\" class=\"ui-widget-content ui-corner-all value_picker_group\"><img alt=\"\" src=\"../images/icons/expand.png\" style=\"width:12px;height:12px;\" /> Parameters</div>";
                            sHTML += "<div id=\"var_picker_group_params\" class=\"hidden\">";

                            foreach (XElement xParameter in xParams.XPathSelectElements("parameter"))
                            {
                                sHTML += "<div class=\"ui-widget-content ui-corner-all value_picker_value\">" + xParameter.Element("name").Value + "</div>";
                            }
                        }
                        sHTML += "</div>";
                    }

                    // Global Variables in an xml file
                    try
                    {
                        XDocument xGlobals = XDocument.Load(Server.MapPath("~/pages/luGlobalVariable.xml"));

                        if (xGlobals == null)
                        {
                            sErr = "XML globals is empty.";

                        }
                        else
                        {
                            sHTML += "<div target=\"var_picker_group_globals\" class=\"ui-widget-content ui-corner-all value_picker_group\"><img alt=\"\" src=\"../images/icons/expand.png\" style=\"width:12px;height:12px;\" /> Globals</div>";
                            sHTML += "<div id=\"var_picker_group_globals\" class=\"hidden\">";

                            IEnumerable<XElement> xItems = xGlobals.XPathSelectElement("globals").XPathSelectElements("global/name");
                            foreach (XElement xEl in xItems)
                                sHTML += "<div class=\"ui-widget-content ui-corner-all value_picker_value\">" + xEl.Value.ToString() + "</div>";

                            sHTML += "</div>";
                        }

                    }
                    catch (Exception)
                    {
                        // if the file does not exist, just ignore it
                    }




                    return sHTML;
                }
                else
                {
                    throw new Exception("Unable to get variables for task. Missing or invalid task_id.");
                }

            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public string wmUpdateTaskDetail(string sTaskID, string sColumn, string sValue)
        {
            dataAccess dc = new dataAccess();

            acUI.acUI ui = new acUI.acUI();

            try
            {
                string sUserID = ui.GetSessionUserID();

                if (ui.IsGUID(sTaskID) && ui.IsGUID(sUserID))
                {
                    string sErr = "";
                    string sSQL = "";

                    //we encoded this in javascript before the ajax call.
                    //the safest way to unencode it is to use the same javascript lib.
                    //(sometimes the javascript and .net libs don't translate exactly, google it.)
                    sValue = ui.unpackJSON(sValue);
					sValue = ui.TickSlash(sValue);
					
                    string sOriginalTaskID = "";

                    sSQL = "select original_task_id from task where task_id = '" + sTaskID + "'";

                    if (!dc.sqlGetSingleString(ref sOriginalTaskID, sSQL, ref sErr))
                        throw new Exception("Unable to get original_task_id for [" + sTaskID + "]." + sErr);

                    if (sOriginalTaskID == "")
                        return "Unable to get original_task_id for [" + sTaskID + "].";


                    // bugzilla 1074, check for existing task_code and task_name
                    if (sColumn == "task_code" || sColumn == "task_name")
                    {
                        sSQL = "select task_id from task where " +
                                sColumn + "='" + sValue + "'" +
                                " and original_task_id <> '" + sOriginalTaskID + "'";

                        string sValueExists = "";
                        if (!dc.sqlGetSingleString(ref sValueExists, sSQL, ref sErr))
                            throw new Exception("Unable to check for existing names [" + sTaskID + "]." + sErr);

                        if (!string.IsNullOrEmpty(sValueExists))
                            return sValue + " exists, please choose another value.";
                    }

                    if (sColumn == "task_code" || sColumn == "task_name")
                    {
                        //changing the name or code updates ALL VERSIONS
                        string sSetClause = sColumn + "='" + sValue + "'";
                        sSQL = "update task set " + sSetClause + " where original_task_id = '" + sOriginalTaskID + "'";
                    }
                    else
                    {
                        string sSetClause = sColumn + "='" + sValue + "'";

                        //some columns on this table allow nulls... in their case an empty sValue is a null
                        if (sColumn == "concurrent_instances" || sColumn == "queue_depth")
                        {
                            if (sValue.Replace(" ", "").Length == 0)
                                sSetClause = sColumn + " = null";
                            else
                                sSetClause = sColumn + "='" + sValue + "'";
                        }

                        //some columns are checkboxes, so make sure it is a db appropriate value (1 or 0)
                        //some columns on this table allow nulls... in their case an empty sValue is a null
                        if (sColumn == "concurrent_by_asset")
                        {
                            if (dc.IsTrue(sValue))
                                sSetClause = sColumn + " = 1";
                            else
                                sSetClause = sColumn + " = 0";
                        }


						sSQL = "update task set " + sSetClause + " where task_id = '" + sTaskID + "'";
                    }


                    if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                        throw new Exception("Unable to update task [" + sTaskID + "]." + sErr);

                    ui.WriteObjectChangeLog(Globals.acObjectTypes.Task, sTaskID, sColumn, sValue);
                }
                else
                {
                    throw new Exception("Unable to update task. Missing or invalid task [" + sTaskID + "] id.");
                }

            }
            catch (Exception ex)
            {
                throw ex;
            }
            return "";
        }

        [WebMethod(EnableSession = true)]
        public string wmDeleteTasks(string sDeleteArray)
        {
            dataAccess dc = new dataAccess();
            acUI.acUI ui = new acUI.acUI();

            string sSql = null;
            string sErr = "";
            string sTaskNames = "";

            if (sDeleteArray.Length < 36)
                return "";

            sDeleteArray = ui.QuoteUp(sDeleteArray);

            //NOTE: right now this plows ALL versions.  There is an enhancement to possibly 'retire' a task, or
            //only delete certain versions.

            try
            {


                // what about the instance tables?????
                // bugzilla 1290 Tasks that have history (task_instance table) can not be deleted
                // exclude them from the list and return a message noting the task(s) that could not be deleted

                // first we need a list of tasks that will not be deleted
                sSql = "select task_name from task t " +
                        "where t.original_task_id in (" + sDeleteArray.ToString() + ") " +
                        "and t.task_id in (select ti.task_id from tv_task_instance ti where ti.task_id = t.task_id)";

                if (!dc.csvGetList(ref sTaskNames, sSql, ref sErr, true))
                    throw new Exception(sErr);

                // list of tasks that will be deleted
                //we have an array of 'original_task_id'.
                //we need an array or task_id
                //build one.
                sSql = "select t.task_id from task t " +
                    "where t.original_task_id in (" + sDeleteArray.ToString() + ") " +
                    "and t.task_id not in (select ti.task_id from tv_task_instance ti where ti.task_id = t.task_id)";

                string sTaskIDs = "";
                if (!dc.csvGetList(ref sTaskIDs, sSql, ref sErr, true))
                    throw new Exception(sErr);

                // if any tasks can be deleted
                if (sTaskIDs.Length > 1)
                {
                    dataAccess.acTransaction oTrans = new dataAccess.acTransaction(ref sErr);

                    oTrans.Command.CommandText = "delete from task_step_user_settings" +
                        " where step_id in" +
                        " (select step_id from task_step where task_id in (" + sTaskIDs + "))";
                    if (!oTrans.ExecUpdate(ref sErr))
                        throw new Exception(sErr);

                    oTrans.Command.CommandText = "delete from task_step where task_id in (" + sTaskIDs + ")";
                    if (!oTrans.ExecUpdate(ref sErr))
                        throw new Exception(sErr);

                    oTrans.Command.CommandText = "delete from task_codeblock where task_id in (" + sTaskIDs + ")";
                    if (!oTrans.ExecUpdate(ref sErr))
                        throw new Exception(sErr);

                    oTrans.Command.CommandText = "delete from task where task_id in (" + sTaskIDs + ")";
                    if (!oTrans.ExecUpdate(ref sErr))
                        throw new Exception(sErr);

                    oTrans.Commit();

                    ui.WriteObjectDeleteLog(Globals.acObjectTypes.Task, "Multiple", "Original Task IDs", sDeleteArray.ToString());

                }


            }
            catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }

            // if the sTaskNames contains any names, then send back a message that these were not deleted because of history records.
            if (sTaskNames.Length > 0)
            {
                return "Task(s) (" + sTaskNames + ") have history rows and could not be deleted.";
            }
            else
            {
                return sErr;
            }

        }

        [WebMethod(EnableSession = true)]
        public string wmExportTasks(string sTaskArray)
        {
			acUI.acUI ui = new acUI.acUI();
			ImportExport.ImportExportClass ie = new ImportExport.ImportExportClass();
			
			string sErr = "";
			
			//pretty much just call the ImportExport function
			try
			{
				//interesting mid-point stopping point...
				//if only one task was selected, export it as XML
				//if more than one, export it the old way as a .csk bundle.
				
				//(because the end goal is the .csk files are still just zip files, 
				//but will contain the new style xml files.
				if (sTaskArray.Contains(","))
				{
					if (sTaskArray.Length < 36)
						return "";
					
					sTaskArray = ui.QuoteUp(sTaskArray);

					//what are we gonna call the final file?
					string sUserID = ui.GetSessionUserID();
					string sFileName = sUserID + "_backup";
					string sPath = Server.MapPath("~/temp/");

					if (!ie.doBatchTaskExport(sPath, sTaskArray, sFileName, ref sErr))
					{
						throw new Exception("Unable to export Tasks." + sErr);
					}
					
					if (sErr == "")
						return sFileName + ".csk";
					else
						return sErr;
				}
				else
				{
					if (sTaskArray.Length == 36)
					{
						Task t = new Task(sTaskArray, "", ref sErr);
						if (t != null)
						{
							string sXML = t.AsXML();
		
							//what are we gonna call the final file?
							TimeSpan oTS = (DateTime.UtcNow - new DateTime(1970, 1, 1));
							int iSecs  = (int) oTS.TotalSeconds;
							string sFileName = Server.UrlEncode(t.Name.Replace(" ","").Replace("/","")) + "_" + iSecs.ToString() + ".xml";
							string sPath = Server.MapPath("~/temp/");
		
							ui.SaveStringToFile(sPath + sFileName, sXML);
							return sFileName;
						}
						else
						{
							return "Unable to get Task [" + sTaskArray + "] to export.";
						}				
					}
					else
					{
						return "Error: Selected Task ID wasn't the right length.";
					}				
				}
			}
			catch (Exception ex)
			{
				throw new Exception(ex.Message);
			}
        }
		
		//THIS METHOD IS INTERNAL
		//we use it for renaming a backup file suitable for the task library.
		//it's not bulletproof, and is not exposed in the gui.
        [WebMethod(EnableSession = true)]
        public string wmRenameFile(string sExistingName, string sNewFileName)
        {
			string sPath = Server.MapPath("~/temp/");

			try
			{
				//delete the new name if it exists
				//File.Delete(sPath + sNewFileName);
			
				//rename the file to our new name
				File.Move(sPath + sExistingName, sPath + sNewFileName);
				
				return sNewFileName;
			}
			catch (Exception ex)
			{
				throw new Exception(ex.Message);
			}
        }

		[WebMethod(EnableSession = true)]
        public string wmCreateTask(string sTaskName, string sTaskCode, string sTaskDesc)
        {
            try
            {
				acUI.acUI ui = new acUI.acUI();

				string sErr = "";

				//create a new Task object
				Task t = new Task(ui.unpackJSON(sTaskName), ui.unpackJSON(sTaskCode), ui.unpackJSON(sTaskDesc));

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

        }

		[WebMethod(EnableSession = true)]
        public string wmCreateTasksFromXML(string sXML)
        {
            try
            {
				if (string.IsNullOrEmpty(sXML))
					return "{\"error\" : \"Task XML is required.\"}";
					
	            acUI.acUI ui = new acUI.acUI();
	            string sErr = "";
	
				string sTestXML = ui.unpackJSON(sXML);
				XDocument xd = XDocument.Parse(sTestXML);
				if (xd != null)
				{
					//make a transaction, and load them all
					dataAccess.acTransaction oTrans = new dataAccess.acTransaction(ref sErr);
					
					string sTaskIDs = "";
					
					//root might be 'task' or 'tasks', so a global xpath handles both.
					foreach (XElement xTask in xd.XPathSelectElements("//task")) {						
						Task t = new Task().FromXML(xTask.ToString(SaveOptions.DisableFormatting), ref sErr);
						
						if (!string.IsNullOrEmpty(sErr))
							return "{\"error\" : \"Could not create Task from XML: " + sErr + "\"}";
						
						if (t != null) {
							if(t.DBSave(ref sErr, oTrans))
							{
								if (!string.IsNullOrEmpty(sErr))
									return "{\"error\" : \"" + sErr + "\"}";
								
								sTaskIDs += "\"" + t.ID + "\" ";
							}
							else
								return "{\"error\" : \"" + sErr + "\"}";
						}
						else
							return "{\"error\" : \"" + sErr + "\"}";
					}
					
					oTrans.Commit();
					return "{\"type\" : \"tasks\", \"ids\" : [" + sTaskIDs.Trim().Replace(" ",",") + "] }";

				} else {
					return "{\"error\" : \"Unable to parse Task XML: " + sErr + "\"}";
				}
            }
			catch (System.Xml.XmlException ex)
			{
				throw new Exception("Error parsing Task XML:\n" + ex.Message);
			}
			catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }
        }

        [WebMethod(EnableSession = true)]
        public string wmCopyTask(string sCopyTaskID, string sTaskCode, string sTaskName)
        {
            acUI.acUI ui = new acUI.acUI();
            string sErr = null;
			
			//using the object
			Task oTask = new Task(sCopyTaskID, true, ref sErr);
			if (oTask == null)
			{
				throw new Exception("Unable to continue.  Unable to build Task object" + sErr);
			}
			
			string sNewTaskID = oTask.Copy(0, sTaskName, sTaskCode);
            if (string.IsNullOrEmpty(sNewTaskID))
			{
                return "Unable to create Task: " + sErr;
            }

			ui.WriteObjectAddLog(Globals.acObjectTypes.Task, oTask.ID, oTask.Name, "Copied from " + sCopyTaskID);
            
            // success, return the new task_id
            return sNewTaskID;

        }

        [WebMethod(EnableSession = true)]
        public string wmGetTaskCodeFromID(string sOriginalTaskID)
        {
            dataAccess dc = new dataAccess();
            acUI.acUI ui = new acUI.acUI();

            if (!ui.IsGUID(sOriginalTaskID.Replace("'", "")))
                throw new Exception("Invalid or missing Task ID.");

            try
            {
                string sErr = "";
                string sSQL = "";

                sSQL = "select task_code from task where original_task_id = '" + sOriginalTaskID + "' and default_version = 1";
                string sTaskCode = "";
                if (!dc.sqlGetSingleString(ref sTaskCode, sSQL, ref sErr))
                {
                    throw new Exception("Unable to get task code." + sErr);
                }
                else
                {

                    return sTaskCode;
                }
            }
            catch (Exception ex)
            {
                throw ex;
            }

        }

        [WebMethod(EnableSession = true)]
        public string wmCreateNewTaskVersion(string sTaskID, string sMinorMajor)
        {
            try
            {
				string sErr = "";
				Task oTask = new Task(sTaskID, true, ref sErr);
				if (oTask == null)
				{
					throw new Exception("Unable to continue.  Unable to build Task object" + sErr);
				}
				
				string sNewTaskID = oTask.Copy((sMinorMajor == "Major" ? 1 : 2), "", "");
				if (string.IsNullOrEmpty(sNewTaskID))
				{
					return "Unable to create new Version: " + sErr;
				}

                return sNewTaskID;
            }
            catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }
        }

        [WebMethod()]
        public string wmGetTaskIDFromName(string sTaskName)
        {
            dataAccess dc = new dataAccess();
            try
            {
                //this expects taskname:version syntax
                //if there is no : the default version is assumed
                string sErr = "";
                string sSQL = "";

                string[] aTNV = sTaskName.Split(':');
                if (aTNV.Length > 1)
                {
                    //there is a version
                    sSQL = "select task_id" +
                        " from task where task_name = '" + aTNV[0] + "'" +
                        " and version = '" + aTNV[1] + "'";
                }
                else
                {
                    //there is not, default
                    sSQL = "select task_id" +
                        " from task where task_name = '" + aTNV[0] + "'" +
                        " and default_version = 1";
                }

                string sID = "";

                if (!string.IsNullOrEmpty(sSQL))
                {
                    dc.sqlGetSingleString(ref sID, sSQL, ref sErr);
                    return sID;
                }

                return "";
            }
            catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }
        }

        [WebMethod()]
        public string wmGetTaskIDFromOTIDandVersion(string sOTID, string sVersion)
        {
            if (string.IsNullOrEmpty(sOTID))
				return "";
			
			dataAccess dc = new dataAccess();
            try
            {
                string sErr = "";
                string sSQL = "";

                if (!string.IsNullOrEmpty(sVersion))
                {
                    //there is a version
                    sSQL = "select task_id" +
                        " from task where original_task_id = '" + sOTID + "'" +
                        " and version = '" + sVersion + "'";
                }
                else
                {
                    //there is not, default
                    sSQL = "select task_id" +
                        " from task where original_task_id = '" + sOTID + "'" +
                        " and default_version = 1";
                }

                string sID = "";

                if (!string.IsNullOrEmpty(sSQL))
                {
                    dc.sqlGetSingleString(ref sID, sSQL, ref sErr);
                    return sID;
                }

                return "";
            }
            catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }
        }

		[WebMethod(EnableSession = true)]
        public string wmGetTaskVersions(string sTaskID)
        {
            dataAccess dc = new dataAccess();
            string sErr = "";
            try
            {
                string sHTML = "";

                string sSQL = "select task_id, version, default_version," +
                              " case default_version when 1 then ' (default)' else '' end as is_default," +
                              " case task_status when 'Approved' then 'encrypted' else 'unlock' end as status_icon," +
                              " date_format(created_dt, '%Y-%m-%d %T') as created_dt" +
                              " from task" +
                              " where original_task_id = " +
                              " (select original_task_id from task where task_id = '" + sTaskID + "')" +
                              " order by version";

                DataTable dt = new DataTable();
                if (!dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
                {
                    throw new Exception("Error selecting versions: " + sErr);
                }
                else
                {
                    if (dt.Rows.Count > 0)
                    {
                        foreach (DataRow dr in dt.Rows)
                        {
                            sHTML += "<li class=\"ui-widget-content ui-corner-all version code\" id=\"v_" + dr["task_id"].ToString() + "\"";
                            sHTML += "task_id=\"" + dr["task_id"].ToString() + "\">";
                            sHTML += "<img src=\"../images/icons/" + dr["status_icon"].ToString() + "_16.png\" alt=\"\" />";
                            sHTML += dr["version"].ToString() + "&nbsp;&nbsp;" + dr["created_dt"].ToString() + dr["is_default"].ToString();
                            sHTML += "</li>";
                            sHTML += "";
                            sHTML += "";

                        }
                    }
                }
                return sHTML;
            }
            catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }
        }

        [WebMethod(EnableSession = true)]
        public string wmGetTaskVersionsDropdown(string sOriginalTaskID)
        {
            dataAccess dc = new dataAccess();
            string sErr = "";
            try
            {
                StringBuilder sbString = new StringBuilder();

                string sSQL = "select task_id, version, default_version" +
                        " from task " +
                        " where original_task_id = '" + sOriginalTaskID + "'" +
                        " order by default_version desc, version";

                DataTable dt = new DataTable();
                if (!dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
                {
                    throw new Exception("Error selecting versions: " + sErr);
                }
                else
                {
                    if (dt.Rows.Count > 0)
                    {
                        sbString.Append("<select name=\"ddlTaskVersions\" style=\"width: 200px;\" id=\"ddlTaskVersions\">");
                        foreach (DataRow dr in dt.Rows)
                        {
                            string sLabel = dr["version"].ToString() + (dr["default_version"].ToString() == "1" ? " (default)" : "");
                            sbString.Append("<option value=\"" + dr["task_id"].ToString() + "\">" + sLabel + "</option>");
                        }
                        sbString.Append("</select>");
                        return sbString.ToString();
                    }
                    else
                    {
                        return "<select name=\"ddlTaskVersions\" id=\"ddlTaskVersions\"></select>";
                    }
                }
            }
            catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }
        }

        [WebMethod(EnableSession = true)]
        public string wmGetAssetIDFromName(string sName)
        {
            dataAccess dc = new dataAccess();


            try
            {
                if (sName.Length > 0)
                {
                    string sAssetID = "";
                    string sErr = "";
                    string sSQL = "select asset_id from asset where asset_name = '" + sName + "'";

                    if (!dc.sqlGetSingleString(ref sAssetID, sSQL, ref sErr))
                        throw new Exception("Unable to check for Asset [" + sName + "]." + sErr);

                    return sAssetID;
                }
                else
                    throw new Exception("Unable to check for Asset - missing Asset Name.");
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        #endregion

        #region "Command Specific"
        [WebMethod(EnableSession = true)]
        public void wmFnSetvarAddVar(string sStepID)
        {
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
            try
            {
                ft.AddToCommandXML(sStepID, "//function", "<variable>" +
                    "<name input_type=\"text\"></name>" +
                    "<value input_type=\"text\"></value>" +
                    "<modifier input_type=\"select\">DEFAULT</modifier>" +
                    "</variable>");

                return;
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public void wmFnClearvarAddVar(string sStepID)
        {
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
            try
            {
                ft.AddToCommandXML(sStepID, "//function", "<variable><name input_type=\"text\"></name></variable>");

                return;
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public void wmFnExistsAddVar(string sStepID)
        {
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
            try
            {
                ft.AddToCommandXML(sStepID, "//function", "<variable>" +
                    "<name input_type=\"text\"></name><is_true>0</is_true>" +
                    "</variable>");

                return;
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public void wmFnVarRemoveVar(string sStepID, int iIndex)
        {
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
            //NOTE: this function supports both the set_varible AND clear_variable commands
            try
            {
                if (iIndex > 0)
                {
                    ft.RemoveFromCommandXML(sStepID, "//function/variable[" + iIndex.ToString() + "]");

                    return;
                }
                else
                {
                    throw new Exception("Unable to modify step. Invalid index.");
                }
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public void wmFnIfRemoveSection(string sStepID, int iIndex)
        {
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
            acUI.acUI ui = new acUI.acUI();

            try
            {
                if (!ui.IsGUID(sStepID))
                    throw new Exception("Unable to remove section from step. Invalid or missing Step ID. [" + sStepID + "]");

                string sEmbStepID = "";

                if (iIndex > 0)
                {
                    //is there an embedded step?
                    sEmbStepID = ft.GetNodeValueFromCommandXML(sStepID, "//function/tests/test[" + iIndex.ToString() + "]/action[1]");

                    if (ui.IsGUID(sEmbStepID))
                        wmDeleteStep(sEmbStepID); //whack it

                    //now adjust the XML
                    ft.RemoveFromCommandXML(sStepID, "//function/tests/test[" + iIndex.ToString() + "]");
                }
                else if (iIndex == -1)
                {
                    //is there an embedded step?
                    sEmbStepID = ft.GetNodeValueFromCommandXML(sStepID, "//function/else[1]");

                    if (ui.IsGUID(sEmbStepID))
                        wmDeleteStep(sEmbStepID); //whack it

                    //now adjust the XML
                    ft.RemoveFromCommandXML(sStepID, "//function/else[1]");
                }
                else
                {
                    throw new Exception("Unable to modify step. Invalid index.");
                }

                return;

            }

            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public void wmFnIfAddSection(string sStepID, int iIndex)
        {
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
            try
            {
                if (iIndex > 0)
                {
                    //an index > 0 means its one of many 'else if' sections
                    ft.AddToCommandXML(sStepID, "//function/tests", "<test><eval input_type=\"text\" /><action input_type=\"text\" /></test>");
                }
                else if (iIndex == -1)
                {
                    //whereas an index of -1 means its the ONLY 'else' section
                    ft.AddToCommandXML(sStepID, "//function", "<else input_type=\"text\" />");
                }
                else
                {
                    //and of course a missing or 0 index is an error
                    throw new Exception("Unable to modify step. Invalid index.");
                }

                return;
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public void wmFnAddPair(string sStepID)
        {
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
            try
            {
                ft.AddToCommandXML(sStepID, "//function", "<pair><key input_type=\"text\"></key><value input_type=\"text\"></value></pair>");

                return;
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public void wmFnRemovePair(string sStepID, int iIndex)
        {
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
            try
            {
                if (iIndex > 0)
                {
                    ft.RemoveFromCommandXML(sStepID, "//function/pair[" + iIndex.ToString() + "]");

                    return;
                }
                else
                {
                    throw new Exception("Unable to modify step. Invalid index.");
                }
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public void wmFnWaitForTasksRemoveHandle(string sStepID, int iIndex)
        {
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
            try
            {
                if (iIndex > 0)
                {
                    ft.RemoveFromCommandXML(sStepID, "//function/handle[" + iIndex.ToString() + "]");

                    return;
                }
                else
                {
                    throw new Exception("Unable to modify step. Invalid index.");
                }
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public void wmFnWaitForTasksAddHandle(string sStepID)
        {
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
            try
            {
                ft.AddToCommandXML(sStepID, "//function", "<handle><name input_type=\"text\"></name></handle>");

                return;
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public void wmFnNodeArrayAdd(string sStepID, string sGroupNode)
        {
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
            try
            {
				//so, let's get the one we want from the XML template for this step... adjust the indexes, and add it.
				Function func = Function.GetFunctionForStep(sStepID);
				if (func == null)
					throw new Exception("Unable to look up Function definition for Step [" + sStepID + "] in Function class.");
				
				//validate it
				//parse the doc from the table
				XDocument xd = func.TemplateXDoc;
				if (xd == null) throw new Exception("Unable to get Function Template.");
				
				//get the original "group" node from the xml_template
				//here's the rub ... the "sGroupNode" from the actual command instance might have xpath indexes > 1... 
				//but the template DOESN'T!
				//So, I'm regexing any [#] on the string back to a [1]... that value should be in the template.
				
				Regex rx = new Regex(@"\[[0-9]*\]");
				string sTemplateNode = rx.Replace(sGroupNode, "[1]");
				
				XElement xGroupNode = xd.XPathSelectElement("//" + sTemplateNode);
				if (xGroupNode == null) throw new Exception("Error: Unable to add.  Source node not found in Template XML. [" + sTemplateNode + "]");
				
				//yeah, this wicked single line aggregates the string value of each node
				string sNewXML = xGroupNode.Nodes().Aggregate("", (str, node) => str += node.ToString());
				
				if (sNewXML != "")
					ft.AddNodeToXMLColumn("task_step", "function_xml", "step_id = '" + sStepID + "'", "//" + sGroupNode, sNewXML);
                return;
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        [WebMethod(EnableSession = true)]
        public void wmFnNodeArrayRemove(string sStepID, string sXPathToDelete)
        {
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
            try
            {
                //string sErr = "";

                ////gotta have a valid index
                //if (iIndex < 1)
                //    throw new Exception("Unable to modify step. Invalid index.");

                if (sStepID.Length > 0)
                {
                    if (sXPathToDelete != "")
                    {
                        ////so, let's get the XML for this step...
                        //string sXML = ft.GetStepCommandXML(sStepID, ref sErr);
                        //if (sErr != "") throw new Exception(sErr);

                        string sNodeToRemove = "//" + sXPathToDelete;

                        //validate it
                        //XDocument xd = XDocument.Parse(sXML);
                        //if (xd == null) throw new Exception("Error: Unable to parse Function XML.");

                        ft.RemoveNodeFromXMLColumn("task_step", "function_xml", "step_id = '" + sStepID + "'", sNodeToRemove);
                    }
                }
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }
        #endregion

        #region "Parameters"
        [WebMethod(EnableSession = true)]
        public string wmGetTaskParam(string sType, string sID, string sParamID)
        {
            dataAccess dc = new dataAccess();
            acUI.acUI ui = new acUI.acUI();

            if (!ui.IsGUID(sID))
                throw new Exception("Invalid or missing ID.");

            try
            {
                string sTable = "";

                if (sType == "ecosystem")
                    sTable = "ecosystem";
                else if (sType == "task")
                    sTable = "task";

                //default values if adding - get overridden if there is a record
                string sName = "";
                string sDesc = "";
                string sRequired = "false";
                string sPrompt = "true";
                string sEncrypt = "false";
                string sValuesHTML = "";
                string sPresentAs = "value";
				string sConstraint = "";
				string sConstraintMsg = "";										
				string sMinLength = "";
				string sMaxLength = "";
				string sMinValue = "";
				string sMaxValue = "";

                if (!string.IsNullOrEmpty(sParamID))
                {
                    string sErr = "";
                    string sXML = "";
                    string sSQL = "select parameter_xml" +
                            " from " + sTable +
                            " where " + sType + "_id = '" + sID + "'";

                    if (!dc.sqlGetSingleString(ref sXML, sSQL, ref sErr))
                        throw new Exception("Unable to get parameter_xml.  " + sErr);

                    if (sXML != "")
                    {
                        XDocument xd = XDocument.Parse(sXML);
                        if (xd == null) throw new Exception("XML parameter data is invalid.");

                        XElement xParameter = xd.XPathSelectElement("//parameter[@id = \"" + sParamID + "\"]");
                        if (xParameter == null) return "Error: XML does not contain parameter.";

                        XElement xName = xParameter.XPathSelectElement("name");
                        if (xName == null) return "Error: XML does not contain parameter name.";
						sName = xName.Value;

						XElement xDesc = xParameter.XPathSelectElement("desc");
                        if (xDesc != null)
							sDesc = xDesc.Value;

                        if (xParameter.Attribute("required") != null)
                            sRequired = xParameter.Attribute("required").Value;

                        if (xParameter.Attribute("prompt") != null)
                            sPrompt = xParameter.Attribute("prompt").Value;

                        if (xParameter.Attribute("encrypt") != null)
                            sEncrypt = xParameter.Attribute("encrypt").Value;

                        if (xParameter.Attribute("maxlength") != null)
                            sMaxLength = xParameter.Attribute("maxlength").Value;
                        if (xParameter.Attribute("maxvalue") != null)
                            sMaxValue = xParameter.Attribute("maxvalue").Value;
                        if (xParameter.Attribute("minlength") != null)
                            sMinLength = xParameter.Attribute("minlength").Value;
                        if (xParameter.Attribute("minvalue") != null)
                            sMinValue = xParameter.Attribute("minvalue").Value;

                        if (xParameter.Attribute("constraint") != null)
                            sConstraint = xParameter.Attribute("constraint").Value;

                        if (xParameter.Attribute("constraint_msg") != null)
                            sConstraintMsg = xParameter.Attribute("constraint_msg").Value;


                        XElement xValues = xd.XPathSelectElement("//parameter[@id = \"" + sParamID + "\"]/values");
                        if (xValues != null)
                        {
                            if (xValues.Attribute("present_as") != null)
                                sPresentAs = xValues.Attribute("present_as").Value;

                            int i = 0;
                            IEnumerable<XElement> xVals = xValues.XPathSelectElements("value");
                            foreach (XElement xVal in xVals)
                            {
                                //since we can delete each item from the page it needs a unique id.
                                string sPID = "pv" + ui.NewGUID();

                                string sValue = xVal.Value;
								string sObscuredValue = "";
								
								if (dc.IsTrue(sEncrypt))
								{
									// 1) obscure the ENCRYPTED value and make it safe to be an html attribute
				                    // 2) return some stars so the user will know a value is there.
									sObscuredValue = "oev=\"" + ui.packJSON(sValue) + "\"";
									sValue = (string.IsNullOrEmpty(sValue) ? "" : "********");
								}

                                sValuesHTML += "<div id=\"" + sPID + "\">" +
                                    "<textarea class=\"param_edit_value\" rows=\"1\" " + sObscuredValue + ">" + sValue + "</textarea>";

                                if (i > 0)
                                {
                                    string sHideDel = (sPresentAs == "list" || sPresentAs == "dropdown" ? "" : " hidden");
                                    sValuesHTML += " <img class=\"param_edit_value_remove_btn pointer " + sHideDel + "\" remove_id=\"" + sPID + "\"" +
                                        " src=\"../images/icons/fileclose.png\" alt=\"\" />";
                                }

                                sValuesHTML += "</div>";

                                i++;
                            }
                        }
                        else
                        {
                            //if, when getting the parameter, there are no values... add one.  We don't want a parameter with no values
                            //AND - no remove button on this only value
                            sValuesHTML += "<div id=\"pv" + ui.NewGUID() + "\">" +
                                "<textarea class=\"param_edit_value\" rows=\"1\"></textarea></div>";
                        }
                    }
                    else
                    {
                        throw new Exception("Unable to get parameter details. Not found.");
                    }
                }
                else
                {
                    //if, when getting the parameter, there are no values... add one.  We don't want a parameter with no values
                    //AND - no remove button on this only value
                    sValuesHTML += "<div id=\"pv" + ui.NewGUID() + "\">" +
                        "<textarea class=\"param_edit_value\" rows=\"1\"></textarea></div>";
                }

                //this draws no matter what, if it's empty it's just an add dialog
                string sHTML = "";

                sHTML += "Name: <input type=\"text\" class=\"w95pct\" id=\"param_edit_name\"" +
                    " validate_as=\"variable\" value=\"" + sName + "\" />";

                sHTML += "Options:<div class=\"param_edit_options\">";
                sHTML += "<span class=\"ui-widget-content ui-corner-all param_edit_option\"><input type=\"checkbox\" id=\"param_edit_required\"" + (sRequired == "true" ? "checked=\"checked\"" : "") + " /> <label for=\"param_edit_required\">Required?</label></span>";
                sHTML += "<span class=\"ui-widget-content ui-corner-all param_edit_option\"><input type=\"checkbox\" id=\"param_edit_prompt\"" + (sPrompt == "true" ? "checked=\"checked\"" : "") + " /> <label for=\"param_edit_prompt\">Prompt?</label></span>";
                sHTML += "<span class=\"ui-widget-content ui-corner-all param_edit_option\"><input type=\"checkbox\" id=\"param_edit_encrypt\"" + (sEncrypt == "true" ? "checked=\"checked\"" : "") + " /> <label for=\"param_edit_encrypt\">Encrypt?</label></span>";

				sHTML += "<hr />";

				sHTML += "Min / Max Length: <input type=\"text\" class=\"w25px\" id=\"param_edit_minlength\"" +
                    " validate_as=\"posint\" value=\"" + sMinLength + "\" /> / " +
					" <input type=\"text\" class=\"w25px\" id=\"param_edit_maxlength\"" +
                    " validate_as=\"posint\" value=\"" + sMaxLength + "\" />" +
					"<br />";
				sHTML += "Min / Max Value: <input type=\"text\" class=\"w25px\" id=\"param_edit_minvalue\"" +
                    " validate_as=\"number\" value=\"" + sMinValue + "\" /> / " +
					" <input type=\"text\" class=\"w25px\" id=\"param_edit_maxvalue\"" +
                    " validate_as=\"number\" value=\"" + sMaxValue + "\" />" +
					"<br />";
				sHTML += "Constraint: <input type=\"text\" class=\"w95pct\" id=\"param_edit_constraint\"" +
                    " value=\"" + sConstraint + "\" /><br />";
				sHTML += "Constraint Help: <input type=\"text\" class=\"w95pct\" id=\"param_edit_constraint_msg\"" +
                    " value=\"" + sConstraintMsg + "\" /><br />";

				sHTML += "</div>";

                sHTML += "<br />Description: <br /><textarea id=\"param_edit_desc\" rows=\"2\">" + sDesc + "</textarea>";

				sHTML += "<div id=\"param_edit_values\">Values:<br />";
                sHTML += "Present As: <select id=\"param_edit_present_as\">";
                sHTML += "<option value=\"value\"" + (sPresentAs == "value" ? "selected=\"selected\"" : "") + ">Value</option>";
                sHTML += "<option value=\"list\"" + (sPresentAs == "list" ? "selected=\"selected\"" : "") + ">List</option>";
                sHTML += "<option value=\"dropdown\"" + (sPresentAs == "dropdown" ? "selected=\"selected\"" : "") + ">Dropdown</option>";
                sHTML += "</select>";

                sHTML += "<hr />" + sValuesHTML + "</div>";

                //if it's not available for this presentation type, it will get the "hidden" class but still be drawn
                string sHideAdd = (sPresentAs == "list" || sPresentAs == "dropdown" ? "" : " hidden");
                sHTML += "<div id=\"param_edit_value_add_btn\" class=\"pointer " + sHideAdd + "\">" +
                    "<img title=\"Add Another\" alt=\"\" src=\"../images/icons/edit_add.png\" style=\"width: 10px;" +
                    "   height: 10px;\" />( click to add a value )</div>";

                return sHTML;
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }
        [WebMethod(EnableSession = true)]
        public string wmUpdateTaskParam(string sType, string sID, string sParamID,
            string sName, string sDesc,
            string sRequired, string sPrompt, string sEncrypt, string sPresentAs, string sValues,
            string sMinLength, string sMaxLength, string sMinValue, string sMaxValue, string sConstraint, string sConstraintMsg)
        {
            dataAccess dc = new dataAccess();

            acUI.acUI ui = new acUI.acUI();
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();

            if (!ui.IsGUID(sID))
                throw new Exception("Invalid or missing ID.");

            string sErr = "";
            string sSQL = "";


            //we encoded this in javascript before the ajax call.
            //the safest way to unencode it is to use the same javascript lib.
            //(sometimes the javascript and .net libs don't translate exactly, google it.)
            sDesc = ui.unpackJSON(sDesc).Trim();
			sConstraint = ui.unpackJSON(sConstraint);
			sConstraintMsg = ui.unpackJSON(sConstraintMsg).Trim();
			
            //normalize and clean the values
            sRequired = (dc.IsTrue(sRequired) ? "true" : "false");
            sPrompt = (dc.IsTrue(sPrompt) ? "true" : "false");
            sEncrypt = (dc.IsTrue(sEncrypt) ? "true" : "false");
            sName = sName.Trim().Replace("'", "''");


            string sTable = "";
            string sXML = "";
            string sParameterXPath = "//parameter[@id = \"" + sParamID + "\"]";  //using this to keep the code below cleaner.

            if (sType == "ecosystem")
                sTable = "ecosystem";
            else if (sType == "task")
                sTable = "task";

            bool bParamAdd = false;
            //bool bParamUpdate = false;

            //if sParamID is empty, we are adding
            if (string.IsNullOrEmpty(sParamID))
            {
                sParamID = "p_" + ui.NewGUID();
                sParameterXPath = "//parameter[@id = \"" + sParamID + "\"]";  //reset this if we had to get a new id


                //does the task already have parameters?
                sSQL = "select parameter_xml from " + sTable + " where " + sType + "_id = '" + sID + "'";
                if (!dc.sqlGetSingleString(ref sXML, sSQL, ref sErr))
                    throw new Exception(sErr);

                string sAddXML = "<parameter id=\"" + sParamID + "\"" +
					" required=\"" + sRequired + "\" prompt=\"" + sPrompt + "\" encrypt=\"" + sEncrypt + "\"" +
					" minlength=\"" + sMinLength + "\" maxlength=\"" + sMaxLength + "\"" +
					" minvalue=\"" + sMinValue + "\" maxvalue=\"" + sMaxValue + "\"" +
					" constraint=\"" + sConstraint + "\" constraint_msg=\"" + sConstraintMsg + "\"" +
					">" +						
                    "<name>" + sName + "</name>" +
                    "<desc>" + sDesc + "</desc>" +
                    "</parameter>";

                if (string.IsNullOrEmpty(sXML))
                {
                    //XML doesn't exist at all, add it to the record
                    sAddXML = "<parameters>" + sAddXML + "</parameters>";

                    sSQL = "update " + sTable + " set " +
                        " parameter_xml = '" + sAddXML + "'" +
                        " where " + sType + "_id = '" + sID + "'";

                    if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                        throw new Exception(sErr);

                    bParamAdd = true;
                }
                else
                {
                    //XML exists, add the node to it
                    ft.AddNodeToXMLColumn(sTable, "parameter_xml", sType + "_id = '" + sID + "'", "//parameters", sAddXML);
                    bParamAdd = true;
                }
            }
            else
            {
                //update the node values
                ft.SetNodeValueinXMLColumn(sTable, "parameter_xml", sType + "_id = '" + sID + "'", sParameterXPath + "/name", sName);
                ft.SetNodeValueinXMLColumn(sTable, "parameter_xml", sType + "_id = '" + sID + "'", sParameterXPath + "/desc", sDesc);
                //and the attributes
                ft.SetNodeAttributeinXMLColumn(sTable, "parameter_xml", sType + "_id = '" + sID + "'", sParameterXPath, "required", sRequired);
                ft.SetNodeAttributeinXMLColumn(sTable, "parameter_xml", sType + "_id = '" + sID + "'", sParameterXPath, "prompt", sPrompt);
                ft.SetNodeAttributeinXMLColumn(sTable, "parameter_xml", sType + "_id = '" + sID + "'", sParameterXPath, "encrypt", sEncrypt);
                ft.SetNodeAttributeinXMLColumn(sTable, "parameter_xml", sType + "_id = '" + sID + "'", sParameterXPath, "minlength", sMinLength);
                ft.SetNodeAttributeinXMLColumn(sTable, "parameter_xml", sType + "_id = '" + sID + "'", sParameterXPath, "maxlength", sMaxLength);
                ft.SetNodeAttributeinXMLColumn(sTable, "parameter_xml", sType + "_id = '" + sID + "'", sParameterXPath, "minvalue", sMinValue);
                ft.SetNodeAttributeinXMLColumn(sTable, "parameter_xml", sType + "_id = '" + sID + "'", sParameterXPath, "maxvalue", sMaxValue);
                ft.SetNodeAttributeinXMLColumn(sTable, "parameter_xml", sType + "_id = '" + sID + "'", sParameterXPath, "constraint", sConstraint);
                ft.SetNodeAttributeinXMLColumn(sTable, "parameter_xml", sType + "_id = '" + sID + "'", sParameterXPath, "constraint_msg", sConstraintMsg);

                bParamAdd = false;
            }


            // not clean at all handling both tasks and ecosystems in the same method, but whatever.
            if (bParamAdd)
            {
                if (sType == "task") { ui.WriteObjectAddLog(Globals.acObjectTypes.Task, sID, "Parameter", "Added Parameter:" + sName ); };
                if (sType == "ecosystem") { ui.WriteObjectAddLog(Globals.acObjectTypes.Ecosystem, sID, "Parameter", "Added Parameter:" + sName); };
            }
            else
            {
                // would be a lot of trouble to add the from to, why is it needed you have each value in the log, just scroll back
                // so just add a changed message to the log
                if (sType == "task") { dc.addSecurityLog(ui.GetSessionUserID(), Globals.SecurityLogTypes.Object, Globals.SecurityLogActions.ObjectModify, Globals.acObjectTypes.Task, sID, "Parameter Changed:[" + sName + "]", ref sErr); };
                if (sType == "ecosystem") { dc.addSecurityLog(ui.GetSessionUserID(), Globals.SecurityLogTypes.Object, Globals.SecurityLogActions.ObjectModify, Globals.acObjectTypes.Ecosystem, sID, "Parameter Changed:[" + sName + "]", ref sErr); };
            }

            //update the values
            string[] aValues = sValues.Split('|');
            string sValueXML = "";

            foreach (string sVal in aValues)
            {
                string sReadyValue = "";
				
				//if encrypt is true we MIGHT want to encrypt this value.
				//but it might simply be a resubmit of an existing value in which case we DON'T
				//if it has oev: as a prefix, it needs no additional work
				if (dc.IsTrue(sEncrypt))
				{
					if (sVal.IndexOf("oev:") > -1)
						sReadyValue = ui.unpackJSON(sVal.Replace("oev:", ""));
					else
						sReadyValue = dc.EnCrypt(ui.unpackJSON(sVal));						
				} else {
					sReadyValue = ui.unpackJSON(sVal);						
				}
				
                sValueXML += "<value id=\"pv_" + ui.NewGUID() + "\">" + sReadyValue + "</value>";
            }

            sValueXML = "<values present_as=\"" + sPresentAs + "\">" + sValueXML + "</values>";


            //whack-n-add
            ft.RemoveNodeFromXMLColumn(sTable, "parameter_xml", sType + "_id = '" + sID + "'", sParameterXPath + "/values");
            ft.AddNodeToXMLColumn(sTable, "parameter_xml", sType + "_id = '" + sID + "'", sParameterXPath, sValueXML);

            return "";
        }
        [WebMethod(EnableSession = true)]
        public string wmDeleteTaskParam(string sType, string sID, string sParamID)
        {
            dataAccess dc = new dataAccess();

            acUI.acUI ui = new acUI.acUI();
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();

            string sErr = "";
            string sSQL = "";
            string sTable = "";

            if (sType == "ecosystem")
                sTable = "ecosystem";
            else if (sType == "task")
                sTable = "task";

            if (!string.IsNullOrEmpty(sParamID) && ui.IsGUID(sID))
            {
                // need the name and values for logging
                string sXML = "";

                sSQL = "select parameter_xml" +
                    " from " + sTable +
                    " where " + sType + "_id = '" + sID + "'";

                if (!dc.sqlGetSingleString(ref sXML, sSQL, ref sErr))
                    throw new Exception("Unable to get parameter_xml.  " + sErr);

                if (sXML != "")
                {
                    XDocument xd = XDocument.Parse(sXML);
                    if (xd == null) throw new Exception("XML parameter data is invalid.");

                    XElement xName = xd.XPathSelectElement("//parameter[@id = \"" + sParamID + "\"]/name");
                    string sName = (xName == null ? "" : xName.Value);
                    XElement xValues = xd.XPathSelectElement("//parameter[@id = \"" + sParamID + "\"]/values");
                    string sValues = (xValues == null ? "" : xValues.ToString());

                    // add security log
                    ui.WriteObjectDeleteLog(Globals.acObjectTypes.Parameter, "", sID, "");

                    if (sType == "task") { ui.WriteObjectChangeLog(Globals.acObjectTypes.Task, sID, "Deleted Parameter:[" + sName + "]", sValues); };
                    if (sType == "ecosystem") { ui.WriteObjectChangeLog(Globals.acObjectTypes.Ecosystem, sID, "Deleted Parameter:[" + sName + "]", sValues); };
                }


                //do the whack
                ft.RemoveNodeFromXMLColumn(sTable, "parameter_xml", sType + "_id = '" + sID + "'", "//parameter[@id = \"" + sParamID + "\"]");


                return "";
            }
            else
            {
                throw new Exception("Invalid or missing Task or Parameter ID.");
            }
        }
		/*
		 * wmGetParameters returns a presentable, HTML list of parameters.
		 * it does appear on the Task Edit page, and is editable...
		 * ...but it's editable in a popup for a single value... not anything done here.
		 * 
		 * all we do here is give the label a pointer if it's editable.
		 * 
		 * */
        [WebMethod(EnableSession = true)]
        public string wmGetParameters(string sType, string sID, bool bEditable, bool bSnipValues)
        {
            dataAccess dc = new dataAccess();
            acUI.acUI ui = new acUI.acUI();

            try
            {
                string sErr = "";
                string sParameterXML = "";
                string sSQL = "";
                string sTable = "";

                if (sType == "ecosystem")
                    sTable = "ecosystem";
                else if (sType == "task")
                    sTable = "task";

                sSQL = "select parameter_xml from " + sTable + " where " + sType + "_id = '" + sID + "'";

                if (!dc.sqlGetSingleString(ref sParameterXML, sSQL, ref sErr))
                {
                    throw new Exception(sErr);
                }

                if (sParameterXML != "")
                {
                    XDocument xDoc = XDocument.Parse(sParameterXML);
                    if (xDoc == null)
                        throw new Exception("Parameter XML data for " + sType + " [" + sID + "] is invalid.");

                    XElement xParams = xDoc.XPathSelectElement("/parameters");
                    if (xParams == null)
                        throw new Exception("Parameter XML data for " + sType + " [" + sID + "] does not contain 'parameters' root node.");


                    string sHTML = "";

                    foreach (XElement xParameter in xParams.XPathSelectElements("parameter"))
                    {
                        string sPID = xParameter.Attribute("id").Value;
                        string sName = xParameter.Element("name").Value;
                        string sDesc = xParameter.Element("desc").Value;

                        bool bEncrypt = false;
                        if (xParameter.Attribute("encrypt") != null)
                            bEncrypt = dc.IsTrue(xParameter.Attribute("encrypt").Value);


                        sHTML += "<div class=\"parameter\">";
                        sHTML += "  <div class=\"ui-state-default parameter_header\">";

                        sHTML += "<div class=\"step_header_title\"><span class=\"parameter_name";
                        sHTML += (bEditable ? " pointer" : ""); //make the name a pointer if it's editable
                        sHTML += "\" id=\"" + sPID + "\">";
                        sHTML += sName;
                        sHTML += "</span></div>";

                        sHTML += "<div class=\"step_header_icons\">";
                        sHTML += "<img class=\"parameter_help_btn pointer trans50\"" +
                            " src=\"../images/icons/info.png\" alt=\"\" style=\"width: 12px; height: 12px;\"" +
                            " title=\"" + sDesc.Replace("\"", "") + "\" />";

                        if (bEditable)
                        {
                            sHTML += "<img class=\"parameter_remove_btn pointer\" remove_id=\"" + sPID + "\"" +
                                " src=\"../images/icons/fileclose.png\" alt=\"\" style=\"width: 12px; height: 12px;\" />";
                        }

                        sHTML += "</div>";
                        sHTML += "</div>";


                        sHTML += "<div class=\"ui-widget-content ui-corner-bottom clearfloat parameter_detail\">";

                        //desc - a short snip is shown here... 75 chars.

                        //if (!string.IsNullOrEmpty(sDesc))
                        //    if (bSnipValues)
                        //        sDesc = ui.GetSnip(sDesc, 75);
                        //    else
                        //        sDesc = ui.FixBreaks(sDesc);
                        //sHTML += "<div class=\"parameter_desc hidden\">" + sDesc + "</div>";


                        //values
                        XElement xValues = xParameter.XPathSelectElement("values");
                        if (xValues != null)
                        {
                            foreach (XElement xValue in xValues.XPathSelectElements("value"))
                            {
                                string sValue = (string.IsNullOrEmpty(xValue.Value) ? "" : xValue.Value);

                                //only show stars IF it's encrypted, but ONLY if it has a value
                                if (bEncrypt && !string.IsNullOrEmpty(sValue))
									sValue = "********";
								else
                                    if (bSnipValues)
                                        sValue = ui.GetSnip(xValue.Value, 64);
                                    else
                                        sValue = ui.FixBreaks(xValue.Value);

                                sHTML += "<div class=\"ui-widget-content ui-corner-tl ui-corner-bl parameter_value\">" + sValue + "</div>";
                            }
                        }

                        sHTML += "</div>";
                        sHTML += "</div>";

                    }

                    return sHTML;
                }
            }
            catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }

            //it may just be there are no parameters
            return "";
        }


        /*
         This gets the complete XML parameter document, for the purposes of launching or saving defaults.
         For Tasks, it's taken right from the task table...
         For others, it's merged in with the saved default values.
         * 
         * CRITICAL REMINDER NOTE!!!!
         * 
         * We ALWAYS wanna do merging unless you're looking at the task.
         * Why?  because the task could have had new parameters added since you saved them on the other object.
         * therefore, we always merge in order to expose those new parameters.
        */
        [WebMethod(EnableSession = true)]
        public string wmGetParameterXML(string sType, string sID, string sFilterByEcosystemID)
        {
            if (sType == "task")
                return wmGetObjectParameterXML(sType, sID, "");
            else
                return wmGetMergedParameterXML(sType, sID, sFilterByEcosystemID); //Merging is happening here!
        }


        ///*
        // * This method does MERGING!
        // * 
        // * It gets the XML for the Task, and additionally get the XML for the other record,
        // * and merges them together, using the values from one to basically select values in 
        // * the master task XML.
        // * 
        // * */
        [WebMethod(EnableSession = true)]
        public string wmGetMergedParameterXML(string sType, string sID, string sEcosystemID)
        {

            dataAccess dc = new dataAccess();
            acUI.acUI ui = new acUI.acUI();
            taskMethods tm = new taskMethods();
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();

            if (string.IsNullOrEmpty(sID))
                throw new Exception("ID required to look up default Parameter values.");

            string sErr = "";

            //what is the task associated with this action?
            //and get the XML for it
            string sSQL = "";
            string sDefaultsXML = "";
            string sTaskID = "";

            if (sType == "action")
            {
                sDefaultsXML = tm.wmGetObjectParameterXML(sType, sID, "");

                sSQL = "select t.task_id" +
                     " from ecotemplate_action ea" +
                     " join task t on ea.original_task_id = t.original_task_id" +
                     " and t.default_version = 1" +
                     " where ea.action_id = '" + sID + "'";
            }
			else  if (sType == "runtask")
            {
				//RunTask is actually a command type
                //but it's very very similar to an Action.
				//so... it handles it's params like an action... more or less.
				
				//HACK ALERT!  Since we are dealing with a unique case here where we have and need both the 
				//step_id AND the target task_id, we're piggybacking a value in.
				//the sID is the STEP_ID (which is kindof equivalient to the action)
				//the sEcosystemID is the target TASK_ID
				//yes, it's a hack I know... but better than adding another argument everywhere... sue me.
				
				//NOTE: plus, don't get confused... yes, run task references tasks by original id and version, but we already worked that out.
				//the sEcosystemID passed in to this function is already resolved to an explicit task_id... it's the right one.

				//get the parameters off the step itself.
				//which is also goofy, as they are embedded *inside* the function xml of the step.
				//but don't worry that's handled in here
				sDefaultsXML = tm.wmGetObjectParameterXML(sType, sID, "");
				
				//now, we will want to get the parameters for the task *referenced by the command* down below
				//but no sql is necessary to get the ID... we already know it!
                sTaskID = sEcosystemID;
				
            }
            else if (sType == "instance")
            {
                sDefaultsXML = tm.wmGetObjectParameterXML(sType, sID, sEcosystemID);

                //IMPORTANT!!! if the ID is not a guid, it's a specific instance ID, and we'll need to get the task_id
                //but if it is a GUID, but the type is "instance", taht means the most recent INSTANCE for this TASK_ID
                if (ui.IsGUID(sID))
                    sTaskID = sID;
                else
                    sSQL = "select task_id" +
                         " from task_instance" +
                         " where task_instance = '" + sID + "'";
            }
            else if (sType == "plan")
            {
                sDefaultsXML = tm.wmGetObjectParameterXML(sType, sID, "");

                sSQL = "select task_id" +
                    " from action_plan" +
                    " where plan_id = '" + sID + "'";
            }
            else if (sType == "schedule")
            {
                sDefaultsXML = tm.wmGetObjectParameterXML(sType, sID, "");

                sSQL = "select task_id" +
                    " from action_schedule" +
                    " where schedule_id = '" + sID + "'";
            }


			//if we didn't get a task id directly, use the SQL to look it up
            if (string.IsNullOrEmpty(sTaskID))
                if (!dc.sqlGetSingleString(ref sTaskID, sSQL, ref sErr))
                    throw new Exception(sErr);

            if (!ui.IsGUID(sTaskID))
                throw new Exception("Unable to find Task ID for record.");


            XDocument xTPDoc = new XDocument();
            XDocument xDefDoc = new XDocument();

            //get the parameter XML from the TASK
            string sTaskParamXML = tm.wmGetParameterXML("task", sTaskID, "");
            if (!string.IsNullOrEmpty(sTaskParamXML))
            {
                xTPDoc = XDocument.Parse(sTaskParamXML);
                if (xTPDoc == null)
                    throw new Exception("Task Parameter XML data is invalid.");

                XElement xTPParams = xTPDoc.XPathSelectElement("/parameters");
                if (xTPParams == null)
                    throw new Exception("Task Parameter XML data does not contain 'parameters' root node.");
            }


            //we populated this up above too
            if (!string.IsNullOrEmpty(sDefaultsXML))
            {
                xDefDoc = XDocument.Parse(sDefaultsXML);
                if (xDefDoc == null)
                    throw new Exception("Defaults XML data is invalid.");

                XElement xDefParams = xDefDoc.XPathSelectElement("//parameters");
                if (xDefParams == null)
                    throw new Exception("Defaults XML data does not contain 'parameters' node.");
            }

            //spin the nodes in the DEFAULTS xml, then dig in to the task XML and UPDATE the value if found.
            //(if the node no longer exists, delete the node from the defaults xml IF IT WAS AN ACTION)
            //and default "values" take precedence over task values.
            foreach (XElement xDefault in xDefDoc.XPathSelectElements("//parameter"))
            {
				//nothing to do if it's empty
				if (xDefault == null)
					break;

				//look it up in the task param xml
                XElement xDefName = xDefault.XPathSelectElement("name");
                string sDefName = (xDefName == null ? "" : xDefName.Value);
                XElement xDefValues = xDefault.XPathSelectElement("values");
				
				//nothing to do if there is no values node...
				if (xDefValues == null)
					break;
				//or if it contains no values.
				if (!xDefValues.HasElements)
					break;
				//or if there is no parameter name
				if (string.IsNullOrEmpty(sDefName))
					break;
				
				
				//so, we have some valid data in the defaults xml... let's merge!
				
				//we have the name of the parameter... go find it in the TASK param XML
                XElement xTaskParam = xTPDoc.XPathSelectElement("//parameter/name[. = '" + sDefName + "']/..");  //NOTE! the /.. gets the parent of the name node!

                //if it doesn't exist in the task params, remove it from this document, permanently
                //but only for action types... instance data is historical and can't be munged
                if (xTaskParam == null && sType == "action")
                {
                    ft.RemoveNodeFromXMLColumn("ecotemplate_action", "parameter_defaults", "action_id = '" + sID + "'", "//parameter/name[. = '" + sDefName + "']/..");
                    continue;
                }


				//is this an encrypted parameter?
				string sEncrypt = "";
				if (xTaskParam.Attribute("encrypt") != null)
                	sEncrypt = xTaskParam.Attribute("encrypt").Value;

 
				//and the "values" collection will be the 'next' node
                XElement xTaskParamValues = xTaskParam.XPathSelectElement("values");

                string sPresentAs = xTaskParamValues.Attribute("present_as").Value;
                if (sPresentAs == "dropdown")
                {
                    //dropdowns get a "selected" indicator
                    string sValueToSelect = xDefValues.XPathSelectElement("value").Value;

                    //find the right one by value and give it the "selected" attribute.
                    XElement xVal = xTaskParamValues.XPathSelectElement("value[. = '" + sValueToSelect + "']");
                    if (xVal != null)
                        xVal.SetAttributeValue("selected", "true");
                }
                else if (sPresentAs == "list")
                {
                    //first, a list gets ALL the values replaced...
                    xTaskParamValues.ReplaceNodes(xDefValues);
               	}
                else
                {
					//IMPORTANT NOTE:
					//remember... both these XML documents came from wmGetObjectParameterXML...
					//so any encrypted data IS ALREADY OBFUSCATED and base64'd in the oev attribute.
					
                    //it's a single value, so just replace it with the default.
                    XElement xVal = xTaskParamValues.XPathSelectElement("value[1]");
                    if (xVal != null)
					{
						//if this is an encrypted parameter, we'll be replacing (if a default exists) the oev attribute
						//AND the value... don't want them to get out of sync!
						if (dc.IsTrue(sEncrypt))
						{
							if (xDefValues.XPathSelectElement("value") != null)
								if (xDefValues.XPathSelectElement("value").Attribute("oev") != null)
								{
									xVal.SetAttributeValue("oev", xDefValues.XPathSelectElement("value").Attribute("oev").Value);
									xVal.Value = xDefValues.XPathSelectElement("value").Value;
								}
						}
						else
						{
							//not encrypted, just replace the value.
							if (xDefValues.XPathSelectElement("value") != null)
								xVal.Value = xDefValues.XPathSelectElement("value").Value;
						}
					}
				}
            }

            return xTPDoc.ToString(SaveOptions.DisableFormatting); ;

        }



        ///*
        // This method simply gets the XML directly from the db for the type.
        // It may be different by type!

        // The schema should be the same, but some documents (task) are complete, while
        // others (action, instance) are JUST VALUES, not the complete document.
        //*/
        [WebMethod(EnableSession = true)]
        public string wmGetObjectParameterXML(string sType, string sID, string sFilterByEcosystemID)
        {
            dataAccess dc = new dataAccess();

            acUI.acUI ui = new acUI.acUI();

            try
            {
                string sErr = "";
                string sParameterXML = "";
                string sSQL = "";

                if (sType == "instance")
                {
                    //if sID is a guid, it's a task_id ... get the most recent run
                    //otherwise assume it's a task_instance and try that.
                    if (ui.IsGUID(sID))
                        sSQL = "select parameter_xml from task_instance_parameter where task_instance = " +
                            "(select max(task_instance) from task_instance where task_id = '" + sID + "')";
                    else if (ui.IsGUID(sFilterByEcosystemID))  //but if there's an ecosystem_id, limit it to that
                        sSQL = "select parameter_xml from task_instance_parameter where task_instance = " +
                            "(select max(task_instance) from task_instance where task_id = '" + sID + "')" +
                            " and ecosystem_id = '" + sFilterByEcosystemID + "'";
                    else
                        sSQL = "select parameter_xml from task_instance_parameter where task_instance = '" + sID + "'";
                }
                else if (sType == "runtask")
                {
					// in this case, sID is actually a *step_id* !
					//sucks that MySql doesn't have decent XML functions... we gotta do string manipulation grr...
                    sSQL = "select substring(function_xml," + 
						" locate('<parameters>', function_xml)," +
						" locate('</parameters>', function_xml) - locate('<parameters>', function_xml) + 13)" +
						" as parameter_xml" +
						" from task_step where step_id = '" + sID + "'";

				}
                else if (sType == "action")
                {
                    sSQL = "select parameter_defaults from ecotemplate_action where action_id = '" + sID + "'";
                }
                else if (sType == "plan")
                {
                    sSQL = "select parameter_xml from action_plan where plan_id = " + sID;
                }
                else if (sType == "schedule")
                {
                    sSQL = "select parameter_xml from action_schedule where schedule_id = '" + sID + "'";
                }
                else if (sType == "task")
                {
                    sSQL = "select parameter_xml from task where task_id = '" + sID + "'";
                }

                if (!dc.sqlGetSingleString(ref sParameterXML, sSQL, ref sErr))
                {
                    throw new Exception(sErr);
                }

                if (!string.IsNullOrEmpty(sParameterXML))
                {
                    XDocument xDoc = XDocument.Parse(sParameterXML);
                    if (xDoc == null)
                        throw new Exception("Parameter XML data for [" + sType + ":" + sID + "] is invalid.");

                    XElement xParams = xDoc.XPathSelectElement("//parameters");
                    if (xParams == null)
                        throw new Exception("Parameter XML data for[" + sType + ":" + sID + "] does not contain 'parameters' node.");
					
                    //NOTE: some values on this document may have a "encrypt" attribute.
					//If so, we will:
					// 1) obscure the ENCRYPTED value and make it safe to be an html attribute
                    // 2) return some stars so the user will know a value is there.
                    foreach (XElement xEncryptedValue in xDoc.XPathSelectElements("//parameter[@encrypt='true']/values/value"))
                    {
						//if the value is empty, it still gets an oev attribute
						string sVal = (string.IsNullOrEmpty(xEncryptedValue.Value) ? "" : ui.packJSON(xEncryptedValue.Value));
						xEncryptedValue.SetAttributeValue("oev", sVal);
						//but it only gets stars if it has a value
						if (!string.IsNullOrEmpty(sVal))
                        	xEncryptedValue.Value = "********";
                    }

                    return xDoc.ToString(SaveOptions.DisableFormatting);
                }
            }
            catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }

            //it may just be there are no parameters
            return "";
        }



        #endregion

        [WebMethod(EnableSession = true)]
        public string wmGetAccountEcosystems(string sAccountID, string sEcosystemID)
        {
            dataAccess dc = new dataAccess();

            string sHTML = "";

            try
            {
                //if the ecosystem passed in isn't really there, make it "" so we can compare below.
                if (string.IsNullOrEmpty(sEcosystemID))
                    sEcosystemID = "";

                if (!string.IsNullOrEmpty(sAccountID))
                {
                    string sErr = "";
                    string sSQL = "select ecosystem_id, ecosystem_name from ecosystem" +
                         " where account_id = '" + sAccountID + "'" +
                         " order by ecosystem_name"; ;

                    DataTable dtEcosystems = new DataTable();
                    if (dc.sqlGetDataTable(ref dtEcosystems, sSQL, ref sErr))
                    {
                        if (dtEcosystems.Rows.Count > 0)
                        {
                            sHTML += "<option value=''></option>";

                            foreach (DataRow dr in dtEcosystems.Rows)
                            {
                                string sSelected = (sEcosystemID == dr["ecosystem_id"].ToString() ? "selected=\"selected\"" : "");
                                sHTML += "<option value=\"" + dr["ecosystem_id"].ToString() + "\" " + sSelected + ">" + dr["ecosystem_name"].ToString() + "</option>";
                            }
                        }
                    };
                }

                return sHTML;
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        public void wmSaveTaskUserSetting(string sTaskID, string sSettingKey, string sSettingValue)
        {
            acUI.acUI ui = new acUI.acUI();

            try
            {
                string sUserID = ui.GetSessionUserID();

                if (ui.IsGUID(sTaskID) && ui.IsGUID(sUserID))
                {
                    //1) get the settings
                    //2) update/add the appropriate value
                    //3) update the settings to the db

					XDocument xDoc = (XDocument)ui.GetSessionObject("user_settings", "Security");
					if (xDoc == null) return;

                    //we have to analyze the doc and see if the appropriate section exists.
                    //if not, we need to construct it
                    if (xDoc.Element("settings").Descendants("debug").Count() == 0)
                        xDoc.Element("settings").Add(new XElement("debug"));

                    if (xDoc.Element("settings").Element("debug").Descendants("tasks").Count() == 0)
                        xDoc.Element("settings").Element("debug").Add(new XElement("tasks"));

                    XElement xTasks = xDoc.Element("settings").Element("debug").Element("tasks");


                    //to search by attribute we must get back an array and we shouldn't have an array anyway
                    //so to be safe and clean, delete all matches and just add back the one we want
                    xTasks.Descendants("task").Where(
                        x => (string)x.Attribute("task_id") == sTaskID).Remove();


                    //add it
                    XElement xTask = new XElement("task");
                    xTask.Add(new XAttribute("task_id", sTaskID));
                    xTask.Add(new XAttribute(sSettingKey, sSettingValue));

                    xTasks.Add(xTask);

					//put it back in the session
					ui.SetSessionObject("user_settings", xDoc, "Security");			

                    return;
                }
                else
                {
                    throw new Exception("Unable to run task. Missing or invalid task [" + sTaskID + "] or unable to get current user.");
                }

            }
            catch (Exception ex)
            {
                throw ex;
            }
        }
    }
}
