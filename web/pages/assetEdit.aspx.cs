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
using System.Xml.Linq;
using System.Xml.XPath;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.Services;
using System.Data;
using System.Data.Odbc;
using System.Text;

namespace Web.pages
{
    public partial class assetEdit : System.Web.UI.Page
    {
        dataAccess dc = new dataAccess();
        acUI.acUI ui = new acUI.acUI();

        int iPageSize;

        string sSQL = "";
        string sErr = "";

        protected void Page_Load(object sender, EventArgs e)
        {
            //could be repository settings for default values, and will be options on the page as well
            iPageSize = 50;

            if (!Page.IsPostBack)
            {

                // first time on the page, get the sortcolumn last used if one exists.
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

                    XElement xSortSettings = xDoc.Descendants("sort").Where(x => (string)x.Attribute("screen") == "asset").LastOrDefault();
                    if (xSortSettings != null)
                    {
                        if (xSortSettings.Attribute("sort_column") != null)
                        {
                            hidSortColumn.Value = xSortSettings.Attribute("sort_column").Value.ToString();
                        }
                        if (xSortSettings.Attribute("sort_direction") != null)
                        {
                            hidSortDirection.Value = xSortSettings.Attribute("sort_direction").Value.ToString();
                        }

                    }

                }

                BindList();
            }
        }

        #region "List Functions"

