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
using System.IO;
using System.Text;
using System.Web.UI;
using System.Web.UI.WebControls;
using Globals;


namespace Web.pages
{
    public partial class taskPrint : System.Web.UI.Page
    {
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
			oTask = new Task(sTaskID, false, ref sErr);
            
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


            //parameters (for edit)
            if (!GetParameters(sTaskID, ref sErr))
            {
                ui.RaiseError(Page, "Parameters record not found for task_id [" + sTaskID + "]. " + sErr, true, "");
                return;
            }

        }
        private bool GetDetails(ref string sErr)
        {
            try
            {
			    if (oTask != null)
				{
                    lblTaskCode.Text = oTask.Code;
                    lblDescription.Text = ui.SafeHTML(oTask.Description);
                    lblStatus.Text = oTask.Status;

                    //the header
                    lblTaskNameHeader.Text = ui.SafeHTML(oTask.Name);
                    lblVersionHeader.Text = oTask.Version + (oTask.IsDefaultVersion ? " (default)" : "");

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

        #region "Steps"
        private bool GetSteps(ref string sErr)
        {
            try
            {
                Literal lt = new Literal();

                //MAIN codeblock first
                lt.Text += "<div class=\"ui-state-default te_header\">MAIN</div>";
                lt.Text += "<div class=\"codeblock_box\">";
                lt.Text += BuildSteps("MAIN");
                lt.Text += "</div>";

				//for the rest of the codeblocks
				foreach (Codeblock cb in oTask.Codeblocks.Values)
                {
					if (cb.Name == "MAIN")
						continue;
					
                    lt.Text += "<div class=\"ui-state-default te_header\" id=\"cbt_" + cb.Name + "\">" + cb.Name + "</div>";
                    lt.Text += "<div class=\"codeblock_box\">";
                    lt.Text += BuildSteps(cb.Name);
                    lt.Text += "</div>";
                }

                phSteps.Controls.Add(lt);

                return true;
            }
            catch (Exception ex)
            {
                sErr = ex.Message;
                return false;
            }
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

        private bool GetParameters(string sTaskID, ref string sErr)
        {
            try
            {
                Literal lt = new Literal();
                lt.Text += "<div class=\"view_parameters\">";
                lt.Text += tm.wmGetParameters("task", sTaskID, false, false);
                lt.Text += "</div>";
                phParameters.Controls.Add(lt);

                return true;
            }
            catch (Exception ex)
            {
               sErr = ex.Message;
               return false;
            }
        }

        protected override void Render(HtmlTextWriter Output)
        {
            string sHTML = "";

            StringBuilder sb = new StringBuilder();
            StringWriter sw = new StringWriter(sb);
            HtmlTextWriter hw = new HtmlTextWriter(sw);

            base.Render(hw);
            sHTML = sb.ToString();

            if (hidExport.Value == "export")
            {
                //5/10/2011 NSC 
                //Winnovative PDF generator was not working with VS2010.
                //if this is needed we will need to find a new PDF generator.

                //PdfConverter pdfConverter = new PdfConverter();
                //pdfConverter.PdfDocumentOptions.PdfPageSize = PdfPageSize.A4;
                //pdfConverter.PdfDocumentOptions.PdfPageOrientation = PDFPageOrientation.Portrait;
                //pdfConverter.PdfDocumentOptions.PdfCompressionLevel = PdfCompressionLevel.Normal;
                //pdfConverter.LicenseKey = "DnGDxKtBfgZuI0rkd765/VniiDaWDOTQkzk1k/tpGW9SYwYC0qMAvqNTuqGjw+dn";

                //string sFile = Server.MapPath("~/reports/" + sUserID + ".html");
                //string sPDF = Server.MapPath("~/reports/" + sUserID + ".pdf");

                //File.WriteAllText(sFile, sHTML);

                //pdfConverter.SavePdfFromUrlToFile(sFile, sPDF);

                //System.IO.FileInfo fPDF = new System.IO.FileInfo(sPDF);
                         
                //  if (fPDF.Exists) {
                //      Response.Clear();
                //      Response.AddHeader("Content-Disposition", "attachment; filename=" + fPDF.Name);
                //      Response.AddHeader("Content-Length", fPDF.Length.ToString());
                //      Response.ContentType = "application/octet-stream";
                //      Response.WriteFile(fPDF.FullName);
                //      Response.Flush();
                //      Response.End();
                //  }

            }
            else
            {

                Output.Write(sHTML);
            }

        }

        protected void btnExport_Click(object sender, EventArgs e)
        {
            hidExport.Value = "export"; 

        }

    }
    
}
