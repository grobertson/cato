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
using System.Text;
using System.Web;
using System.Web.UI;
using System.IO;
using Globals;
using System.Data;
using System.Text.RegularExpressions;
using System.Net;

namespace acUI
{
    public class acUI : System.Web.UI.Page
    {
        dataAccess dc = new dataAccess();

        #region "Session Functions"
		public bool PutUserSettingsInSession(ref string sErr)
		{
			string sUserID = GetSessionUserID();
			if (!string.IsNullOrEmpty(sUserID))
			{
	            string sSQL = "select settings_xml from users where user_id = '" + sUserID + "'";
				string sSettingXML = "";
				if (!dc.sqlGetSingleString(ref sSettingXML, sSQL, ref sErr))
	            {
	                return false;
	            }
	            else
	            {
	                if (string.IsNullOrEmpty(sSettingXML))
					{
						//there are no settings!
						//create the row
						sSettingXML = "<settings></settings>";
						sSQL = "update users set settings_xml = '" + sSettingXML + "' where user_id = '" + sUserID + "'";
						if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
			                return false;
					}
					
	
	                if (string.IsNullOrEmpty(sSettingXML))
					{
						//something is just wrong if we land here... error out
						sErr = "Unable to find/repair application_settings.";
						return false;
					}
					else
					{
						//woot! we have settings.
						XDocument xd = XDocument.Parse(sSettingXML);
						if (xd != null)
						{
							SetSessionObject("user_settings", xd, "Security");
							return true;
						}
						else
						{
							sErr = "Unable to parse and load User Settings.";
							return false;
						}
					}
	            }	
			}
			else
			{
				sErr = "Unable to load User Settings - GetSessionUserID returned nothing.";
				return false;
			}
		}
		public bool PutApplicationSettingsInSession(ref string sErr)
		{
            string sSQL = "select setting_xml from application_settings where id = 1";
			string sSettingXML = "";
			if (!dc.sqlGetSingleString(ref sSettingXML, sSQL, ref sErr))
            {
                return false;
            }
            else
            {
                if (string.IsNullOrEmpty(sSettingXML))
				{
					//there are no settings!
					//create the row
					sSettingXML = "<settings></settings>";
					sSQL = "insert into application_settings values (1, '" + sSettingXML + "')";
					if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
		                return false;
				}
				

                if (string.IsNullOrEmpty(sSettingXML))
				{
					//something is just wrong if we land here... error out
					sErr = "Unable to find/repair application_settings.";
					return false;
				}
				else
				{
					//woot! we have settings.
					XDocument xd = XDocument.Parse(sSettingXML);
					if (xd != null)
					{
						SetSessionObject("application_settings", xd, "Security");
						return true;
					}
					else
					{
						sErr = "Unable to parse and load Application Settings.";
						return false;
					}
				}
            }			
		}
		public string GetApplicationSetting(string sXPath)
		{
			//get it from the session collection
			XDocument xd = (XDocument)GetSessionObject("application_settings", "Security");
			if (xd != null)
			{
				XElement xe = xd.XPathSelectElement("//settings/" + sXPath);
				if (xe != null)
				{
					return xe.Value;
				}
				return null;
			}
			else
			{
				throw new Exception("Unable to read Application Settings from the session.");
			}
		}
		public bool SetApplicationSetting(string sCategory, string sSetting, string sValue, ref string sErr)
		{
			//get it from the session collection
			XDocument xd = (XDocument)GetSessionObject("application_settings", "Security");
			if (xd != null)
			{
				XElement xSettings = xd.Element("settings");
				if (xSettings != null)
				{
					XElement xCat = xSettings.Element(sCategory);
					if (xCat == null)
					{
						xSettings.Add(new XElement(sCategory));
						xCat = xSettings.Element(sCategory);
					}
					
					XElement xSetting = xCat.Element(sSetting);
					if (xSetting == null)
					{
						xCat.Add(new XElement(sSetting, sValue));
					}
					else
					{
						xSetting.Value = sValue;
					}
				
	
					//update the XML both in the session and in the db.
					SetSessionObject("application_settings", xd, "Security");
						
					string sSQL = "update application_settings set setting_xml = '" + xd.ToString(SaveOptions.DisableFormatting) + "' where id = 1";
					if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
						return false;
					
					return true;

				}
				throw new Exception("Application Settings 'settings' section not found in session xml.");
			}
			else
			{
				throw new Exception("Unable to read Application Settings from the session.");
			}
		}
		//this one shoves the site.master.xml into the session
        public void SetSitemaster(ref string sErr)
        {
			try 
			{
				XDocument xSiteMaster = XDocument.Load(HttpContext.Current.Server.MapPath("~/pages/site.master.xml"));
				
				if (xSiteMaster == null)
				{
					sErr = "XML file is missing or unreadable.";
					return;
				}
				else 
				{
					SetSessionObject("site_master_xml", xSiteMaster, "Security");
				}
			} catch (Exception ex) {
				sErr = "XML is invalid." + ex.Message;
				return;
			}
		}
		//this one returns the entire FunctionCategories class
        public FunctionCategories GetTaskFunctionCategories()
        {
            return (FunctionCategories) GetSessionObject("function_categories", "Security");
		}
		//this one returns the flattened Functions class
        public Functions GetTaskFunctions()
        {
            return (Functions) GetSessionObject("functions", "Security");
		}
		//this one returns just one specific function
        public Function GetTaskFunction(string sFunctionName)
        {
            Functions funcs =  GetTaskFunctions();
			if (funcs != null)
			{
				try {
					Function fn = funcs[sFunctionName];
					if (fn != null)
						return fn;
					else 
						return null;				
				} catch (Exception ex) {
					return null;
				}
			}
			else
			{
				return null;
			}
		}
        public void SetTaskCommands(ref string sErr)
        {
			//load the task_commands.xml file into the session.  If it doesn't exist, we can't proceed.
			try 
			{
				//we load two classes here...
				//first, the category/function hierarchy
				FunctionCategories cats = FunctionCategories.Load(HttpContext.Current.Server.MapPath("~/pages/luCommands.xml"));
				SetSessionObject("function_categories", cats, "Security");
				
				//then the flat list of all functions for fastest lookups
				Functions funcs = new Functions(cats);
				SetSessionObject("functions", funcs, "Security");
			} catch (Exception ex) {
				sErr = "Unable to load Task Commands XML." + ex.Message;
			}
		}
        public void DeleteSessionObject(string Key, string CollectionName = "")
        {
            try
            {
                if (string.IsNullOrEmpty(CollectionName))
                {
                    Session.Remove(Key);
                }
                else
                {
                    Dictionary<string, object> d = (Dictionary<string, object>)Session[CollectionName];

                    //if the collection doesnt exist you can't delete the key.
                    if (Session[CollectionName] != null)
                    {
                        if (d.ContainsKey(Key))
                            d.Remove(Key);
                    }
                }
            }
            catch (Exception ex)
            {
                HttpContext.Current.Response.Write(ex.Message);
            }
        }
        public object GetSessionObject(string Key, string CollectionName = "")
        {
            // If the session is missing, redirect to the login screen
            // Warning!!! Optional parameters not supported
            if (Session != null)
            {
                try
                {

                    if (CollectionName == "")
                    {
                        if (Session[Key] == null)
                        {
                            return null;
                        }
                        else
                        {
                            return Session[Key];
                        }
                    }
                    else if (Session[CollectionName] == null)
                    {
                        return null;
                    }

                    //still here?  maybe a keyvaluepair?
                    Dictionary<string, object> d = (Dictionary<string, object>)Session[CollectionName];
                    if (d.ContainsKey(Key))
                    {
                        return d[Key];
                    }
                    else
                    {
                        return null;
                    }
                }
                catch (Exception ex)
                {
                    HttpContext.Current.Response.Write((ex.Message + "\r\n"));
                    return null;
                }
            }
            else
            {
                Logout("Your Session has expired. (Session) Please log in again.");
                return null;
            }
        }
        public void SetSessionObject(string Key, object Value, string CollectionName = "")
        {
            try
            {
                if (string.IsNullOrEmpty(CollectionName))
                {
                    //if the key doesn't exist add it, if it does overwrite it
                    if (Session[Key] == null)
                    {
                        Session.Add(Key, Value);
                    }
                    else
                    {
                        Session[Key] = Value;
                    }
                }
                else
                {
                    //if the collection already exists add to it.  If not then create it.
                    if (Session[CollectionName] == null)
                    {
                        Dictionary<string, object> d = new Dictionary<string, object>();
                        d.Add(Key, Value);
                        Session.Add(CollectionName, d);
                    }
                    else
                    {
                        Dictionary<string, object> d = (Dictionary<string, object>)Session[CollectionName];
                        //if the key doesn't exist add it, if it does overwrite it
                        if (d.ContainsKey(Key))
                            d.Remove(Key);

                        d.Add(Key, Value);
                    }
                }
            }
            catch (Exception ex)
            {
                HttpContext.Current.Response.Write(ex.Message);
            }
        }
        public bool UpdateUserSession(ref string sMsg)
        {
            //This code will:
            //get the user id.  If GetSessionUserID doesn't find the session, it will throw us back to the login.

            //Then...Check the session table, and kill the GUI if the row for the user_id has been removed.
            //Update the heartbeat if the row still exists.

            string sUserID = GetSessionUserID();
            if (!string.IsNullOrEmpty(sUserID))
            {
                string sUserName = GetSessionUsername();
                string sAddress = Convert.ToString(GetSessionObject("ip_address", "Security"));

                string sSQL = null;
                string sErr = "";

                //First, make sure this user account is still enabled.
                sSQL = "select u.status, u.user_id, s.kick " +
                    "from users u " +
                    "left outer join user_session s " +
                    "on s.user_id = u.user_id " +
                    "where u.user_id = '" + sUserID + "'" +
                    " and address = '" + sAddress + "'";
                DataTable dt = new DataTable();

                if (dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
                {
                    if (dt.Rows.Count != 1)
                    {
                        Logout("Your session has ended. (User Session Table)");
                    }
                    else
                    {
                        DataRow dr = dt.Rows[0];
                        if (Convert.ToInt32(dr["status"]) == 0)
                        {
                            //Log this login in the security_audit
                            dc.addSecurityLog(sUserID, SecurityLogTypes.Security, SecurityLogActions.UserLogout, acObjectTypes.None, sUserName, "", ref sErr);

                            Logout("Your session has been ended because your user account has been disabled.");
                        }
                        else
                        {
                            if (Convert.ToInt32(dr["kick"]) == 1)
                            {
                                dc.addSecurityLog(sUserID, SecurityLogTypes.Security, SecurityLogActions.Other, acObjectTypes.None, sUserName, "Session Warned", ref sErr);

                                sSQL = "update user_session set kick = 2, heartbeat = now() where user_id = '" + sUserID + "' and address = '" + sAddress + "'";
                                dc.sqlExecuteUpdate(sSQL, ref sErr);

                                if (string.IsNullOrEmpty(sErr))
                                {
                                    sMsg = "The system is going down for maintenance.  Please save your work and log out.  This session will close automatically in 1 minute.";
                                    return true;
                                }
                                else
                                {
                                    Logout(sErr);
                                }
                            }
                            else if (Convert.ToInt32(dr["kick"]) > 1)
                            {
                                dc.addSecurityLog(sUserID, SecurityLogTypes.Security, SecurityLogActions.Other, acObjectTypes.None, sUserName, "Session Kicked", ref sErr);

                                sSQL = "update user_session set kick = 3, heartbeat = now() where user_id = '" + sUserID + "' and address = '" + sAddress + "'";
                                dc.sqlExecuteUpdate(sSQL, ref sErr);

                                if (string.IsNullOrEmpty(sErr))
                                {
                                    Logout("The system is going down now.  Your session has been ended.");
                                }
                                else
                                {
                                    Logout(sErr);
                                }
                            }
                            else
                            {
                                sSQL = "update user_session set heartbeat = now() where user_id = '" + sUserID + "' and address = '" + sAddress + "'";
                                dc.sqlExecuteUpdate(sSQL, ref sErr);
                            }
                        }
                    }
                }
                else
                {
                    Logout(sErr);
                }
            }
            else
            {
                Logout("Your Session has ended. (UID)");
            }

            return true;

        }
        public string GetSessionUserFullName()
        {
            object o = GetSessionObject("user_full_name", "Security");
            if (o == null)
                Logout("Server Session has expired (3). Please log in again.");
            if (o != null)
                return o.ToString();
            else
                return "";
        }
        public string GetSessionUserRole()
        {
            object o = GetSessionObject("user_role", "Security");
            if (o == null)
                Logout("Server Session has expired (4). Please log in again.");
            if (o != null)
                return o.ToString();
            else
                return "";
        }
        public string GetSessionUserTagsByName()
        {
            object o = GetSessionObject("user_tags", "Security");
            if (o == null)
                Logout("Server Session has expired (5). Please log in again.");
            if (o != null)
                return o.ToString();
            else
                return "";
        }
        public string GetSessionUserID()
        {
            /*
             This will work when we are ready to stop using the session!
             
            string sUserID = CurrentUser.UserID;
            if (string.IsNullOrEmpty(sUserID))
            {
                Logout("Server Session has expired (1). Please log in again.");
                return "";
            }
            else
                return sUserID;

            */
            
            object o = GetSessionObject("user_id", "Security");
            if ((o == null))
            {
                Logout("Server Session has expired (1). Please log in again.");
            }
            if (!(o == null))
            {
                return o.ToString();
            }
            else
            {
                return "";
            }
        }
        public string GetSessionUsername()
        {
            object o = GetSessionObject("user_name", "Security");
            if (o == null)
                Logout("Server Session has expired (2). Please log in again.");
            if (o != null)
                return o.ToString();
            else
                return "";
        }
        #endregion
        #region "Security Functions"
        public bool UserIsInRole(string sRoleToCheck)
        {
            string sUserRole = GetSessionUserRole();
            if (sUserRole.ToLower() == sRoleToCheck.ToLower())
                return true;
            else
                return false;
        }
        public bool UserHasTag(string sGroup)
        {
            //this looks up roles by name
            string sGroups = null;
            sGroups = GetSessionUserTagsByName();
            if (sGroups.IndexOf(sGroup) > -1)
                return true;
            else
                return false;
        }
        public bool UserAndObjectTagsMatch(string sObjectID, int iObjectType)
        {
            //will return true if the specified object id and type share any tags with the user
            int iResult = 0;
            string sErr = "";
            string sSQL = "select 1 from object_tags otu" +
                " join object_tags oto on otu.tag_name = oto.tag_name" +
                " where(otu.object_type = 1)" +
                " and otu.object_id = '" + GetSessionUserID() + "'" +
                " and oto.object_type = " + iObjectType + "" +
                " and oto.object_id = '" + sObjectID + "'";

            dc.sqlGetSingleInteger(ref iResult, sSQL, ref sErr);

            return dc.IsTrue(iResult);
        }
        public void addPageViewLog()
        {
            //this logs views of 'pages' in the gui.  Reports are logged differently.
            if (!Page.IsPostBack)
            {
                if (GetSessionObject("page_view_logging", "Security") != null)
                {
                    string sErr = "";

                    if (dc.IsTrue(GetSessionObject("page_view_logging", "Security").ToString()))
                    {
                        //what is the filename of this page? (Retarded that .net doesn't have a clean way to get this.)
                        string sPageName = null;
                        string[] sTmp = HttpContext.Current.Request.ServerVariables["SCRIPT_NAME"].Split('/');
                        sPageName = sTmp[sTmp.GetUpperBound(0)];

                        //we do something neat here... we don't want to flood the table with pave view logs if the user keeps hitting the same page.
                        //so, when we write a log we write the page name in a cookie.
                        //if the subsequent calls are for the same page, we just skip them.

                        //but we set the cookie to expire in 15 minutes

                        string sLastPage = GetCookie("last_logged_page_view");
                        if (!string.IsNullOrEmpty(sLastPage))
                        {
                            if (sLastPage == sPageName)
                                return;
                        }

                        dc.addSecurityLog(GetSessionUserID(), SecurityLogTypes.Usage, SecurityLogActions.PageView, acObjectTypes.None, "", HttpContext.Current.Request.RawUrl, ref sErr);
                        SetCookie("last_logged_page_view", sPageName, DateTime.Now.AddMinutes(15).ToString());
                    }
                }
            }
        }
        public void ReportSecurityIssue(string sPageName, string sMessage = "")
        {
            if (string.IsNullOrEmpty(sPageName))
            {
                string[] sTmp = HttpContext.Current.Request.Path.Split('/');
                sPageName = sTmp[sTmp.GetUpperBound(0)];
            }

            string sErr = "";
            dc.addSecurityLog(GetSessionUserID(), SecurityLogTypes.Security, SecurityLogActions.PageView, acObjectTypes.None, sPageName, "Illegal page access attempt: [" + sPageName + "].", ref sErr);

            if (!string.IsNullOrEmpty(sMessage))
            {
                SetSessionObject("NotAllowedMessage", sMessage, "Security");
            }

            HttpContext.Current.Response.Redirect("~/pages/notAllowed.aspx", false);
        }
        public void IsPageAllowed(string sMessage = "")
        {
            // IF the page does not exist in the master list (new page), it's a dev bug and must be added,
            // but you will not be able to see it.
            // IF the page does exist, it will be checked to see if the current user has the privilege of viewing it

            string sRole = GetSessionUserRole();
            string sPage = GetPageNameFromURL(GetPageURL());

            //FIRST! --- the Administrator role gets everything, no check required.
            if (sRole == "Administrator")
                return;

            // If no role is passed in return false
            if (string.IsNullOrEmpty(sPage))
                ReportSecurityIssue("Error: No page name.");
            if (string.IsNullOrEmpty(sRole))
                ReportSecurityIssue(sPage + "User has no role.");


            //but don't choke on certain pages, even if they aren't in the lookup table
            //otherwise everything would fall apart.
            string sAllowedPagesNoMatterWhat = "notAllowed.aspx,home.aspx,about.aspx,userPreferenceEdit.aspx";

            if (sAllowedPagesNoMatterWhat.IndexOf(sPage) == -1)
            {
				//this will check against what it read in the xml file
				//which should be cached in the security session at login into a csv string called allowed_pages
                string sAllowedPages = GetSessionObject("allowed_pages", "Security").ToString();
                if (sAllowedPages.ToLower().IndexOf(sPage.ToLower()) == -1)
                    ReportSecurityIssue(sPage, sMessage);
            }
        }
        public void Logout(string sMsg)
        {
			string sErr = "";

            if (string.IsNullOrEmpty(sMsg))
                sMsg = "Session Ended";

            // 2-17-2010 NSC: Temporarily logging all calls to this, as we try to track down a random session ending bug
            // Warning!!! Optional parameters not supported
            string sPageName = "";
            string[] sTmp = HttpContext.Current.Request.Path.Split('/');
            sPageName = sTmp[sTmp.GetUpperBound(0)];

            dc.addSecurityLog("No Session", SecurityLogTypes.Security, SecurityLogActions.UserSessionDrop, acObjectTypes.None, sPageName, "Logout called from : [" + sPageName + "].", ref sErr);


            System.Web.Security.FormsAuthentication.SignOut();
            System.Web.Security.FormsAuthentication.RedirectToLoginPage("msg=" + Server.UrlEncode(sMsg));
            HttpContext.Current.Response.End();
        }
        #endregion
        #region "Cookie Functions"
        public void SetCookie(string Key, string Value, string ExpiresOn = "")
        {
            HttpCookie c = default(HttpCookie);
            c = new HttpCookie(Key, Value);

            if (!string.IsNullOrEmpty(ExpiresOn))
            {
                //is the string a valid date?
                DateTime ValidDate = default(DateTime);
                if (DateTime.TryParse(ExpiresOn, out ValidDate))
                {
                    c.Expires = ValidDate;
                }
            }
            HttpContext.Current.Response.Cookies.Set(c);
        }
        public string GetCookie(string Key)
        {
            string s = "";
            try
            {
                s = HttpContext.Current.Request.Cookies.Get(Key).Value;
            }
            catch (Exception)
            {
            }

            return s;
        }
        #endregion
        #region "Output Functions"
        public string GetSnip(string sString, int iMaxLength)
        {
            //helpful for short notes or long notes with a short title line.

            //odd behavior, but web forms seems to put just a \n as the newline entered in a textarea.
            //so I'll test for both just to be safe.
            //btw... Environment.NewLine IS \r\n on windows and \n on unix

            string sReturn = "";

            if (!string.IsNullOrEmpty(sString))
            {
                bool bShowElipse = false;

                //test for line breaks
                int iLength = sString.IndexOf(Environment.NewLine);
                if (iLength < 0)
                    iLength = sString.IndexOf("\\r\\n");
                if (iLength < 0)
                    iLength = sString.IndexOf("\\r");
                if (iLength < 0)
                    iLength = sString.IndexOf("\\n");
                if (iLength < 0)
                    iLength = iMaxLength;

                //now, if what we are showing is shorter than the entire field, show an elipse
                //if it is the entire field, set the length
                if (iLength < sString.Length)
                {
                    bShowElipse = true;
                }
                else
                {
                    iLength = sString.Length;
                }

                sReturn += sString.Substring(0, iLength);
                if (bShowElipse)
                {
                    sReturn += " ... ";
                }
            }

            return SafeHTML(sReturn);
        }
        public string SafeHTML(string sInput)
        {
            return Server.HtmlEncode(sInput);
        }
        public string FixBreaks(string sInput)
        {
            return sInput.Replace("\r\n", "<br />").Replace("\r", "<br />").Replace("\n", "<br />").Replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;");
        }

        public void RaiseError(Page oPage, string sMsg, bool bLogToDatabase, string sAdditionalInformation = "")
        {
            //string sErr = "";
            if (bLogToDatabase)
            {
                //if (dc.IsTrue(getConfigParameter("General", "ui_error_logging")))
                //{
                //    if (!WriteErrorLog(sMsg, sAdditionalInformation, ref sErr))
                //    {
                //        //this shouldn't happen except in dire circumstances
                //        //if we can't write the log, give the user an error.
                //        sErr = "ERROR WRITING ERROR LOG: " + sErr;
                //    }
                //}
            }

            //now, how to invoke a client script?
            if (!string.IsNullOrEmpty(sMsg))
            {
                //ticks and slashes and javascript won't play.
                sMsg = sMsg.Replace("'", "").Replace("\\", "").Replace("\\r\\n", "\\n").Replace("\\r", "\\n").Replace(Environment.NewLine, "\\n");
                sAdditionalInformation = sAdditionalInformation.Replace("'", "").Replace("\\", "").Replace("\\r\\n", "\\n").Replace("\\r", "\\n").Replace(Environment.NewLine, "\\n");

                sMsg = "setTimeout(\"showAlert('" + sMsg + "', '" + sAdditionalInformation + "');\",500);";
                ScriptManager.RegisterStartupScript(oPage, typeof(string), NewGUID(), sMsg, true);
            }
        }

        public void RaiseInfo(Page oPage, string sMsg, string sAdditionalInformation = "")
        {
            if (!string.IsNullOrEmpty(sMsg))
            {
                //ticks and slashes and javascript won't play.
                sMsg = sMsg.Replace("'", "").Replace("\\", "").Replace("\\r\\n", "\\n").Replace("\\r", "\\n").Replace(Environment.NewLine, "\\n");
                sAdditionalInformation = sAdditionalInformation.Replace("'", "").Replace("\\", "").Replace("\\r\\n", "\\n").Replace("\\r", "\\n").Replace(Environment.NewLine, "\\n");

                sMsg = "showInfo('" + sMsg + "', '" + sAdditionalInformation + "');";
                ScriptManager.RegisterStartupScript(oPage, typeof(string), NewGUID(), sMsg, true);
            }
        }
        public bool SendEmailMessage(string sTo, string sFrom, string sSubject, string sBody, ref string sErr)
        {
            string sSQL = "insert into message (date_time_entered,process_type,status,msg_to,msg_from,msg_subject,msg_body)" + " values (now(), 1, 0, '" + sTo + "', '" + sFrom + "','" + sSubject.Replace("'", "''").Trim() + "','" + sBody.Replace("'", "''").Trim() + "')";

            if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
                return false;

            return true;
        }

        #endregion
        #region "Misc Functions"
        public string PercentEncodeRfc3986(string s)
        {
            s = HttpUtility.UrlEncode(s, System.Text.Encoding.UTF8);
            s = s.Replace("'", "%27").Replace("(", "%28").Replace(")", "%29").Replace("*", "%2A").Replace("!", "%21").Replace("%7e", "~").Replace("+", "%20");
            StringBuilder sb = new StringBuilder(s);
            for (int i = 0; i < sb.Length; i++)
            {
                if (sb[i] == '%')
                {
                    if (Char.IsLetter(sb[i + 1]) || Char.IsLetter(sb[i + 2]))
                    {
                        sb[i + 1] = Char.ToUpper(sb[i + 1]); sb[i + 2] = Char.ToUpper(sb[i + 2]);
                    }
                }
            }
            return sb.ToString();
        }
        public string GetSortedParamsAsString(SortedDictionary<String, String> paras, bool isCanonical)
        {
            String sParams = "";
            String sKey = null;
            String sValue = null;
            String separator = "";
            foreach (KeyValuePair<string, String> entry in paras)
            {
                sKey = PercentEncodeRfc3986(entry.Key);
                sValue = PercentEncodeRfc3986(entry.Value);
                //if (isCanonical)
                //{
                //    sKey = PercentEncodeRfc3986(sKey);
                //    sValue = PercentEncodeRfc3986(sValue);
                //}
                sParams += separator + sKey + "=" + sValue;
                separator = "&";
            }

            return sParams;
        }
        public string GetSHA1(string sKey, string sStringToSign)
        {
            System.Security.Cryptography.HMACSHA1 MySigner =
                new System.Security.Cryptography.HMACSHA1(System.Text.Encoding.UTF8.GetBytes(sKey));
            string SignatureValue =
                Convert.ToBase64String(MySigner.ComputeHash(System.Text.Encoding.UTF8.GetBytes(sStringToSign)));
            return SignatureValue;
        }
        public string GetSHA256(string sKey, string sStringToSign)
        {
            System.Security.Cryptography.HMACSHA256 MySigner =
                new System.Security.Cryptography.HMACSHA256(System.Text.Encoding.UTF8.GetBytes(sKey));
            string SignatureValue =
                Convert.ToBase64String(MySigner.ComputeHash(System.Text.Encoding.UTF8.GetBytes(sStringToSign)));
            return SignatureValue;
        }

		//these four functions are primarily used to encode/decode data being sent via JSON to the server
		//or back to the client.
        public string packJSON(string sIn)
        {
			if (string.IsNullOrEmpty(sIn))
			    return sIn;
			//NOTE! base64 encoding still has a couple of reserved characters so we explicitly replace them AFTER
    		string sOut = base64Encode(sIn);
			return sOut.Replace("/", "%2F").Replace("+", "%2B");
        }
        public string unpackJSON(string sIn)
        {
			if (string.IsNullOrEmpty(sIn))
			    return sIn;
			//NOTE! base64 decoding still has a couple of reserved characters so we explicitly replace them BEFORE
    		string sOut = sIn.Replace("%2F", "/").Replace("%2B", "+");
			return base64Decode(sOut);
        }
		public string base64Encode(string data)
		{
		    try
		    {
		        byte[] encData_byte = new byte[data.Length];
		        encData_byte = System.Text.Encoding.UTF8.GetBytes(data);    
		        string encodedData = Convert.ToBase64String(encData_byte);
		        return encodedData;
		    }
		    catch(Exception e)
		    {
		        throw new Exception("Error in base64Encode" + e.Message);
		    }
		}		
		public string base64Decode(string data)
		{
		    try
		    {
		        System.Text.UTF8Encoding encoder = new System.Text.UTF8Encoding();  
		        System.Text.Decoder utf8Decode = encoder.GetDecoder();
		    
		        byte[] todecode_byte = Convert.FromBase64String(data);
		        int charCount = utf8Decode.GetCharCount(todecode_byte, 0, todecode_byte.Length);    
		        char[] decoded_char = new char[charCount];
		        utf8Decode.GetChars(todecode_byte, 0, todecode_byte.Length, decoded_char, 0);                   
		        string result = new String(decoded_char);
		        return result;
		    }
		    catch(Exception ex)
		    {
		        throw new Exception("Error in UI.base64Decode" + ex.Message);
		    }
		}
				
		//a wrapper around the IsTrue function in the DataClass for pages that don't include the DataClass
		public bool IsTrue(object o)
		{
			return dc.IsTrue(o);
		}
		
		//Get data via HTTP
		public string HTTPGet(string sURL, int iTimeout, ref string sErr)
		{
			string sResult = "";
			try {
				// Create a request for the URL. 
				//WebRequest request = WebRequest.Create(sAPICall);
				HttpWebRequest request = WebRequest.Create (sURL) as HttpWebRequest;
				request.Method = "GET";
				request.Timeout = iTimeout;
				
				HttpWebResponse response = request.GetResponse() as HttpWebResponse;
				
				if (response.StatusCode == HttpStatusCode.OK) {
					// Get the stream containing content returned by the server.
					Stream dataStream = response.GetResponseStream();
					// Open the stream using a StreamReader for easy access.
					StreamReader sr = new StreamReader (dataStream);
					// Read the content.
					sResult = sr.ReadToEnd();
					// Clean up the streams and the response.
					sr.Close();
					response.Close();

					return sResult;
				}
				else
				{
					sErr = "<code>" + response.StatusCode.ToString() + "</code>";
					return "";
				}
				
				
			} catch (WebException ex) {
				using (WebResponse response = ex.Response) {
					if (response != null) {
						HttpWebResponse httpResponse = (HttpWebResponse)response;
						sErr = "HTTP Status Code:<br /><code>" + httpResponse.StatusCode.ToString();
						using (Stream data = response.GetResponseStream()) {
							string text = new StreamReader (data).ReadToEnd();
							sErr += text;
						}
						sErr += "</code>";
					} else
						sErr = "<code>" + ex.Message + "</code>";
				}
				return "";
			} catch (Exception ex) {
				sErr = "<code>" + ex.Message + "</code>";
				return "";
			}
		}
		
		//Get data via HTTP and do not error under any circumstances
		public string HTTPGetNoFail(string sURL)
		{
			string sResult = "";
			try {
				// Create a request for the URL. 
				HttpWebRequest request = WebRequest.Create (sURL) as HttpWebRequest;
				request.Method = "GET";
				request.Timeout = 4000;
				
				HttpWebResponse response = request.GetResponse() as HttpWebResponse;
				if (response.StatusCode == HttpStatusCode.OK) {
					// Get the stream containing content returned by the server.
					Stream dataStream = response.GetResponseStream();
					// Open the stream using a StreamReader for easy access.
					StreamReader sr = new StreamReader (dataStream);
					// Read the content.
					sResult = sr.ReadToEnd();
					// Clean up the streams and the response.
					sr.Close();
					response.Close();

					return sResult;
				}
				else
				{
					return "";
				}				
			} catch (WebException) {
				return "";
			} catch (Exception) {
				return "";
			}
		}
		
		//Checks whether the value is a 36 character GUID       
		public bool IsGUID(string String)
        {
            if (!string.IsNullOrEmpty(String))
            {
                if (String.Length == 36)
                {
                    Regex rx = new Regex("[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}");
                    if (rx.IsMatch(String))
                        return true;
                }
            }

            return false;
        }   
		//we would like all new guids to be lower case, so a wrapper function is used.
		public string NewGUID()
		{
			return Guid.NewGuid().ToString().ToLower();
		}
		public string GetPageURL()
        {
            string sURL = "";
            string sQS = "";
            sURL = HttpContext.Current.Request.ServerVariables["SCRIPT_NAME"].ToString();
            sQS = HttpContext.Current.Request.ServerVariables["QUERY_STRING"].ToString();
            return sURL + "?" + sQS;
        }
        public string GetPageNameFromURL(string sURL)
        {
            string sPageName = "";

            string[] sTmp = sURL.Split(Convert.ToChar("/"));
            //some urls (like itemselector) may have more than one file in them (the destination for example)
            //so, we can't just grab the last part of the url... we have to be smarter.
            //we'll step into the split array, and take the first one we encounter with a . in it.
            //(NOTE: this presupposed we will never have a directory on the application with a . in the directory name!)
            int i = 0;
            for (i = 0; i <= sTmp.GetUpperBound(0); i++)
            {
                if (sTmp[i].IndexOf(".") > -1)
                {
                    sPageName = sTmp[i];
                    break;
                }
            }

            //but if there was no dot, well I guess we will just take the last element
            if (string.IsNullOrEmpty(sPageName))
                sPageName = sTmp[sTmp.GetUpperBound(0)];

            sTmp = sPageName.Split('?');
            sPageName = sTmp[0];

            return sPageName;
        }
        public DataTable GetPageFromSessionTable(DataTable dt, int iPageSize, int iPageNum, int iStart, int iEnd, string sSortColumn, string sSortDir)
        {

            string sErr = "";

            DataTable dtSubset = null;

            DataTable dtSorted = null;
            // if we are sorting apply that now to the stored object

            if (!string.IsNullOrEmpty(sSortColumn))
            {
                DataView dv = new DataView(dt);
                // if the sort direction was passed in, use it
                if (!string.IsNullOrEmpty(sSortDir))
                {
                    dv.Sort = sSortColumn + " " + sSortDir;
                }
                else
                {
                    string sSortDirection = "asc";

                    // this may not be the best way, but for just do this now
                    // not sure how to change the classes to show up down arrows and such
                    // since the repeater rebuilds the header each time, maybe it shouldnt?
                    if (Convert.ToString(GetSessionObject("SortColumn", "SelectorListTables")) == sSortColumn)
                    {
                        // we are sorting the same column so swap the direction
                        if (Convert.ToString(GetSessionObject("SortDirection", "SelectorListTables")) == "asc")
                        {
                            sSortDirection = "desc";
                            SetSessionObject("SortDirection", sSortDirection, "SelectorListTables");
                        }
                    }
                    else
                    {
                        SetSessionObject("SortDirection", "asc", "SelectorListTables");
                        SetSessionObject("SortColumn", sSortColumn, "SelectorListTables");
                    }

                    dv.Sort = sSortColumn + " " + sSortDirection;
                }


                dtSorted = dv.ToTable();
            }
            else
            {
                SetSessionObject("SortColumn", "", "SelectorListTables");
                SetSessionObject("SortDirection", "", "SelectorListTables");
                dtSorted = dt;
            }

            if (iStart > 0 && iEnd > 0)
            {
                //start and end was passed, get that range
                if (iEnd > iStart)
                {
                    dtSubset = dc.GetRangeFromTable(dtSorted, iStart, iEnd, ref sErr);
                }
                else
                {
                    //but what to do if the end isn't > the start?
                    //this shouldn't be allowed but it's not validated
                    //should it warn or just die?
                }
            }
            else if (iPageSize > 0 && iPageNum > 0)
            {
                //specific page was passed, get that page
                dtSubset = dc.GetPageFromTable(dtSorted, iPageSize, iPageNum, ref sErr);
            }
            else
            {
                //no properties passed, get it all
                dtSubset = dtSorted;
            }

            return dtSubset;
        }
        public string DrawPager(int iTotalRows, int iPageSize, int iSelectedPage)
        {
            int iPageNum = 1;

            int iPages = Convert.ToInt32(Math.Ceiling(Convert.ToDouble(iTotalRows) / Convert.ToDouble(iPageSize)));

            string s = null;

            s = "<span href='#' class='pager_button' page='1'><< </span>";

            //this can be enhanced to only show a range, or a pick box, I don't care
            for (iPageNum = 1; iPageNum <= iPages; iPageNum++)
            {
                if (iPageNum == iSelectedPage)
                {
                    s += "<span class='pager_button pager_button_selected' page='" + iPageNum + "'>" + iPageNum + "&nbsp;</span>";
                }
                else
                {
                    s += "<span class='pager_button' page='" + iPageNum + "'>" + iPageNum + "</span>&nbsp;";
                }
            }

            s += " <span class='pager_button' page='" + iPages + "'>>></span>";

            s += "<span class='pager_button_total'>&nbsp;&nbsp; " + iTotalRows.ToString() + " records</span>";

            return s;

        }
        public object GetQuerystringValue(string sKey, System.Type Type)
        {
            //Check if it exists, if not return -1 for an int or "" for a string.
            //if it does exist:
            //for integer, return the number  - if it can't be cast as an int return -1
            //for string, return the string.
            if (!string.IsNullOrEmpty(HttpContext.Current.Request.QueryString[sKey]))
            {
                string sValue = HttpContext.Current.Request.QueryString[sKey];
                if (object.ReferenceEquals(Type, typeof(int)))
                {
                    int result;
                    if (int.TryParse(sValue, out result))
                    {
                        return result;
                    }
                    else
                    {
                        return -1;
                    }
                }
                else
                {
                    return sValue;
                }
            }
            else
            {
                if (object.ReferenceEquals(Type, typeof(int)))
                {
                    return -1;
                }
                else
                {
                    return "";
                }
            }
        }
        public string RemoveNamespacesFromXML(string sXML)
        {
			if (!string.IsNullOrEmpty(sXML)) 
			{
	            Regex r = new Regex(" xmlns=\"(.)*\"");
	            Match match = r.Match(sXML);
	
	            while (match.Success == true)
	            {
	                sXML = sXML.Replace(match.ToString(), "");
	                match = match.NextMatch();
	            }
			}
            return sXML;
        }
        public string QuoteUp(string sString)
        {
            ArrayList a = new ArrayList();
            a.AddRange(sString.Split(','));

            StringBuilder sb = new StringBuilder();

            foreach (string s in a)
            {
                sb.Append("'" + s.ToString() + "',");
            }

            sb.Remove(sb.Length - 1, 1);

            return sb.ToString();
        }
        public Dictionary<string, string> GetUsersSort(string sScreen)
        {
			//this should eventually be replaced with whatever is necessary to support a
			//new feature rich ajax grid, like DataTAbles.net or another
			
			//no warnings or failures along the way, just don't return anything if there are errors.
            Dictionary<string, string> d = new Dictionary<string, string>();
			
			XDocument xDoc = (XDocument)GetSessionObject("user_settings", "Security");
			if (xDoc == null) return null;
			
			XElement xSortSettings = xDoc.Descendants("sort").Where(x => (string)x.Attribute("screen") == sScreen).LastOrDefault();
			if (xSortSettings != null)
			{
				if (xSortSettings.Attribute("sort_column") != null)
					d.Add("sort_column", xSortSettings.Attribute("sort_column").Value.ToString());
				if (xSortSettings.Attribute("sort_direction") != null)
					d.Add("sort_direction",xSortSettings.Attribute("sort_direction").Value.ToString());
			}
	
			return d;	
		}
        public Dictionary<string, string> GetUsersTaskDebug(string sTaskID)
        {
			//this should eventually be replaced with whatever is necessary to support a
			//new feature rich ajax grid, like DataTAbles.net or another
			
			//no warnings or failures along the way, just don't return anything if there are errors.
            Dictionary<string, string> d = new Dictionary<string, string>();
			
			XDocument xDoc = (XDocument)GetSessionObject("user_settings", "Security");
			if (xDoc == null) return null;
			
			XElement xTask = xDoc.Descendants("task").Where(
                x => (string)x.Attribute("task_id") == sTaskID).LastOrDefault();
            if (xTask != null)
            {
                //test asset?
                if (xTask.Attribute("asset_id") != null)
                {
                    string sDebugAssetID = xTask.Attribute("asset_id").Value.ToString();

                    if (IsGUID(sDebugAssetID))
                    {
                        string sErr = "";
						string sDebugAssetName = "";
                        string sSQL = "select asset_name from asset where asset_id = '" + sDebugAssetID + "'";
                        if (!dc.sqlGetSingleString(ref sDebugAssetName, sSQL, ref sErr))
                        {
                        }
						else {
							d.Add("asset_id", sDebugAssetID); //txtTestAsset.Text = sDebugAssetName;
							d.Add("asset_name", sDebugAssetName); //txtTestAsset.Attributes["asset_id"] = sDebugAssetID;
						}
					}
                }
            }
	
			return d;	
		}
		
		public void SaveUsersSort(string sScreen, string sColumn, string sSortDirection, ref string sErr)
        {
			//if we can't save the sort settings... so what.
            // takes the screen name ie. users
            // column  ie.  full_name
            // and sort direction asc or des
			XDocument xDoc = (XDocument)GetSessionObject("user_settings", "Security");
            if (xDoc == null) return;

            //we have to analyze the doc and see if the appropriate section exists.
            //if not, we need to construct it
            if (xDoc.Element("settings").Descendants("sorting").Count() == 0)
            {
                xDoc.Element("settings").Add(new XElement("sorting"));
            }

            if (xDoc.Element("settings").Element("sorting").Descendants("sort").Count() == 0)
            {
                xDoc.Element("settings").Element("sorting").Add(new XElement("sort"));
            }

            XElement xSorts = xDoc.Element("settings").Element("sorting").Element("sort");

            xSorts.Descendants("sort").Where(p => p.Attribute("screen").Value == sScreen).Remove();

            //add it
            XElement xSort = new XElement("sort");
            xSort.Add(new XAttribute("screen", sScreen));
            xSort.Add(new XAttribute("sort_column", sColumn));
            xSort.Add(new XAttribute("sort_direction", sSortDirection));
            xSorts.Add(xSort);
			
			//put it back in the session
			SetSessionObject("user_settings", xDoc, "Security");			
			
			return;
        }
        #endregion
        #region "Cloud Functions"
        public bool SetActiveCloudAccount(string sAccountID, ref string sErr)
        {
            if (sAccountID.Length == 36)
            {
                string sSQL = "select account_id, provider, account_name," +
                    " concat(account_name, ' (', provider, ')') as account_label, " +
                    " login_id, login_password, is_default" +
                    " from cloud_account" +
                    " where account_id = '" + sAccountID + "'";

                DataRow drCloudAccounts = null;

                if (dc.sqlGetDataRow(ref drCloudAccounts, sSQL, ref sErr))
                {
                    if (drCloudAccounts != null)
                    {
						//put the default Account in the session as the 'selected' Account.
						CloudAccount ca = new CloudAccount(drCloudAccounts["account_id"].ToString());
						if (ca != null)
						{
							SetSessionObject("selected_cloud_account", ca, "Security");
						}
                    }
                    else
                    {
                        sErr = "Unable to set selected Cloud Account.  Data not found.";
                        return false;
                    }

                    return true;
                }
                else
                {
                    return false;
                }
            }
            else
            {
                sErr = "Unable to set selected Cloud Account.  Invalid Account ID [" + sAccountID + "].";
                return false;
            }


        }
        public bool PutCloudAccountsInSession(ref string sErr)
        {
            string sSQL = "select account_id, provider, account_name," +
                " concat(account_name, ' (', provider, ')') as account_label, " +
                " login_id, login_password, is_default" +
                " from cloud_account" +
                " order by is_default desc";

            DataTable dtCloudAccounts = new DataTable();
            if (!dc.sqlGetDataTable(ref dtCloudAccounts, sSQL, ref sErr))
            {
                return false;
            }
            else
            {
                SetSessionObject("cloud_accounts_dt", dtCloudAccounts, "Security");

                if ((dtCloudAccounts.Rows.Count > 0))
                {
					//the first row is the default
					//put the default Account in the session as the 'selected' Account.
					CloudAccount ca = new CloudAccount(dtCloudAccounts.Rows[0]["account_id"].ToString());
					if (ca != null)
					{
						SetSessionObject("selected_cloud_account", ca, "Security");
					}
				}
                else
                {
                    //have to set it as empty ... this isn't important enough to cause a session drop.
                    SetSessionObject("selected_cloud_account", null, "Security");
                }

                return true;
            }

        }

        public string GetSelectedCloudAccountID()
        {
            CloudAccount ca = (CloudAccount) GetSessionObject("selected_cloud_account", "Security");
            if (ca != null)
				return ca.ID;
			else
				return "";
        }
        public Provider GetSelectedCloudProvider()
        {
            CloudAccount ca = (CloudAccount) GetSessionObject("selected_cloud_account", "Security");
            if (ca != null)
				return ca.Provider;
			else
				return null;
        }
		//this one returns the entire Cloud Providers class... all data
        public CloudProviders GetCloudProviders()
        {
            return (CloudProviders) GetSessionObject("cloud_providers", "Security");
		}
		//this one shoves the Cloud Providers xml into the session
        public void SetCloudProviders(ref string sErr)
        {
			//load the cloud_providers.xml file into the session.  If it doesn't exist, we can't proceed.
			try 
			{
				XDocument xProviders = XDocument.Load(HttpContext.Current.Server.MapPath("~/conf/cloud_providers.xml"));
				
				if (xProviders == null)
				{
					sErr = "Error: Cloud Providers XML file is missing or unreadable.";
				}
				else 
				{
					CloudProviders cp = new CloudProviders(xProviders);
					SetSessionObject("cloud_providers", cp, "Security");
				}
			} catch (Exception ex) {
				sErr = "Error: Unable to load Cloud Providers XML." + ex.Message;
			}
		}
		//this one takes a modified Cloud Providers class and puts it into the session
        public void UpdateCloudProviders(CloudProviders cp)
        {
            SetSessionObject("cloud_providers", cp, "Security");
		}
		
//        public string GetCloudObjectTypes()
//        {
//            object o = GetSessionObject("cloud_object_types", "Cloud");
//            if (o == null)
//                o = Convert.ToString("");
//            return o.ToString();
//        }
        public CloudObjectType GetCloudObjectType(Provider p, string sObjectType)
        {
	        if (p == null)
                RaiseError(Page, "Unable to get Cloud Provider.", false, "");

			CloudObjectType cot = p.GetObjectTypeByName(sObjectType);
            if (cot != null)
                return cot;
			
            return null;
        }


        #endregion
        #region "Logging Functions"
        //also, we need to start standardizing the way we write 'security logs'.
        //this helps do that.
        public void WriteObjectChangeLog(acObjectTypes oType, string sObjectID, string sLabel, string sFrom, string sTo)
        {
            string sErr = "";
            if (!string.IsNullOrEmpty(sFrom) && !string.IsNullOrEmpty(sTo))
            {
                if (sFrom != sTo)
                {
                    dc.addSecurityLog(GetSessionUserID(), SecurityLogTypes.Object, SecurityLogActions.ObjectModify, oType, sObjectID, "Changed: " + sLabel + " from [" + sFrom.Replace("'", "''") + "] to [" + sTo.Replace("'", "''") + "].", ref sErr);
                }
            }
        }
        public void WriteObjectChangeLog(acObjectTypes oType, string sObjectID, string sObjectName, string sLog)
        {
            string sErr = "";
            if (!string.IsNullOrEmpty(sObjectID) && !string.IsNullOrEmpty(sObjectName))
            {
                string sMsg = "";
                if (string.IsNullOrEmpty(sObjectName))
                {
                    sMsg = "[" + sLog + "]";
                }
                else
                {
                    sMsg = "Changed: [" + sObjectName.Replace("'", "''") + "] - [" + sLog + "]";
                }
                dc.addSecurityLog(GetSessionUserID(), SecurityLogTypes.Object, SecurityLogActions.ObjectModify, oType, sObjectID, sMsg, ref sErr);
            }
        }
        public void WriteObjectAddLog(acObjectTypes oType, string sObjectID, string sObjectName, string sLog = "")
        {
            string sErr = "";
            if (!string.IsNullOrEmpty(sObjectID) && !string.IsNullOrEmpty(sObjectName))
            {
                if (string.IsNullOrEmpty(sLog))
                {
                    sLog = "Created: [" + sObjectName.Replace("'", "''") + "].";
                }
                else
                {
                    sLog = "Created: [" + sObjectName.Replace("'", "''") + "] - [" + sLog + "]";
                }
                dc.addSecurityLog(GetSessionUserID(), SecurityLogTypes.Object, SecurityLogActions.ObjectAdd, oType, sObjectID, sLog, ref sErr);
            }
        }
        public void WriteObjectDeleteLog(acObjectTypes oType, string sObjectID, string sObjectName, string sLog = "")
        {
            string sErr = "";
            if (!string.IsNullOrEmpty(sObjectID) && !string.IsNullOrEmpty(sObjectName))
            {
                if (string.IsNullOrEmpty(sLog))
                {
                    sLog = "Deleted: [" + sObjectName.Replace("'", "''") + "].";
                }
                else
                {
                    sLog = "Deleted: [" + sObjectName.Replace("'", "''") + "] - [" + sLog + "]";
                }
                dc.addSecurityLog(GetSessionUserID(), SecurityLogTypes.Object, SecurityLogActions.ObjectDelete, oType, sObjectID, sLog, ref sErr);
            }
        }
        #endregion

    }
}
