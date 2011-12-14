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
using System.Data;
using System.Linq;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Xml.Linq;
using System.Xml.XPath;
using Globals;

namespace Web.pages
{
    public partial class taskEdit : System.Web.UI.Page
    {
        dataAccess dc = new dataAccess();
        acUI.acUI ui = new acUI.acUI();
        ACWebMethods.taskMethods tm = new ACWebMethods.taskMethods();
		
		//Get a global Task object for this task
		Task oTask;
		string sTaskID;
        protected void Page_Load(object sender, EventArgs e)
        {
            string sErr = "";
			
            sTaskID = ui.GetQuerystringValue("task_id", typeof(string)).ToString();
            //sQSCodeblock = ui.GetQuerystringValue("codeblock_name", typeof(string)).ToString();

			//instantiate the new Task object
			oTask = new Task(sTaskID, ref sErr);

            if (!Page.IsPostBack)
            {
				hidTaskID.Value = sTaskID;
                //the initial value of the Codeblock is always "MAIN"
                hidCodeblockName.Value = "MAIN";

                if (!GetDetails(ref sErr))
                {
                    ui.RaiseError(Page, "Unable to continue.  Task record not found for task_id [" + sTaskID + "].<br />" + sErr, true, "");
                    return;
                }

                //categories and functions
                if (!GetCategories(ref sErr))
                {
                    ui.RaiseError(Page, "Unable to continue.  No categories defined.<br />" + sErr, true, "");
                    return;
                }

                //get debug information
                if (!GetDebug(ref sErr))
                {
                    ui.RaiseError(Page, "Error getting Debugging information.<br />" + sErr, true, "");
                    return;
                }

                //codeblocks
                if (!GetCodeblocks(ref sErr))
                {
                    ui.RaiseError(Page, "Unable to continue.  Could not retrieve Codeblocks. " + sErr, true, "");
                    return;
                }
            }
        }

