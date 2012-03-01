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
using System.Linq;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.Services;
using System.Data;
using Globals;

namespace Web.pages
{
    public partial class cloudEdit : System.Web.UI.Page
    {
        acUI.acUI ui = new acUI.acUI();

        protected void Page_Load(object sender, EventArgs e)
        {
            if (!Page.IsPostBack)
            {
				ltClouds.Text = GetClouds("");
 				
				//one time get of the Provider list.
				ltProviders.Text = GetProviders();
           }
        }
		
		public string GetProviders() {
			string sOptionHTML = "";
			
			CloudProviders cp = ui.GetCloudProviders();
			if (cp != null)
			{
				foreach (Provider p in cp.Values) {
					if (p.UserDefinedClouds)
						sOptionHTML += "<option value=\"" + p.Name + "\">" + p.Name + "</option>";
				}
			}
		
			return sOptionHTML;
		}
		public string GetClouds(string sSearch) {
            string sErr = "";
			string sHTML = "";

			Clouds c = new Clouds(sSearch, ref sErr);
				
			if (c!= null && string.IsNullOrEmpty(sErr))
			{
	            //build the table
	            sHTML += "<table class=\"jtable\" cellspacing=\"1\" cellpadding=\"1\" width=\"99%\">";
	            sHTML += "<tr>";
	            sHTML += "<th class=\"chkboxcolumn\">";
	            sHTML += "<input type=\"checkbox\" class=\"chkbox\" id=\"chkAll\" />";
	            sHTML += "</th>";
	
	            sHTML += "<th sortcolumn=\"cloud_name\">Cloud Name</th>";
	            sHTML += "<th sortcolumn=\"provider\">Type</th>";
	            sHTML += "<th sortcolumn=\"api_protocol\">Protocol</th>";
	            sHTML += "<th sortcolumn=\"api_url\">URL</th>";
	
	            sHTML += "</tr>";
	
	            //loop rows
	            foreach (DataRow dr in c.DataTable.Rows)
	            {
	                sHTML += "<tr account_id=\"" + dr["cloud_id"].ToString() + "\">";
	                sHTML += "<td class=\"chkboxcolumn\">";
	                sHTML += "<input type=\"checkbox\" class=\"chkbox\"" +
	                    " id=\"chk_" + dr[0].ToString() + "\"" +
	                    " object_id=\"" + dr[0].ToString() + "\"" +
	                    " tag=\"chk\" />";
	                sHTML += "</td>";
	
	                sHTML += "<td tag=\"selectable\">" + dr["cloud_name"].ToString() +  "</td>";
	                sHTML += "<td tag=\"selectable\">" + dr["provider"].ToString() +  "</td>";
	                sHTML += "<td tag=\"selectable\">" + dr["api_protocol"].ToString() +  "</td>";
	                sHTML += "<td tag=\"selectable\">" + dr["api_url"].ToString() +  "</td>";
	
	                sHTML += "</tr>";
	            }
	
	            sHTML += "</table>";
			}
			else
			{
				ui.RaiseError(Page, "Unable to get Clouds.", false, sErr);
			}
			
			return sHTML;
		}

        [WebMethod(EnableSession = true)]
        public static string wmGetClouds(string sSearch)
        {
			cloudEdit ce = new cloudEdit();
            return ce.GetClouds(sSearch);
        }
    }
}
