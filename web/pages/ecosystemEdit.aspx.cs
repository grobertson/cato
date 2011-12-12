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
        dataAccess dc = new dataAccess();
        acUI.acUI ui = new acUI.acUI();

        string sEcosystemID;
        string sEcoTemplateID;

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
                string sSQL = "select e.ecosystem_id, e.ecosystem_name, e.ecosystem_desc," +
                    " e.account_id, e.ecotemplate_id, et.ecotemplate_name" +
                    " from ecosystem e" +
                    " join ecotemplate et on e.ecotemplate_id = et.ecotemplate_id" +
                    " where e.ecosystem_id = '" + sEcosystemID + "'" +
                    " and e.account_id = '" + ui.GetSelectedCloudAccountID() + "'";

                DataRow dr = null;
                if (!dc.sqlGetDataRow(ref dr, sSQL, ref sErr)) return false;

                if (dr != null)
                {
                    sEcoTemplateID = dr["ecotemplate_id"].ToString();
                    hidEcoTemplateID.Value = sEcoTemplateID;
                    lblEcotemplateName.Text = dr["ecotemplate_name"].ToString();

                    txtEcosystemName.Text = dr["ecosystem_name"].ToString();
                    ViewState["txtEcosystemName"] = dr["ecosystem_name"].ToString();
                    txtDescription.Text = dr["ecosystem_desc"].ToString();
                    ViewState["txtDescription"] = dr["ecosystem_desc"].ToString();

                    //the header
                    lblEcosystemNameHeader.Text = dr["ecosystem_name"].ToString();

                    //schedule, only if we are the default.
                    //if (!GetSchedule(ref sErr)) return false;

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