        private void BindList()
        {

            string sWhereString = " where 1=1";

            if (txtSearch.Text.Length > 0)
            {
                //split on spaces
                int i = 0;
                string[] aSearchTerms = txtSearch.Text.Split(' ');
                for (i = 0; i <= aSearchTerms.Length - 1; i++)
                {

                    //if the value is a guid, it's an existing task.
                    //otherwise it's a new task.
                    if (aSearchTerms[i].Length > 0)
                    {
                        sWhereString += " and (a.asset_name like '%" + aSearchTerms[i] + "%' " +
                            "or a.port like '%" + aSearchTerms[i] + "%' " +
                            "or a.address like '%" + aSearchTerms[i] + "%' " +
                            "or a.connection_type like '%" + aSearchTerms[i] + "%' " +
                            "or a.db_name like '%" + aSearchTerms[i] + "%' " +
                            "or a.asset_status like '%" + aSearchTerms[i] + "%' " +
                            "or ac.username like '%" + aSearchTerms[i] + "%') ";
                    }
                }
            }

            sSQL = "select a.asset_id, a.asset_name, a.asset_status, a.address, a.connection_type, " +
                    " case when ac.shared_or_local = 1 then 'Local - ' else 'Shared - ' end as shared_or_local," +
                    " case when ac.domain <> '' then concat(ac.domain, cast(char(92) as char), ac.username) else ac.username end as credentials" +
                    " from asset a " +
                    " left outer join asset_credential ac " +
                    " on ac.credential_id = a.credential_id " +
                    sWhereString +
                    " order by a.asset_name";



            DataTable dt = new DataTable();
            if (!dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
            {
                ui.RaiseError(Page, sErr, true, "");
            }

            ui.SetSessionObject("AssetList", dt, "SelectorListTables");

            //now, actually get the data from the session table and display it
            GetAssets();
        }
        private void GetAssets()
        {
            //here's how the paging works
            //you can get at the data by explicit ranges, or by pages
            //where pages are defined by properties

            //could come from a field on the page
            int iStart = 0;
            int iEnd = 0;

            //this is the page number you want
            int iPageNum = (string.IsNullOrEmpty(hidPage.Value) ? 1 : Convert.ToInt32(hidPage.Value));
            DataTable dtTotal = (DataTable)ui.GetSessionObject("AssetList", "SelectorListTables");
            dtTotal.TableName = "AssetList";
            DataTable dt = ui.GetPageFromSessionTable(dtTotal, iPageSize, iPageNum, iStart, iEnd, hidSortColumn.Value, hidSortDirection.Value);

            rpAssets.DataSource = dt;
            rpAssets.DataBind();

            // save the users settings for sorting on this page.
            // the same general logic exists in 3 places,
            // based on if the last column sorted was the same, then reverse the order etc.
            ui.SaveUsersSort("asset", hidSortColumn.Value, hidSortDirection.Value, ref sErr);
            if (sErr != "")
            {
                ui.RaiseError(Page, sErr, true, "");
            }

            if ((dt != null))
            {
                if ((dtTotal.Rows.Count > iPageSize))
                {
                    Literal lt = new Literal();
                    lt.Text = ui.DrawPager(dtTotal.Rows.Count, iPageSize, iPageNum);
                    phPager.Controls.Add(lt);
                }
            }
        }

        [WebMethod()]
        public static string GetConnectionTypes()
        {
			FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
            string sErr = "";

            DataTable dt = new DataTable();
            dt = ft.getConnectionTypes(ref sErr);
            if (!string.IsNullOrEmpty(sErr))
            {
                throw new Exception("Connection Type lookup error: " + sErr);
            }
            else
            {
				string sHTML = "<select name=\"ddlConnectionType\" style=\"width: 200px;\" id=\"ddlConnectionType\">";
				if (dt.Rows.Count > 0)
                {
                    foreach (DataRow dr in dt.Rows)
                    {
                        sHTML += "<option value=\"" + dr["connection_type"].ToString() + "\">" + dr["connection_type"].ToString() + "</option>";
                    }
                }
				sHTML += "</select>";
				return sHTML;
			}
        }

        [WebMethod()]
        public static string GetCredentials()
        {

			dataAccess dc = new dataAccess();

            string sSql = null;
            string sErr = null;
            StringBuilder sbString = new StringBuilder();


            DataTable dt = new DataTable();
            sSql = "select username from asset_credential order by username";
            if (!dc.sqlGetDataTable(ref dt, sSql, ref sErr))
            {
                throw new Exception(sErr);
            }
            else
            {
                if (dt.Rows.Count > 0)
                {
                    sbString.Append("<select name=\"ddlCredentials\" id=\"ddlCredentials\">");
                    sbString.Append("<option value=\"\"></option>");
                    foreach (DataRow dr in dt.Rows)
                    {
                        sbString.Append("<option value=\"" + dr["username"] + "\">" + dr["username"] + "</option>");
                    }
                    sbString.Append("</select>");

                    return sbString.ToString();
                }
                else
                {
                    return "<select name=\"ddlCredentials\" id=\"ddlCredentials\"></select>";
                }
            }
        }

        #endregion

        #region "Delete Functions"

        [WebMethod()]
        public static string DeleteAssets(string sDeleteArray)
        {
	        dataAccess dc = new dataAccess();
	        acUI.acUI ui = new acUI.acUI();
            string sSql = null;
            string sErr = "";

            ArrayList arrList = new ArrayList();
            arrList.AddRange(sDeleteArray.Split(','));

            if (sDeleteArray.Length < 36)
                return "";


            StringBuilder sbAssetIDString = new StringBuilder();
            StringBuilder sbAssetsCantDelete = new StringBuilder();
            foreach (string sAssetID in arrList)
            {
                if (sAssetID.Length == 36)
                {
                    // what about the instance tables?????
                    // bugzilla 1290 Assets that have history (task_instance table) can not be deleted
                    // exclude them from the list and return a message noting the asset(s) that could not be deleted
                    // check if this asset has any history rows.
                    sSql = "select count(*) from tv_task_instance where asset_id = '" + sAssetID + "'";
                    int iHistory = 0;
                    if (!dc.sqlGetSingleInteger(ref iHistory, sSql, ref sErr))
                        throw new Exception(sErr);
                    // if there is no history add this to the delete list,
                    // otherwise add the task id to the non delete list
                    if (iHistory == 0)
                    {
                        sbAssetIDString.Append("'" + sAssetID + "',");
                    }
                    else
                    {
                        sbAssetsCantDelete.Append("'" + sAssetID + "',");
                    };

                }
            }
            // trim the trailing ,
            if (sbAssetsCantDelete.ToString().Length > 2) { sbAssetsCantDelete.Remove(sbAssetsCantDelete.Length - 1, 1); };

            if (sbAssetIDString.ToString().Length > 2)
            {
                // delete from these tables:
                //   asset, asset_credential (if the credential is local). 

                // trim the trailing ,
                sbAssetIDString.Remove(sbAssetIDString.Length - 1, 1);
                try
                {
					dataAccess.acTransaction oTrans = new dataAccess.acTransaction(ref sErr);

                    // TBD
                    // delete asset_credential

                    // delete asset
                    sSql = "delete from asset where asset_id in (" + sbAssetIDString.ToString() + ")";
                    oTrans.Command.CommandText = sSql;
                    if (!oTrans.ExecUpdate(ref sErr))
                    {
                        throw new Exception(sErr);
                    }

                    oTrans.Commit();

                    // add security log
                    ui.WriteObjectDeleteLog(Globals.acObjectTypes.Asset, sbAssetIDString.ToString(), "Batch Asset Delete", "Deleted Assets in batch mode");
                }
                catch (Exception ex)
                {
                    throw new Exception(ex.Message);
                }
            };



            // if some did not get deleted return a message.
            if (sbAssetsCantDelete.Length > 2)
            {
                string sTaskNames = "";
                sSql = "select asset_name from asset where asset_id in (" + sbAssetsCantDelete.ToString() + ")";

                if (!dc.csvGetList(ref sTaskNames, sSql, ref sErr, true))
                    throw new Exception(sErr);

                return "Asset deletion completed. Asset(s) (" + sTaskNames + ") could not be deleted because history rows exist.";

            }
            else
            {
                return sErr;
            }



        }

        #endregion

        #region "Modify Functions"

        private static string GetCredentialNameFromID(string sCredentialID)
        {
            dataAccess dc = new dataAccess();
            string sCredentialName = "";
            string sSQL = "";
            string sErr = "";
            sSQL = "select username from asset_credential where credential_id = '" + sCredentialID + "'";
            if (!dc.sqlGetSingleString(ref sCredentialName, sSQL, ref sErr))
            {
                throw new Exception(sErr);
            }
            else
            {
                if (string.IsNullOrEmpty(sCredentialName))
                {
                    sCredentialName = "";
                }
            }

            return sCredentialName;
        }


        [WebMethod()]
        public static string SaveAsset(object[] oAsset)
        {
            // check the # of elements in the array
            if (oAsset.Length != 19) return "Incorrect number of Asset Properties:" + oAsset.Length.ToString();

            string sAssetID = oAsset[0].ToString();
            string sAssetName = oAsset[1].ToString().Replace("'", "''");
            string sDbName = oAsset[2].ToString().Replace("'", "''");
            string sPort = oAsset[3].ToString();
            string sConnectionType = oAsset[4].ToString();
            string sIsConnection = "0"; // oAsset[5].ToString();

            string sAddress = oAsset[5].ToString().Replace("'", "''");
            // mode is edit or add
            string sMode = oAsset[6].ToString();
            string sCredentialID = oAsset[7].ToString();
            string sCredUsername = oAsset[8].ToString().Replace("'", "''");
            string sCredPassword = oAsset[9].ToString().Replace("'", "''");
            string sShared = oAsset[10].ToString();
            string sCredentialName = oAsset[11].ToString().Replace("'", "''");
            string sCredentialDescr = oAsset[12].ToString().Replace("'", "''");
            string sDomain = oAsset[13].ToString().Replace("'", "''");
            string sCredentialType = oAsset[14].ToString();

            string sAssetStatus = oAsset[15].ToString();
            string sPrivilegedPassword = oAsset[16].ToString();
            string sTagArray = oAsset[17].ToString();

            string sConnString = oAsset[18].ToString().Replace("'", "''");

            // for logging
            string sOriginalAssetName = "";
            string sOriginalPort = "";
            string sOriginalDbName = "";
            string sOriginalAddress = "";
            string sOriginalConnectionType = "";
            string sOriginalUserName = "";
            string sOriginalConnString = "";
            string sOriginalCredentialID = "";
            string sOriginalAssetStatus = "";

            dataAccess dc = new dataAccess();
            acUI.acUI ui = new acUI.acUI();
            string sSql = null;
            string sErr = null;


            //if we are editing get the original values
			//this is getting original values for logging purposes
            if (sMode == "edit")
            {
                DataRow dr = null;
                sSql = "select a.asset_name, a.asset_status, a.port, a.db_name, a.address, a.db_name, a.connection_type, a.conn_string, ac.username, a.credential_id," +
					" case when a.is_connection_system = '1' then 'Yes' else 'No' end as is_connection_system " +
					" from asset a " + 
					" left outer join asset_credential ac on ac.credential_id = a.credential_id " +
                    " where a.asset_id = '" + sAssetID + "'";

                if (!dc.sqlGetDataRow(ref dr, sSql, ref sErr))
                    throw new Exception(sErr);
                else
                {
                    if (dr != null)
                    {
                        sOriginalAssetName = dr["asset_name"].ToString();
                        sOriginalPort = (object.ReferenceEquals(dr["port"], DBNull.Value) ? "" : dr["port"].ToString());
                        sOriginalDbName = (object.ReferenceEquals(dr["db_name"], DBNull.Value) ? "" : dr["db_name"].ToString());
                        sOriginalAddress = (object.ReferenceEquals(dr["address"], DBNull.Value) ? "" : dr["address"].ToString());
                        sOriginalConnectionType = (object.ReferenceEquals(dr["connection_type"], DBNull.Value) ? "" : dr["connection_type"].ToString());
                        sOriginalUserName = (object.ReferenceEquals(dr["username"], DBNull.Value) ? "" : dr["username"].ToString());
                        sOriginalConnString = (object.ReferenceEquals(dr["conn_string"], DBNull.Value) ? "" : dr["conn_string"].ToString());
                        sOriginalCredentialID = (object.ReferenceEquals(dr["credential_id"], DBNull.Value) ? "" : dr["credential_id"].ToString());
                        sOriginalAssetStatus = dr["asset_status"].ToString();
                    }
                }
            }
			
			//NOTE NOTE NOTE!
			//the following is a catch 22.
			//if we're adding a new asset, we will need to figure out the credential first so we can save the credential id on the asset
			//but if it's a new local credential, it gets the asset id as it's name.
			//so.........
			//if it's a new asset, go ahead and get the new guid for it here so the credential add will work.
			if (sMode == "add")
				sAssetID = ui.NewGUID();
			//and move on...
			
			
			
            // there are three CredentialType's 
            // 1) 'selected' = user selected a different credential, just save the credential_id
            // 2) 'new' = user created a new shared or local credential
            // 3) 'existing' = same credential, just update the username,description ad password
            string sPriviledgedPasswordUpdate = null;
            if (sCredentialType == "new")
            {
				if (sPrivilegedPassword.Length == 0)
					sPriviledgedPasswordUpdate = "NULL";
				else
					sPriviledgedPasswordUpdate = "'" + dc.EnCrypt(sPrivilegedPassword) + "'";

				//if it's a local credential, the credential_name is the asset_id.
				//if it's shared, there will be a name.
				if (sShared == "1")
				{
					sCredentialName = sAssetID;
					
					//whack and add - easiest way to avoid conflicts
                    sSql = "delete from asset_credential where credential_name = '" + sCredentialName + "' and shared_or_local = '1'";
                    if (!dc.sqlExecuteUpdate(sSql, ref sErr))
                        throw new Exception(sErr);
				}
				
				//now we're clear to add
				sCredentialID = "'" + ui.NewGUID() + "'";
				sSql = "insert into asset_credential " +
					"(credential_id,credential_name,username,password,domain,shared_or_local,shared_cred_desc,privileged_password) " +
						"values (" + sCredentialID + ",'" + sCredentialName + "','" + sCredUsername + "','" + dc.EnCrypt(sCredPassword) + "','" + sDomain + "','" + sShared + "','" + sCredentialDescr + "'," + sPriviledgedPasswordUpdate + ")";
				if (!dc.sqlExecuteUpdate(sSql, ref sErr))
				{
					if (sErr == "key_violation")
						throw new Exception("A Credential with that name already exists.  Please select another name.");
					else 
						throw new Exception(sErr);
				}
				
				// add security log
				ui.WriteObjectAddLog(Globals.acObjectTypes.Credential, sCredentialID, sCredentialName, "");
                

            }
            else if (sCredentialType == "existing")
            {
                sCredentialID = "'" + sCredentialID + "'";
                // bugzilla 1126 if the password has not changed leave it as is.
                string sPasswordUpdate = null;
                if (sCredPassword == "($%#d@x!&")
                    // password has not been touched
                    sPasswordUpdate = "";
                else
                    // updated password
                    sPasswordUpdate = ",password = '" + dc.EnCrypt(sCredPassword) + "'";

                // bugzilla 1260
                // same for privileged_password

                if (sPrivilegedPassword == "($%#d@x!&")
                    // password has not been touched
                    sPriviledgedPasswordUpdate = "";
                else
                {
                    // updated password
                    // bugzilla 1352 priviledged password can be blank, so if it is, set it to null
                    if (sPrivilegedPassword.Length == 0)
                        sPriviledgedPasswordUpdate = ",privileged_password = null";
                    else
                        sPriviledgedPasswordUpdate = ",privileged_password = '" + dc.EnCrypt(sPrivilegedPassword) + "'";
                }

                sSql = "update asset_credential " +
                        "set username = '" + sCredUsername + "'" + sPasswordUpdate + sPriviledgedPasswordUpdate + ",domain = '" + sDomain + "'," +
                        "shared_or_local = '" + sShared + "',shared_cred_desc = '" + sCredentialDescr + "'" +
                        "where credential_id = " + sCredentialID;
                if (!dc.sqlExecuteUpdate(sSql, ref sErr))
                    throw new Exception(sErr);

                // add security log
                ui.WriteObjectChangeLog(Globals.acObjectTypes.Asset, sAssetID, sAssetName.Trim().Replace("'", "''") + "Changed credential", sOriginalUserName, sCredUsername);

            }
            else
            {
                // user selected a shared credential
                // remove the local credential if one exists

                if (sOriginalCredentialID.Length > 0)
                {
                    sSql = "delete from asset_credential where credential_id = '" + sOriginalCredentialID + "' and shared_or_local = '1'";
                    if (!dc.sqlExecuteUpdate(sSql, ref sErr))
                        throw new Exception(sErr);

                    // add security log
                    ui.WriteObjectDeleteLog(Globals.acObjectTypes.Asset, sAssetID, sAssetName.Trim().Replace("'", "''"), "Credential deleted" + sOriginalCredentialID + " " + sOriginalUserName);
                }


                sCredentialID = "'" + sCredentialID + "'";

            }


            // checks that cant be done on the client side
            // is the name unique?
            string sInuse = "";

            if (sMode == "edit")
                sSql = "select asset_id from asset where asset_name = '" + sAssetName.Trim() + "' and asset_id <> '" + sAssetID + "' limit 1";
            else
                sSql = "select asset_id from asset where asset_name = '" + sAssetName.Trim() + "' limit 1";

            if (!dc.sqlGetSingleString(ref sInuse, sSql, ref sErr))
                throw new Exception(sErr);
            else
                if (!string.IsNullOrEmpty(sInuse))
                    return "Asset Name '" + sAssetName + "' already in use, choose another." + sAssetID;

            try
            {
                dataAccess.acTransaction oTrans = new dataAccess.acTransaction(ref sErr);

                if (sMode == "edit")
                {
                    sSql = "update asset set asset_name = '" + sAssetName + "'," +
                        " asset_status = '" + sAssetStatus + "'," +
                        " address = '" + sAddress + "'" + "," +
                        " conn_string = '" + sConnString + "'" + "," +
                        " db_name = '" + sDbName + "'," +
                        " port = " + (sPort == "" ? "NULL" : "'" + sPort + "'") + "," +
                        " connection_type = '" + sConnectionType + "'," +
                        " is_connection_system = '" + (sIsConnection == "Yes" ? 1 : 0) + "'," +
                        " credential_id = " + sCredentialID +
                        " where asset_id = '" + sAssetID + "'";

                    oTrans.Command.CommandText = sSql;
                    if (!oTrans.ExecUpdate(ref sErr))
                        throw new Exception(sErr);

                }
                else
                {
                    sSql = "insert into asset (asset_id,asset_name,asset_status,address,conn_string,db_name,port,connection_type,is_connection_system,credential_id)" +
                    " values (" +
                    "'" + sAssetID + "'," +
                    "'" + sAssetName + "'," +
                    "'" + sAssetStatus + "'," +
                    "'" + sAddress + "'," +
                    "'" + sConnString + "'," +
                    "'" + sDbName + "'," +
                    (sPort == "" ? "NULL" : "'" + sPort + "'") + "," +
                    "'" + sConnectionType + "'," +
                    "'0'," +
                    sCredentialID + ")";

                    oTrans.Command.CommandText = sSql;
                    if (!oTrans.ExecUpdate(ref sErr))
                        throw new Exception(sErr);
                }

				#region "tags"
                // remove the existing tags
                sSql = "delete from object_tags where object_id = '" + sAssetID + "'";
                oTrans.Command.CommandText = sSql;
                if (!oTrans.ExecUpdate(ref sErr))
                {
                    throw new Exception(sErr);
                }

                // add user groups, if there are any
                if (sTagArray.Length > 0)
                {
                    ArrayList aTags = new ArrayList(sTagArray.Split(','));
                    foreach (string sTagName in aTags)
                    {
                        sSql = "insert object_tags (object_id, object_type, tag_name)" +
                            " values ('" + sAssetID + "', 2, '" + sTagName + "')";
                        oTrans.Command.CommandText = sSql;
                        if (!oTrans.ExecUpdate(ref sErr))
                        {
                            throw new Exception(sErr);
                        }
                    }
                }
                #endregion

                oTrans.Commit();

            }
            catch (Exception ex)
            {

                throw new Exception(ex.Message);
            }






            //--------------------------------------------------------------------------------------------------
            // NOTE! too many if edit... probably need to just make 2 functions, update asset, and create asset
            //--------------------------------------------------------------------------------------------------

            // add security log
            // since this is not handled as a page postback, theres no "Viewstate" settings
            // so 2 options either we keep an original setting for each value in hid values, or just get them from the db as part of the 
            // update above, since we are already passing in 15 or so fields, lets just get the values at the start and reference them here
            if (sMode == "edit")
            {
                string sOrigCredUsername = GetCredentialNameFromID(sOriginalCredentialID.Replace("'", "")).ToString();
                string sCurrentCredUsername = GetCredentialNameFromID(sCredentialID.Replace("'", "")).ToString();
                ui.WriteObjectChangeLog(Globals.acObjectTypes.Asset, sAssetID, sAssetName.Trim().Replace("'", "''") + " Name", sOriginalAssetName, sAssetName);
                ui.WriteObjectChangeLog(Globals.acObjectTypes.Asset, sAssetID, sAssetName.Trim().Replace("'", "''") + " Address", sOriginalAddress, sAddress);
                ui.WriteObjectChangeLog(Globals.acObjectTypes.Asset, sAssetID, sAssetName.Trim().Replace("'", "''") + " Port", sOriginalPort, sPort);
                ui.WriteObjectChangeLog(Globals.acObjectTypes.Asset, sAssetID, sAssetName.Trim().Replace("'", "''") + " DB Name", sOriginalDbName, sDbName);
                ui.WriteObjectChangeLog(Globals.acObjectTypes.Asset, sAssetID, sAssetName.Trim().Replace("'", "''") + " Connection Type", sOriginalConnectionType, sConnectionType);
                ui.WriteObjectChangeLog(Globals.acObjectTypes.Asset, sAssetID, sAssetName.Trim().Replace("'", "''") + " Credential", sOrigCredUsername, sCurrentCredUsername);
                ui.WriteObjectChangeLog(Globals.acObjectTypes.Asset, sAssetID, sAssetName.Trim().Replace("'", "''") + " Status", sOriginalAssetStatus, sAssetStatus);
				ui.WriteObjectChangeLog(Globals.acObjectTypes.Asset, sAssetID, sAssetName.Trim().Replace("'", "''") + " ConnString", sOriginalConnString, sConnString);
            }
            else
            {
                ui.WriteObjectAddLog(Globals.acObjectTypes.Asset, sAssetID, sAssetName.Trim().Replace("'", "''"), "Asset Created");
            }


            // no errors to here, so return an empty string
            return "";
        }

        [WebMethod()]
        public static string LoadAssetData(string sAssetID)
        {
            dataAccess dc = new dataAccess();
			acUI.acUI ui = new acUI.acUI();
            
			string sSql = null;
            string sErr = null;

            string sAssetName = null;
            string sPort = null;
            string sDbName = null;
            string sAddress = null;
            string sConnectionType = null;
            string sUserName = null;
            string sSharedOrLocal = null;
            string sCredentialID = null;
            string sPassword = null;
            string sDomain = null;
            string sAssetStatus = null;
            string sPrivilegedPassword = null;
            string sSharedCredName = null;
            string sSharedCredDesc = null;
            string sConnString = null;

            DataRow dr = null;
            sSql = "select a.asset_name, a.asset_status, a.port, a.db_name, a.conn_string," +
                   " a.address, a.connection_type, ac.username, ac.password, ac.privileged_password, ac.domain, ac.shared_cred_desc, ac.credential_name, a.credential_id," +
                   " case when ac.shared_or_local = '0' then 'Shared' else 'Local' end as shared_or_local" +
                   " from asset a " +
                   " left outer join asset_credential ac on ac.credential_id = a.credential_id " +
                   " where a.asset_id = '" + sAssetID + "'";

            if (!dc.sqlGetDataRow(ref dr, sSql, ref sErr))
            {
                throw new Exception(sErr);
            }
            else
            {
                if (dr != null)
                {
                    sAssetName = dr["asset_name"].ToString();
                    sPort = (object.ReferenceEquals(dr["port"], DBNull.Value) ? "" : dr["port"].ToString());
                    sDbName = (object.ReferenceEquals(dr["db_name"], DBNull.Value) ? "" : dr["db_name"].ToString());
                    sAddress = (object.ReferenceEquals(dr["address"], DBNull.Value) ? "" : dr["address"].ToString().Replace("\\\\", "||"));
                    sAddress = sAddress.Replace("\\", "|");
                    sConnectionType = (object.ReferenceEquals(dr["connection_type"], DBNull.Value) ? "" : dr["connection_type"].ToString());
                    sUserName = (object.ReferenceEquals(dr["username"], DBNull.Value) ? "" : dr["username"].ToString());
                    sConnString = (object.ReferenceEquals(dr["conn_string"], DBNull.Value) ? "" : dr["conn_string"].ToString());
                    sSharedOrLocal = (object.ReferenceEquals(dr["shared_or_local"], DBNull.Value) ? "" : dr["shared_or_local"].ToString());
                    sCredentialID = (object.ReferenceEquals(dr["credential_id"], DBNull.Value) ? "" : dr["credential_id"].ToString());
                    sPassword = (object.ReferenceEquals(dr["password"], DBNull.Value) ? "" : "($%#d@x!&");
                    sDomain = (object.ReferenceEquals(dr["domain"], DBNull.Value) ? "" : dr["domain"].ToString());
                    sAssetStatus = dr["asset_status"].ToString();
                    sPrivilegedPassword = (object.ReferenceEquals(dr["privileged_password"], DBNull.Value) ? "" : "($%#d@x!&");
                    sSharedCredName = (object.ReferenceEquals(dr["credential_name"], DBNull.Value) ? "" : dr["credential_name"].ToString());
                    sSharedCredDesc = (object.ReferenceEquals(dr["shared_cred_desc"], DBNull.Value) ? "" : dr["shared_cred_desc"].ToString());
                }
            }

            // Return the asset object as a JSON 
            StringBuilder sbAssetValues = new StringBuilder();
            sbAssetValues.Append("{");
            sbAssetValues.AppendFormat("\"{0}\" : \"{1}\",", "sAssetName", ui.packJSON(sAssetName));
            sbAssetValues.AppendFormat("\"{0}\" : \"{1}\",", "sPort", sPort);
            sbAssetValues.AppendFormat("\"{0}\" : \"{1}\",", "sDbName", sDbName);
            sbAssetValues.AppendFormat("\"{0}\" : \"{1}\",", "sAddress", sAddress);
            sbAssetValues.AppendFormat("\"{0}\" : \"{1}\",", "sConnectionType", sConnectionType);
            sbAssetValues.AppendFormat("\"{0}\" : \"{1}\",", "sUserName", sUserName);
            sbAssetValues.AppendFormat("\"{0}\" : \"{1}\",", "sConnString", ui.packJSON(sConnString));
            sbAssetValues.AppendFormat("\"{0}\" : \"{1}\",", "sSharedOrLocal", sSharedOrLocal);
            sbAssetValues.AppendFormat("\"{0}\" : \"{1}\",", "sCredentialID", sCredentialID);
            sbAssetValues.AppendFormat("\"{0}\" : \"{1}\",", "sPassword", sPassword);
            sbAssetValues.AppendFormat("\"{0}\" : \"{1}\",", "sDomain", sDomain);
            sbAssetValues.AppendFormat("\"{0}\" : \"{1}\",", "sPriviledgedPassword", sPrivilegedPassword);
            sbAssetValues.AppendFormat("\"{0}\" : \"{1}\",", "sSharedCredName", sSharedCredName);
            sbAssetValues.AppendFormat("\"{0}\" : \"{1}\",", "sSharedCredDesc", ui.packJSON(sSharedCredDesc));

            //last value, no comma on the end
            sbAssetValues.AppendFormat("\"{0}\" : \"{1}\"", "sAssetStatus", sAssetStatus);
            sbAssetValues.Append("}");

            return sbAssetValues.ToString();
        }

        [WebMethod()]
        public static string GetCredentialSelector()
        {

            dataAccess dc = new dataAccess();
            string sSql = null;
            string sErr = null;

            StringBuilder sb = new StringBuilder();

            // return either the shared sShared==0  which include descriptions
            // or local sShared==1 just the username


            sSql = "select credential_id, username, domain, shared_cred_desc from asset_credential where shared_or_local = 0 order by username";
            DataTable dt = new DataTable();
            if (!dc.sqlGetDataTable(ref dt, sSql, ref sErr))
            {
                return sErr;
            }
            else
            {
                sb.Append("<table id='tblCredentialSelector' width='99%'><thead><tr><th class='col_header'>Username</th><th class='col_header'>Domain</th><th class='col_header'>Description</th></th></thead><tbody>");

                foreach (DataRow dr in dt.Rows)
                {
                    sb.Append("<tr class='select_credential' credential_id='" + dr["credential_id"].ToString() + "'><td tag='selectablecrd' class='row'>" + dr["username"].ToString() + "</td><td tag='selectablecrd' class='row'>" + dr["domain"].ToString() + "</td><td class='row'>" + dr["shared_cred_desc"].ToString() + "</td></tr>");
                }

            }
            sb.Append("</tbody></table>");



            return sb.ToString();
        }



        #endregion

        #region "Buttons"

        protected void btnGetPage_Click(object sender, System.EventArgs e)
        {
            GetAssets();
        }
        protected void btnSearch_Click(object sender, EventArgs e)
        {
            // we are searching so clear out the page value
            hidPage.Value = "1";
            BindList();
        }


        #endregion

    }
}
