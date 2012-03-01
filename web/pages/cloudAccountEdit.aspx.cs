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
using System.Text;
using Globals;

namespace Web.pages
{
    public partial class cloudAccountEdit : System.Web.UI.Page
    {
        acUI.acUI ui = new acUI.acUI();

        protected void Page_Load(object sender, EventArgs e)
        {
            if (!Page.IsPostBack)
            {
				ltAccounts.Text = GetAccounts("");
				
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
					sOptionHTML += "<option value=\"" + p.Name + "\">" + p.Name + "</option>";
				}
			}
		
			return sOptionHTML;
		}
		public string GetAccounts(string sSearch) {
            string sErr = "";

			CloudAccounts ca = new CloudAccounts(sSearch, ref sErr);
				
			string sHTML = "";

			if (ca != null && string.IsNullOrEmpty(sErr))
			{
	            //buld the table
	            sHTML += "<table class=\"jtable\" cellspacing=\"1\" cellpadding=\"1\" width=\"99%\">";
	            sHTML += "<tr>";
	            sHTML += "<th class=\"chkboxcolumn\">";
	            sHTML += "<input type=\"checkbox\" class=\"chkbox\" id=\"chkAll\" />";
	            sHTML += "</th>";
	
	            sHTML += "<th sortcolumn=\"account_name\">Account Name</th>";
	            sHTML += "<th sortcolumn=\"account_number\">Account Number</th>";
	            sHTML += "<th sortcolumn=\"provider\">Type</th>";
	            sHTML += "<th sortcolumn=\"login_id\">Login ID</th>";
	            sHTML += "<th sortcolumn=\"is_default\">Default?</th>";
	
	            sHTML += "</tr>";
	
	            //loop rows
	            foreach (DataRow dr in ca.DataTable.Rows)
	            {
	                sHTML += "<tr account_id=\"" + dr["account_id"].ToString() + "\">";
	                
					if (dr["has_ecosystems"].ToString() == "0")
					{
						sHTML += "<td class=\"chkboxcolumn\">";
		                sHTML += "<input type=\"checkbox\" class=\"chkbox\"" +
		                    " id=\"chk_" + dr["account_id"].ToString() + "\"" +
		                    " object_id=\"" + dr["account_id"].ToString() + "\"" +
		                    " tag=\"chk\" />";
		                sHTML += "</td>";
					}
					else 
					{
						sHTML += "<td>";
						sHTML += "<img class=\"account_help_btn trans50\"" +
		                    " src=\"../images/icons/info.png\" alt=\"\" style=\"padding: 2px 0 0 2px; width: 12px; height: 12px;\"" +
		                    " title=\"This account has associated Ecosystems and cannot be deleted.\" />";
						sHTML += "</td>";
					}
					
					
	                sHTML += "<td tag=\"selectable\">" + dr["account_name"].ToString() +  "</td>";
	                sHTML += "<td tag=\"selectable\">" + dr["account_number"].ToString() +  "</td>";
	                sHTML += "<td tag=\"selectable\">" + dr["provider"].ToString() +  "</td>";
	                sHTML += "<td tag=\"selectable\">" + dr["login_id"].ToString() +  "</td>";
	                sHTML += "<td tag=\"selectable\">" + dr["is_default"].ToString() +  "</td>";
	
	                sHTML += "</tr>";
	            }
	
	            sHTML += "</table>";
			}
			else
			{
				ui.RaiseError(Page, "Unable to get Cloud Accounts.", false, sErr);
			}
			
			return sHTML;
		}

        #region "Web Methods"
        [WebMethod(EnableSession = true)]
        public static string wmGetAccounts(string sSearch)
        {
			cloudAccountEdit ca = new cloudAccountEdit();
            return ca.GetAccounts(sSearch);
        }
	
