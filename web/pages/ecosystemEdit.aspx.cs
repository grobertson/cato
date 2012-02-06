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
using System.Web.Services;
using System.Data;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Collections.Specialized;
using System.Xml.Linq;
using System.Xml;
using System.Xml.XPath;
using Globals;

namespace Web.pages
{
    public partial class ecosystemEdit : System.Web.UI.Page
    {
        acUI.acUI ui = new acUI.acUI();

        string sEcosystemID;

		protected void Page_Load(object sender, EventArgs e)
        {
            string sErr = "";

            sEcosystemID = (string)ui.GetQuerystringValue("ecosystem_id", typeof(string));

            if (!Page.IsPostBack)
            {
                hidEcosystemID.Value = sEcosystemID;

                if (!GetDetails(ref sErr))
                {
                    ui.RaiseError(Page, "Record not found for ecosystem_id [" + sEcosystemID + "]. " + sErr, true, "");
                    return;
                }
            }
        }

        private bool GetDetails(ref string sErr)
        {
            try
            {
				Ecosystem e = new Ecosystem(sEcosystemID);
			
				if (e != null)
                {
                    hidEcoTemplateID.Value = e.EcotemplateID;
                    lblEcotemplateName.Text = e.EcotemplateName;

                    txtEcosystemName.Text = e.Name;
                    txtDescription.Text = e.Description;

                    //the header
                    lblEcosystemNameHeader.Text = e.Name;

					//storm file
					txtStormFile.Text = e.StormFile;

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

    }

}
