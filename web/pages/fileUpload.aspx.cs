using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.Configuration;
using System.IO;
using Globals;
using System.Collections;
using System.Data;

namespace Web.pages
{
    public partial class fileUpload : System.Web.UI.Page
    {
        acUI.acUI ui = new acUI.acUI();

        protected void Page_Load(object sender, EventArgs e)
        {
        }

        protected void btnImport_Click(object sender, EventArgs e)
        {
			string sUserID = ui.GetSessionUserID();
            string sPath = Server.MapPath("~/temp/");
			
			//first, clean up any previous uploads from this user.
			string[] sFiles = Directory.GetFiles(sPath, sUserID + "-*.tmp");
			foreach (string sFileToDel in sFiles)
				File.Delete(sFileToDel);

            //get the file from the browser
            if ((fupFile.PostedFile != null) && (fupFile.PostedFile.ContentLength > 0))
            {
				string sRefID = ui.GetQuerystringValue("ref_id", typeof(string)).ToString();			
				string sFileName = sUserID + "-" + sRefID + ".tmp"; //System.IO.Path.GetFileName(fupFile.PostedFile.FileName);
                string sFullPath = sPath + sFileName;
                try
                {
                    fupFile.PostedFile.SaveAs(sFullPath);
					
					//if we're here, it was uploaded.  Pass the name back to the parent via an iframe parent callback.
					//Response.Write(string.Format("<script type='text/javascript'>fileWasSaved('{0}');</script>", sFullPath));
					string sScript = string.Format("fileWasSaved('{0}');", sFullPath);
					ScriptManager.RegisterStartupScript(Page, typeof(string), ui.NewGUID(), sScript, true);
                }
                catch (Exception ex)
                {
                    ui.RaiseError(Page, ex.Message, true, "");
                }
            }
            else
            {
                ui.RaiseError(Page, "Please select a file to upload.", true, "");
            }
        }
    }
}