        #region "Tabs"
        private bool GetDetails(ref string sErr)
        {
            try
            {
                if (oTask != null)
                {
                    //ATTENTION!
                    //Approved tasks CANNOT be edited.  So, if the status is approved... we redirect to the
                    //task 'view' page.
                    //this is to prevent any sort of attempts on the client to load an approved or otherwise 'locked' 
                    // version into the edit page.
                    if (oTask.Status == "Approved")
                    {
                        Response.Redirect("taskView.aspx?task_id=" + sTaskID, false);
                        return true;
                    }
                    //so, we are here, meaning we have an editable task.
                    txtTaskName.Text = oTask.Name;
                    txtTaskCode.Text = oTask.Code;
                    lblVersion.Text = oTask.Version;
                    lblCurrentVersion.Text = oTask.Version;

                    //chkDirect.Checked = oTask.UseConnectorSystem;

                    txtDescription.Text = oTask.Description;
                    txtConcurrentInstances.Text = oTask.ConcurrentInstances;
                    txtQueueDepth.Text = oTask.QueueDepth;

                    hidDefault.Value = (oTask.IsDefaultVersion ? "1" : "0");

                    hidOriginalTaskID.Value = oTask.OriginalTaskID;

                    //lblStatus.Text = dr["task_status"].ToString();
                    lblStatus2.Text = oTask.Status;

                    /*                    
                     * ok, this is important.
                     * there are some rules for the process of 'Approving' a task.
                     * specifically:
                     * -- if there are no other approved tasks in this family, this one will become the default.
                     * -- if there is another approved task in this family, we show the checkbox
                     * -- allowing the user to decide whether or not to make this one the default
                     */
                    if (oTask.NumberOfApprovedVersions > 0)
                        chkMakeDefault.Visible = true;
                    else
                        chkMakeDefault.Visible = false;



                    //the header
                    lblTaskNameHeader.Text = oTask.Name;
                    lblVersionHeader.Text = oTask.Version + (oTask.IsDefaultVersion ? " (default)" : "");
					
					//NSC: WHY?  Why is this just checking to see if it can get the max version, then doing nothing with it?
                    if (!GetMaxVersion(sTaskID, ref sErr)) return false;

                    //schedules (only if this is default)
                    if (oTask.IsDefaultVersion)
                    {
                        tab_schedules.Visible = true;
                    }
                    else
                        tab_schedules.Visible = false;

                    return true;
                }
                else
                {
                    return false;
                }
            }
            catch (Exception ex)
            {
                sErr = ex.Message;
                return false;
            }
        }
        private bool GetDebug(ref string sErr)
        {
            //valid task_instance statuses
            //Submitted, Processing, Queued, Completed, Error and Cancelled
            try
            {
                //get the last 'done' instance.
                string sSQL = "select ti.task_status, ti.submitted_dt, ti.started_dt, ti.completed_dt, ti.ce_node, ti.pid," +
                    " t.task_name, a.asset_name, u.full_name" +
                    " from tv_task_instance ti" +
                    " join task t on ti.task_id = t.task_id" +
                    " left outer join users u on ti.submitted_by = u.user_id" +
                    " left outer join asset a on ti.asset_id = a.asset_id" +
                    " where ti.task_instance = (" +
                        "select max(task_instance)" +
                        " from tv_task_instance" +
                        " where task_status in ('Cancelled','Completed','Error')" +
                        " and task_id = '" + sTaskID + "'";
                //if (ui.IsGUID(sAssetID))
                //{
                //    sSQL += " and asset_id = '" + sAssetID + "'";
                //}
                sSQL += ")";

                DataRow dr = null;
                if (!dc.sqlGetDataRow(ref dr, sSQL, ref sErr)) return false;

                if (dr != null)
                {
                    lblLastRunStatus.Text = dr["task_status"].ToString();
                    lblLastRunDT.Text = (dr["completed_dt"].Equals(System.DBNull.Value) ? "" : dr["completed_dt"].ToString());
                }
                else
                {
                    // bugzilla 1139, hide the link to the runlog if the task has never ran.
                    debug_view_latest_log.Visible = false;
                }

                //ok, is it currently running?
                //this is a different check than the one above
                sSQL = "select task_instance, task_status" +
                        " from tv_task_instance" +
                        " where task_instance = (" +
                            "select max(task_instance)" +
                            " from tv_task_instance" +
                            " where task_status in ('Submitted','Queued','Processing','Aborting','Staged')" +
                            " and task_id = '" + sTaskID + "'";
                //if (ui.IsGUID(sAssetID))
                //{
                //    sSQL += " and asset_id = '" + sAssetID + "'";
                //}
                sSQL += ")";

                if (!dc.sqlGetDataRow(ref dr, sSQL, ref sErr)) return false;

                if (dr != null)
                {
                    hidDebugActiveInstance.Value = dr["task_instance"].ToString();
                    lblCurrentStatus.Text = dr["task_status"].ToString();
                }
                else
                {
                    lblCurrentStatus.Text = "Inactive";
                }


                //see if any debug settings were saved for this user
                string sSettingXML = "";
                sSQL = "select settings_xml from users where user_id = '" + ui.GetSessionUserID() + "'";

                if (!dc.sqlGetSingleString(ref sSettingXML, sSQL, ref sErr))
                {
                    ui.RaiseError(Page, "Unable to get settings for user.<br />", false, sErr);
                }

                //we don't care to do anything if there were no settings
                if (sSettingXML != "")
                {
                    XDocument xDoc = XDocument.Parse(sSettingXML);
                    if (xDoc == null) ui.RaiseError(Page, "XML settings data for user is invalid.", false, "");

                    XElement xTask = xDoc.Descendants("task").Where(
                        x => (string)x.Attribute("task_id") == sTaskID).LastOrDefault();
                    if (xTask != null)
                    {
                        //yay! we have user settings...

                        //test asset?
                        string sDebugAssetID = "";
                        if (xTask.Attribute("asset_id") != null)
                        {
                            sDebugAssetID = xTask.Attribute("asset_id").Value.ToString();

                            if (ui.IsGUID(sDebugAssetID))
                            {
                                string sDebugAssetName = "";
                                sSQL = "select asset_name from asset where asset_id = '" + sDebugAssetID + "'";
                                if (!dc.sqlGetSingleString(ref sDebugAssetName, sSQL, ref sErr))
                                {
                                    ui.RaiseError(Page, "Unable to get asset name for asset [" + sDebugAssetID + "].<br />", false, sErr);
                                }

                                //txtTestAsset.Text = sDebugAssetName;
                                //txtTestAsset.Attributes["asset_id"] = sDebugAssetID;
                            }
                        }
                    }
                }


                return true;
            }
            catch (Exception ex)
            {
                throw ex;
            }

        }
        private bool GetCodeblocks(ref string sErr)
        {
			//TODO: this will need to move asap to a jquery ajax web method, because adding/deleting is using a MS ajax postback which is bad and wrong.
            try
            {
				string sCBHTML = "";
				
				foreach (Codeblock cb in oTask.Codeblocks.Values)
				{
					sCBHTML += "<li class=\"ui-widget-content ui-corner-all codeblock\" id=\"cb_" + cb.Name + "\">";
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
				ltCodeblocks.Text = sCBHTML;
				return true;
            }
            catch (Exception ex)
            {
                sErr = ex.Message;
                return false;
            }
        }
        private bool GetCategories(ref string sErr)
        {
            try
            {
				//so, we will use the FunctionCategories class in the session that was loaded at login, and build the list items for the commands tab.

				//not by a web method yet, baby steps ....
				
				FunctionCategories cats = ui.GetTaskFunctionCategories();
                if (cats == null)
                {
                    ui.RaiseError(Page, "Error: Task Function Categories class is not in the session.", false, "");
                } 
				else 
				{
					string sCatHTML = "";
					string sFunHTML = "";
					
					foreach (Category cat in cats.Values)
                    {
                        sCatHTML += "<li class=\"ui-widget-content ui-corner-all command_item category\"";
                        sCatHTML += " id=\"cat_" + cat.Name + "\"";
						sCatHTML += " name=\"" + cat.Name + "\">";
						sCatHTML += "<div>";
						sCatHTML += "<img class=\"category_icon\" src=\"../images/" + cat.Icon + "\" alt=\"\" />";
						sCatHTML += "<span>" + cat.Label + "</span>";
                        sCatHTML += "</div>";
                        sCatHTML += "<div id=\"help_text_" + cat.Name + "\" class=\"hidden\">";
						sCatHTML += cat.Description;
                        sCatHTML += "</div>";
                        sCatHTML += "</li>";
						
						
						sFunHTML += "<div class=\"functions hidden\" id=\"cat_" + cat.Name + "_functions\">";
						//now, let's work out the functions.
						//we can just draw them all... they are hidden and will display on the client as clicked
						foreach (Function fn in cat.Functions.Values)
	                    {
							sFunHTML += "<div class=\"ui-widget-content ui-corner-all command_item function\"";
	                        sFunHTML += " id=\"fn_" + fn.Name + "\"";
	                        sFunHTML += " name=\"" + fn.Name + "\">";
	                        sFunHTML += "<img class=\"function_icon\" src=\"../images/" + fn.Icon + "\" alt=\"\" />";
	                        sFunHTML += "<span>" + fn.Label + "</span>";
	                        sFunHTML += "<div id=\"help_text_" + fn.Name + "\" class=\"hidden\">";
	                        sFunHTML += fn.Description;
	                        sFunHTML += "</div>";
	                        sFunHTML += "</div>";
						}
						sFunHTML += "</div>";

					}
						
					ltCategories.Text = sCatHTML;
					ltFunctions.Text = sFunHTML;
					
				}
				
				return true;
				
            }
            catch (Exception ex)
            {
                sErr = ex.Message;
                return false;

            }
        }
        #endregion
 
        #region "Buttons"
        protected void btnCBRefresh_Click(object sender, System.EventArgs e)
        {
            string sErr = "";
            if (!GetCodeblocks(ref sErr))
            {
                ui.RaiseError(Page, "Error getting codeblocks:" + sErr, true, "");
            }
        }
        #endregion

        private bool GetMaxVersion(string sTaskID, ref string sErr)
        {
            try
            {
                string sMaxVer = tm.wmGetTaskMaxVersion(sTaskID, ref sErr);

                if (!string.IsNullOrEmpty(sMaxVer))
                {
                    lblNewMinor.Text = "New Minor Version (" + String.Format("{0:0.000}", (Convert.ToDouble(sMaxVer) + .001)) + ")";
                    lblNewMajor.Text = "New Major Version (" + String.Format("{0:0.000}", Math.Round((Convert.ToDouble(sMaxVer) + .5), MidpointRounding.AwayFromZero)) + ")";

                    return true;
                };
                return false;
            }
            catch (Exception ex)
            {
                sErr = ex.Message;
                return false;
            }
        }

    }
}
