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
using System.Linq;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.UI.HtmlControls;
using System.Data;
using System.Xml.Linq;
using System.Xml;
using System.Xml.XPath;
using Globals;

namespace Web.pages
{
    public partial class taskView : System.Web.UI.Page
    {
        dataAccess dc = new dataAccess();

        acUI.acUI ui = new acUI.acUI();
        FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
        ACWebMethods.taskMethods tm = new ACWebMethods.taskMethods();

		//Get a global Task object for this task
		Task oTask;
        string sTaskID;

        //use a checkbox on the page to set this
        bool bShowNotes = true;

        protected void Page_Load(object sender, EventArgs e)
        {
            string sErr = "";

            sTaskID = ui.GetQuerystringValue("task_id", typeof(string)).ToString();

			//instantiate the new Task object
			oTask = new Task(sTaskID, ref sErr);

            if (!Page.IsPostBack)
            {
                hidTaskID.Value = sTaskID;

                //details
                if (!GetDetails(ref sErr))
                {
                    ui.RaiseError(Page, "Unable to continue.  Task record not found for task_id [" + sTaskID + "].<br />" + sErr, true, "");
                    return;
                }

                //steps
                if (!GetSteps(ref sErr))
                {
                    ui.RaiseError(Page, "Unable to continue.<br />" + sErr, true, "");
                    return;
                }

            }

        }
        private bool GetDetails(ref string sErr)
        {
		    if (oTask != null)
			{
				hidOriginalTaskID.Value = oTask.OriginalTaskID;

				hidDefault.Value = (oTask.IsDefaultVersion ? "1" : "0");
		
		        if (oTask.IsDefaultVersion)
		            btnSetDefault.Visible = false;
		
		        lblTaskCode.Text = ui.SafeHTML(oTask.Code);
		        lblVersion.Text = oTask.Version;
		        lblCurrentVersion.Text = oTask.Version;
		
		        lblDescription.Text = ui.SafeHTML(oTask.Description);
		
		        //lblDirect.Text = ((int)dr["use_connector_system"] == 1 ? "Yes" : "No");
		        lblConcurrentInstances.Text = oTask.ConcurrentInstances;
		        lblQueueDepth.Text = oTask.QueueDepth;
		
		        lblStatus.Text = oTask.Status;
		        lblStatus2.Text = oTask.Status;
		
		        //the header
		        lblTaskNameHeader.Text = ui.SafeHTML(oTask.Name);
		        lblVersionHeader.Text = oTask.Version + (oTask.IsDefaultVersion ? " (default)" : "");
		
		        if (!GetMaxVersion(sTaskID, ref sErr)) return false;
		
		        //schedules (only if this is default)
		        if (oTask.IsDefaultVersion)
		        {
		            if (!GetSchedule(oTask.OriginalTaskID, ref sErr)) return false;
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
        private bool GetSchedule(string sTaskID, ref string sErr)
        {
            return true;
            //try
            //{
            //    string sSQL = "select s.schedule_id, s.schedule_name, s.status from schedule s, schedule_object so " +
            //                  " where so.object_id = '" + sTaskID + "'" +
            //                  " and so.schedule_id = s.schedule_id";


            //    DataTable dt = new DataTable();
            //    if (!dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
            //    {
            //        return false;
            //    }

            //    if (dt.Rows.Count > 0)
            //    {
            //        rpSchedules.DataSource = dt;
            //        rpSchedules.DataBind();
            //    }
            //    return true;
            //}
            //catch (Exception ex)
            //{
            //    sErr = ex.Message;
            //    return false;
            //}
        }
        #region "Steps"

        private bool GetSteps(ref string sErr)
        {
            try
            {
                Literal lt = new Literal();

                //MAIN codeblock first
                lt.Text += "<div class=\"ui-state-default te_header\">";

                lt.Text += "<div class=\"step_section_title\">";
                lt.Text += "<span class=\"step_title\">";
                lt.Text += "MAIN";
                lt.Text += "</span>";
                lt.Text += "</div>";
                lt.Text += "<div class=\"step_section_icons\">";
                lt.Text += "<span id=\"print_link\" class=\"pointer\">";
                lt.Text += "<img class=\"task_print_link\" alt=\"\" src=\"../images/icons/printer.png\" />";
                lt.Text += "</span>";
                lt.Text += "</div>";
                lt.Text += "</div>";

                lt.Text += "<div class=\"codeblock_box\">";
                lt.Text += BuildSteps("MAIN");
                lt.Text += "</div>";

				
				//for the rest of the codeblocks
				foreach (Codeblock cb in oTask.Codeblocks.Values)
                {
					if (cb.Name == "MAIN")
						continue;
					
                    lt.Text += "<div class=\"ui-state-default te_header\">";

                    lt.Text += "<div class=\"step_section_title\" id=\"cbt_" + cb.Name + "\">";
                    lt.Text += "<span class=\"step_title\">";
                    lt.Text += cb.Name;
                    lt.Text += "</span>";
                    lt.Text += "</div>";
                    lt.Text += "</div>";

                    lt.Text += "<div class=\"codeblock_box\">";
                    lt.Text += BuildSteps(cb.Name);
                    lt.Text += "</div>";
                }

                phSteps.Controls.Add(lt);
            }
            catch (Exception ex)
            {
                sErr = ex.Message;
                return false;
            }

            return true;
        }
        private string BuildSteps(string sCodeblockName)
        {
			string sHTML = "";
            if (oTask.Codeblocks[sCodeblockName].Steps.Count > 0)
            {
                foreach (Step oStep in oTask.Codeblocks[sCodeblockName].Steps.Values)
                {
					sHTML += ft.DrawReadOnlyStep(oStep, bShowNotes);
                }
            }
            else
            {
                sHTML = "<li class=\"no_step\">No Commands defined for this Codeblock.</li>";
            }

            return sHTML;
        }
        #endregion

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
                                    throw new Exception("Unable to get asset name for asset [" + sDebugAssetID + "].<br />" + sErr);
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


        private void SetDefaultVersion()
        {
            try
            {
                string sErr = "";
                string sSQL = "";

                sSQL = "update task set default_version = 0" +
                    " where original_task_id = " +
                    " (select original_task_id from task where task_id = '" + sTaskID + "');" +
                    "update task set default_version = 1 where task_id = '" + sTaskID + "';";

                if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                {
                    ui.RaiseError(Page, "Unable to set Default Version. " + sErr, true, "");
                    return;
                }

                //now that it's set, hide the button
                btnSetDefault.Visible = false;

                btnSetDefault.Visible = false;
            }
            catch (Exception ex)
            {
                ui.RaiseError(Page, "Unable to set Default Version. " + ex.Message, true, "");

            }
        }
        private bool GetMaxVersion(string sTaskID, ref string sErr)
        {

            try
            {

                string sMaxVer = tm.wmGetTaskMaxVersion(sTaskID, ref sErr);

                if (!string.IsNullOrEmpty(sMaxVer))
                {
                    //lblNewMinor.Text = "New Minor Version (" + String.Format("{0:0.000}", (Convert.ToDouble(sMaxVer) + .001)) + ")";
                    //lblNewMajor.Text = "New Major Version (" + String.Format("{0:0.000}", Math.Round((Convert.ToDouble(sMaxVer) + .5), MidpointRounding.AwayFromZero)) + ")";

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
        protected void btnSetDefault_Click(object sender, System.EventArgs e)
        {
            SetDefaultVersion();
        }
    }
}