        [WebMethod(EnableSession = true)]
        public static string GetKeyPairs(string sID)
        {

            dataAccess dc = new dataAccess();
            string sSql = null;
            string sErr = null;
            string sHTML = "";

            sSql = "select keypair_id, keypair_name, private_key, passphrase" +
                " from cloud_account_keypair" +
                " where account_id = '" + sID + "'";

            DataTable dt = new DataTable();
            if (!dc.sqlGetDataTable(ref dt, sSql, ref sErr))
            {
                throw new Exception(sErr);
            }

            if (dt.Rows.Count > 0)
            {
                sHTML += "<ul>";
                foreach (DataRow dr in dt.Rows)
                {
                    string sName = dr["keypair_name"].ToString();

                    //DO NOT send these back to the client.
                    string sPK = (object.ReferenceEquals(dr["private_key"], DBNull.Value) ? "false" : "true");
                    string sPP = (object.ReferenceEquals(dr["passphrase"], DBNull.Value) ? "false" : "true");
                    //sLoginPassword = "($%#d@x!&";

                    sHTML += "<li class=\"ui-widget-content ui-corner-all keypair\" id=\"kp_" + dr["keypair_id"].ToString() + "\" has_pk=\"" + sPK + "\" has_pp=\"" + sPP + "\">";
                    sHTML += "<span class=\"keypair_label pointer\">" + sName + "</span>";
                    sHTML += "<span class=\"keypair_icons pointer\"><img src=\"../images/icons/fileclose.png\" class=\"keypair_delete_btn\" /></span>";
                    sHTML += "</li>";
                }
                sHTML += "</ul>";
            }
            else
            {
                sHTML += "";
            }


            return sHTML;
        }

        [WebMethod(EnableSession = true)]
        public static string SaveKeyPair(string sKeypairID, string sAccountID, string sName, string sPK, string sPP)
        {
            acUI.acUI ui = new acUI.acUI();

			if (string.IsNullOrEmpty(sName))
                return "KeyPair Name is Required.";

            //we encoded this in javascript before the ajax call.
            //the safest way to unencode it is to use the same javascript lib.
            //(sometimes the javascript and .net libs don't translate exactly, google it.)
            sPK = ui.unpackJSON(sPK);

            bool bUpdatePK = false;
			if (sPK.Length > 0)
				bUpdatePK = true;

            bool bUpdatePP = false;
            if (sPP != "!2E4S6789O")
                bUpdatePP = true;


            //all good, keep going


            dataAccess dc = new dataAccess();
            string sSQL = null;
            string sErr = null;

            try
            {
                if (string.IsNullOrEmpty(sKeypairID))
                {
                    //empty id, it's a new one.
                    string sPKClause = "";
                    if (bUpdatePK)
                        sPKClause = "'" + dc.EnCrypt(sPK) + "'";

                    string sPPClause = "null";
                    if (bUpdatePP)
                        sPPClause = "'" + dc.EnCrypt(sPP) + "'";

                    sSQL = "insert into cloud_account_keypair (keypair_id, account_id, keypair_name, private_key, passphrase)" +
                        " values ('" + ui.NewGUID() + "'," +
                        "'" + sAccountID + "'," +
                        "'" + sName.Replace("'", "''") + "'," +
                        sPKClause + "," +
                        sPPClause +
                        ")";
                }
                else
                {
                    string sPKClause = "";
                    if (bUpdatePK)
                        sPKClause = ", private_key = '" + dc.EnCrypt(sPK) + "'";

                    string sPPClause = "";
                    if (bUpdatePP)
                        sPPClause = ", passphrase = '" + dc.EnCrypt(sPP) + "'";

                    sSQL = "update cloud_account_keypair set" +
                        " keypair_name = '" + sName.Replace("'", "''") + "'" +
                        sPKClause + sPPClause +
                        " where keypair_id = '" + sKeypairID + "'";
                }

                if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                    throw new Exception(sErr);

            }
            catch (Exception ex)
            {

                throw new Exception(ex.Message);
            }




            //// add security log
            //// since this is not handled as a page postback, theres no "Viewstate" settings
            //// so 2 options either we keep an original setting for each value in hid values, or just get them from the db as part of the 
            //// update above, since we are already passing in 15 or so fields, lets just get the values at the start and reference them here
            //if (sMode == "edit")
            //{
            //    ui.WriteObjectChangeLog(Globals.acObjectTypes.CloudAccount, sAccountID, sAccountName, sOriginalName, sAccountName);
            //}
            //else
            //{
            //    ui.WriteObjectAddLog(Globals.acObjectTypes.CloudAccount, sAccountID, sAccountName, "Account Created");
            //}


            // no errors to here, so return an empty string
            return "";
        }

        [WebMethod(EnableSession = true)]
        public static string DeleteKeyPair(string sKeypairID)
        {
            dataAccess dc = new dataAccess();
            string sSQL = null;
            string sErr = "";

            try
            {
                sSQL = "delete from cloud_account_keypair where keypair_id = '" + sKeypairID + "'";
                if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                    throw new Exception(sErr);

                if (sErr != "")
                    throw new Exception(sErr);
            }
            catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }

            return "";
        }
        #endregion
    }
}
