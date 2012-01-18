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
using System.Collections.Generic;
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
			oTask = new Task(sTaskID, true, ref sErr);
			if (oTask == null)
			{
				ui.RaiseError(Page, "Unable to continue.  Unable to build Task object" + sErr, true, "");
				return;
			}
			
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
					
					//TODO: this populates the "new" version options on the add version dialog.
					//the web method could do it when the dialog is popped instead of here.
					//or this can stay, just call the WM and make it return both values so we can get rid of this
					//and the identical func in taskView.
                    if (!GetMaxVersion(sTaskID, ref sErr)) return false;

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

                //see if a debug asset was saved for this user
//				Dictionary<string, string> d = ui.GetUsersTaskDebug(sTaskID);
//				if (d != null)
//				{
//					txtTestAsset.Text = d["asset_name"];
//					txtTestAsset.Attributes["asset_id"] = d["asset_id"];
//				}

				return true;
            }
            catch (Exception ex)
            {
                throw ex;
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
