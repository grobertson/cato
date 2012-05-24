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
using System.ComponentModel;
using System.Data;
using System.Linq;
using System.Xml.Linq;
using System.Xml.XPath;
using System.Text;
using System.Text.RegularExpressions;

namespace Globals
{
	//a new class for handling api responses consistently.
	public class apiResponse
	{
		public string Method = "";
		public string Response = "";
		public string ErrorCode = "";
		public string ErrorMessage = "";
		public string ErrorDetail = "";
		
		//default constructor
		public apiResponse()
		{
		}
		
		//constructor for a method
		public apiResponse(string sMethod)
		{
			Method = sMethod;
		}
		
		//default constructor
		public apiResponse(string sMethod, string sResponse, string sErrorCode, string sErrorMessage, string sErrorDetail)
		{
			Method = sMethod;
			Response = sResponse;
			ErrorCode = sErrorCode;
			ErrorMessage = sErrorMessage;
			ErrorDetail = sErrorDetail;
		}

		public string AsXML()
		{
            acUI.acUI ui = new acUI.acUI();

			//well, for XML we have to do a little cleanup
			//it's entirely possible there may be some invalid stuff in the Message or Detail
			//so, let's just use some patterns to remove the most common offenders, like an xml declaration.
			Regex rx = new Regex("<\\?xml.*\\?>");
			this.ErrorMessage = rx.Replace(this.ErrorMessage, "");
			this.ErrorDetail = rx.Replace(this.ErrorDetail, "");
			//there may be more later.
			
			// validate the response and error detail as valid XML
			// OR
			// escape any offending characters.
			if (!string.IsNullOrEmpty(this.Response))
			{
				try {
					XDocument x = null;
					x = XDocument.Parse(this.Response);
					if (x == null)
						this.Response = ui.SafeHTML(this.Response);			
				} catch (Exception) {
					this.Response = ui.SafeHTML(this.Response);
				}
			}

			if (!string.IsNullOrEmpty(this.ErrorDetail))
			{
				try {
					XDocument x = null;
					x = XDocument.Parse(this.ErrorDetail);
					if (x == null)
						this.ErrorDetail = ui.SafeHTML(this.ErrorDetail);			
				} catch (Exception) {
					this.ErrorDetail = ui.SafeHTML(this.ErrorDetail);
				}
			}

			
			StringBuilder sb = new StringBuilder();
			
			sb.Append("<apiResponse>");
			sb.AppendFormat("<method>{0}</method>", this.Method);
			sb.AppendFormat("<response>{0}</response>", this.Response);
			
			if (!string.IsNullOrEmpty(this.ErrorCode))
			{
				sb.Append("<error>");
				sb.AppendFormat("<code>{0}</code>", this.ErrorCode);
				sb.AppendFormat("<message>{0}</message>", this.ErrorMessage);
				sb.AppendFormat("<detail>{0}</detail>", this.ErrorDetail);
				sb.Append("</error>");
			}
			sb.Append("</apiResponse>");
			
			return sb.ToString();

		}
	

		//there are some standard responses... so rather than have code everywhere, we'll have class methods for the common ones.
	
		//API authentication failure
		public void CommonResponse(string sErrorCode)
		{
			switch (sErrorCode) {
			case "1004":
				this.ErrorCode = "1004";
				this.ErrorMessage = "Authentication Failure";
				break;
			default:
				break;
			}
			
			return;
		}
	}
	#region "Enums"
    public enum acObjectTypes : int
    {
        None = 0,
        User = 1,
        Asset = 2,
        Task = 3,
        Schedule = 4,
        Procedure = 5,
        Registry = 6,
        DashLayout = 10,
        DashWidget = 11,
        FileReader = 14,
        MessageTemplate = 18,
        Parameter = 34,
        Credential = 35,
        Domain = 36,
        CloudAccount = 40,
		Cloud = 41,
		Ecosystem = 50,
        EcoTemplate = 51
    }
    public enum FieldValidatorTypes : int
    {
        [Description("Restricts entry to any numeric value, positive or negative, with or without a decimal.")]
        Number = 0,
        [Description("Restricts entry to a positive number.")]
        PositiveNumber = 1,
        [Description("Limits entry to upper and lowercase letters, numbers, dot, underscore and @.")]
        UserName = 2,
        [Description("Restricts entry to a strict identifier style.  Uppercase letters, numbers and underscore only.")]
        TaskName = 3
    }
    public enum SecurityLogTypes
    {
        Object = 0,
        Security = 1,
        Usage = 2,
        Other = 3
    }
    public enum SecurityLogActions
    {
        UserLogin = 0,
        UserLogout = 1,
        UserLoginAttempt = 2,
        UserPasswordChange = 3,
        UserSessionDrop = 4,
        SystemLicenseException = 5,

        ObjectAdd = 100,
        ObjectModify = 101,
        ObjectDelete = 102,
        ObjectView = 103,
        ObjectCopy = 104,

        PageView = 800,
        ReportView = 801,

        APIInterface = 700,

        Other = 900,
        ConfigChange = 901
    }
	#endregion    

	//this CurrentUser class will be used when we are ready to stop using Session
    public class CurrentUser
    {
        private static string sUserID = "";
        public static string UserID
        {
            get { return sUserID; }
            set { sUserID = value; }
        }
	}
	
	#region "Database Settings"
	public class DatabaseSettings
    {

        private static int iConnectionTimeout = 15;
        public static int ConnectionTimeout
        {
            get { return iConnectionTimeout; }
            set { iConnectionTimeout = value; }
        }

		private static int iConnectionRetries = 15;
        public static int ConnectionRetries
        {
            get { return iConnectionRetries; }
            set { iConnectionRetries = value; }
        }

        private static string sAppInstance = "";
        public static string AppInstance
        {
            get { return sAppInstance; }
            set { sAppInstance = value; }
        }

        private static string sDatabaseName = "";
        public static string DatabaseName
        {
            get { return sDatabaseName; }
            set { sDatabaseName = value; }
        }

        private static string sServerAddress = "";
        public static string DatabaseAddress
        {
            get { return sServerAddress; }
            set { sServerAddress = value; }
        }

        private static string sServerPort = "";
        public static string DatabasePort
        {
            get { return sServerPort; }
            set { sServerPort = value; }
        }

        private static string sServerUserName = "";
        public static string DatabaseUID
        {
            get { return sServerUserName; }
            set { sServerUserName = value; }
        }

        private static string sServerUserPassword = "";
        public static string DatabaseUserPassword
        {
            get { return sServerUserPassword; }
            set { sServerUserPassword = value; }
        }

        private static string sEnvironmentKey = "";
        public static string EnvironmentKey
        {
            get { return sEnvironmentKey; }
            set { sEnvironmentKey = value; }
        }

        private static string sServerUseSSL = "";
        public static string UseSSL
        {
            get { return sServerUseSSL; }
            set { sServerUseSSL = value; }
        }

		private static bool bSqlLog = false;
        public static bool SqlLog
        {
            get { return bSqlLog; }
            set { bSqlLog = value; }
        }

		private static bool bDbLog = false;
        public static bool DbLog
        {
            get { return bDbLog; }
            set { bDbLog = value; }
        }
    }
	#endregion    

	#region "Global Settings"
	public class GlobalSettings
    {
        private static int iTempDirDays = 30;
        public static int UITempDirDays
        {
            get { return iTempDirDays; }
            set { iTempDirDays = value; }
        }
        private static string sStormApiURL = "";
        public static string StormApiURL
        {
            get { return sStormApiURL; }
            set { sStormApiURL = value; }
        }
        private static string sStormApiPort = "";
        public static string StormApiPort
        {
            get { return sStormApiPort; }
            set { sStormApiPort = value; }
        }
    }
	#endregion    

	#region "Ecosystems"
	//Ecosystems contains a DataTable
	//more efficient to read from the DB as a DataTable than to loop and create a dictionary.
	//if you want a dictionary, that's an instance method.
	public class Ecosystems
	{
		public DataTable DataTable = new DataTable();
		
		public Ecosystems(string sFilter, string sAccountID, ref string sErr)
		{
			try
			{
				//buids a list of ecosystems from the db, with the optional filter
				dataAccess dc = new dataAccess();
	            string sWhereString = "";
	
	            if (!string.IsNullOrEmpty(sFilter))
	            {
	                //split on spaces
	                int i = 0;
	                string[] aSearchTerms = sFilter.Split(' ');
	                for (i = 0; i <= aSearchTerms.Length - 1; i++)
	                {
	                    if (aSearchTerms[i].Length > 0)
	                    {
	                        sWhereString = " and (e.ecosystem_name like '%" + aSearchTerms[i] +
	                           "%' or e.ecosystem_desc like '%" + aSearchTerms[i] + "%' or et.ecotemplate_name like '%" + aSearchTerms[i] + "%' ) ";
	                    }
	                } 
	            }
	
	            string sSQL = "select e.ecosystem_id, e.ecosystem_name, e.ecosystem_desc, e.account_id, et.ecotemplate_name, created_dt, last_update_dt," +
					" (select count(*) from ecosystem_object where ecosystem_id = e.ecosystem_id) as num_objects" +
					" from ecosystem e" +
					" join ecotemplate et on e.ecotemplate_id = et.ecotemplate_id" +
					" where e.account_id = '" + sAccountID + "'" +
					sWhereString +
					" order by e.ecosystem_name";
	
	            if (!dc.sqlGetDataTable(ref this.DataTable, sSQL, ref sErr))
	                return;
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
		public Dictionary<string, Ecosystem> AsDictionary()
		{
			try
			{
				//spin "this" and turn it into a dictionary
				Dictionary<string, Ecosystem> dict = new Dictionary<string, Ecosystem>();
				
				foreach (DataRow dr in this.DataTable.Rows)
				{
					Ecosystem e = new Ecosystem();
					e.ID = dr["ecosystem_id"].ToString();
					
					dict.Add(e.ID, e);				
				}
				
				return dict;
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
	}
	public class Ecosystem 
	{
		acUI.acUI ui = new acUI.acUI();
		
		public string ID;
		public string Name;
		public string Description;
		public string StormFile;
		public string AccountID;
		public string EcotemplateID;
		public string EcotemplateName; //no referenced objects just yet, just the name and ID until we need more.
		public string ParameterXML;
		public string CloudID;
		public string StormStatus;
		public Nullable<DateTime> CreatedDate;
		public Nullable<DateTime> LastUpdate;
		public int NumObjects = 0;
		
		//an empty constructor
		public Ecosystem()
		{
			this.ID = ui.NewGUID();
		}
		
		//aname and desc
		public Ecosystem(string sName, string sDescription, string sEcotemplateID, string sAccountID)
		{
			this.ID = ui.NewGUID();
			this.Name = sName;
			this.Description = sDescription;
			this.EcotemplateID = sEcotemplateID;
			this.AccountID = sAccountID;
			this.CreatedDate = DateTime.Now;
		}
		
		//the default constructor, given an ID loads it up.
		public Ecosystem(string sEcosystemID)
		{
			try
			{
				if (string.IsNullOrEmpty(sEcosystemID))
					throw new Exception("Error building Ecosystem object: ID is required.");	
				
	            dataAccess dc = new dataAccess();
				
				string sErr = "";
	                string sSQL = "select e.ecosystem_id, e.ecosystem_name, e.ecosystem_desc, e.storm_file, e.storm_status," +
	                    " e.account_id, e.ecotemplate_id, et.ecotemplate_name, e.created_dt, e.last_update_dt," +
						" (select count(*) from ecosystem_object where ecosystem_id = e.ecosystem_id) as num_objects" +
	                    " from ecosystem e" +
	                    " join ecotemplate et on e.ecotemplate_id = et.ecotemplate_id" +
	                    " where e.ecosystem_id = '" + sEcosystemID + "'";
	
	            DataRow dr = null;
	            if (dc.sqlGetDataRow(ref dr, sSQL, ref sErr))
	            {
	                if (dr != null)
	                {
						this.ID = dr["ecosystem_id"].ToString();;
						this.Name = dr["ecosystem_name"].ToString();
						this.AccountID = dr["account_id"].ToString();
						this.EcotemplateID = dr["ecotemplate_id"].ToString();
						this.EcotemplateName = dr["ecotemplate_name"].ToString();
						this.Description = (object.ReferenceEquals(dr["ecosystem_desc"], DBNull.Value) ? "" : dr["ecosystem_desc"].ToString());
						this.StormFile = (object.ReferenceEquals(dr["storm_file"], DBNull.Value) ? "" : dr["storm_file"].ToString());
						this.StormStatus = (object.ReferenceEquals(dr["storm_status"], DBNull.Value) ? "" : dr["storm_status"].ToString());
						if (!object.ReferenceEquals(dr["created_dt"], DBNull.Value)) this.CreatedDate = Convert.ToDateTime(dr["created_dt"].ToString());
						if (!object.ReferenceEquals(dr["last_update_dt"], DBNull.Value)) this.LastUpdate = Convert.ToDateTime(dr["last_update_dt"].ToString());
						this.NumObjects = Convert.ToInt16(dr["num_objects"].ToString());
					}
				}
				else 
				{
					throw new Exception("Error building Ecosystem object: " + sErr);	
				}
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
		
		//saves this Ecosystem to the database
		public bool DBUpdate(ref string sErr)
		{
			try
			{
				dataAccess dc = new dataAccess();
				
				if (string.IsNullOrEmpty(this.Name) || string.IsNullOrEmpty(this.EcotemplateID) || string.IsNullOrEmpty(this.AccountID)) 
				{
					sErr = "Name, EcotemplateID and Account ID are required Ecosystem properties.";
					return false;
				}
				
				string sSQL = "update ecosystem set" + 
					" ecosystem_name = '" + this.Name + "'," +
					" ecotemplate_id = '" + this.EcotemplateID + "'," +
					" account_id = '" + this.AccountID + "'," +
					" ecosystem_desc = " + (string.IsNullOrEmpty(this.Description) ? " null" : " '" + ui.TickSlash(this.Description) + "'") + "," +
					" last_update_dt = now()," +
					" storm_file = " + (string.IsNullOrEmpty(this.StormFile) ? " null" : " '" + ui.TickSlash(this.StormFile) + "'") +
					" where ecosystem_id = '" + this.ID + "'";
				
				if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
					throw new Exception(sErr);
	
				return true;
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}

		//saves this Ecosystem as a new one in the db
		public bool DBCreateNew(ref string sErr)
		{
			try
			{
	            dataAccess dc = new dataAccess();
				string sSQL = "";
				
				if (string.IsNullOrEmpty(this.Name) || string.IsNullOrEmpty(this.ID)) 
				{
					sErr = "ID and Name are required Ecosystem properties.";
					return false;
				}
				
                sSQL = "insert into ecosystem (ecosystem_id, ecosystem_name, ecosystem_desc, account_id, ecotemplate_id," +
					" storm_file, storm_status, storm_parameter_xml, storm_cloud_id, created_dt, last_update_dt)" +
                    " select '" + this.ID + "'," +
                    " '" + this.Name + "'," +
                    (string.IsNullOrEmpty(this.Description) ? " null" : " '" + ui.TickSlash(this.Description) + "'") + "," +
                    " '" + AccountID + "'," +
                    " ecotemplate_id," +
                    " storm_file," +
                    (string.IsNullOrEmpty(this.StormStatus) ? " null" : " '" + ui.TickSlash(this.StormStatus) + "'") + "," +
                    (string.IsNullOrEmpty(this.ParameterXML) ? " null" : " '" + ui.TickSlash(this.ParameterXML) + "'") + "," +
                    (string.IsNullOrEmpty(this.CloudID) ? " null" : " '" + this.CloudID + "'") + "," +
					" now(), now()" +
                    " from ecotemplate where ecotemplate_id = '" + this.EcotemplateID + "'";
				
				if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
				{
					if (sErr == "key_violation")
					{
						sErr = "An Ecosystem with that name already exists.  Please select another name.";
						return false;
					}
					else 
						throw new Exception(sErr);
				}
				
				ui.WriteObjectAddLog(acObjectTypes.Ecosystem, this.ID, this.Name, "Ecosystem created.");
				
				//yay!
				return true;
			}
			catch (Exception ex)
			{
				throw new Exception(ex.Message);
			}		
		}
	}
	#endregion
	
	#region "Ecotemplates"
	//Ecotemplates contains a DataTable
	//more efficient to read from the DB as a DataTable than to loop and create a dictionary.
	//if you want a dictionary, that's an instance method.
	public class Ecotemplates
	{
		public DataTable DataTable = new DataTable();
		
		public Ecotemplates(string sFilter, ref string sErr)
		{
			try
			{
				//builds a list of ecotemplates from the db, with the optional filter
				dataAccess dc = new dataAccess();
	            string sWhereString = "";
	
	            if (!string.IsNullOrEmpty(sFilter))
	            {
	                //split on spaces
	                int i = 0;
	                string[] aSearchTerms = sFilter.Split(' ');
	                for (i = 0; i <= aSearchTerms.Length - 1; i++)
	                {
	                    if (aSearchTerms[i].Length > 0)
	                    {
	                        sWhereString = " and (a.ecotemplate_name like '%" + aSearchTerms[i] +
	                           "%' or a.ecotemplate_desc like '%" + aSearchTerms[i] + "%' ) ";
	                    }
	                } 
	            }
	
	            string sSQL = "select a.ecotemplate_id, a.ecotemplate_name, a.ecotemplate_desc" +
	                   " from ecotemplate a" +
	                   " where 1=1" +
	                   sWhereString +
	                   " order by ecotemplate_name";
	
	            if (!dc.sqlGetDataTable(ref this.DataTable, sSQL, ref sErr))
	                return;
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
		public Dictionary<string, Ecotemplate> AsDictionary()
		{
			try
			{
				//spin "this" and turn it into a dictionary
				Dictionary<string, Ecotemplate> dict = new Dictionary<string, Ecotemplate>();
				
				//this will be slow as it does a select for each one.
				//also, not currently being used
				foreach (DataRow dr in this.DataTable.Rows)
				{
					Ecotemplate et = new Ecotemplate(dr["ecotemplate_id"].ToString());
					dict.Add(et.ID, et);
				}
				
				return dict;
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
	}
	public class Ecotemplate 
	{
		acUI.acUI ui = new acUI.acUI();
		
		public string ID;
		public string Name;
		public string Description;
		public string StormFileType;
		public string StormFile;
		public bool IncludeTasks = false; //used for export to xml
		public bool DBExists;
		public string OnConflict = "cancel";  //the default behavior for all conflicts is to cancel the operation
		public Dictionary<string, EcotemplateAction> Actions = new Dictionary<string, EcotemplateAction>();
		
		//an empty constructor
		public Ecotemplate()
		{
			this.ID = ui.NewGUID();
		}
		
		//a name and desc
		public Ecotemplate(string sName, string sDescription)
		{
			this.ID = ui.NewGUID();
			this.Name = sName;
			this.Description = sDescription;
			this.DBExists = _DBExists();
		}
		
		//the default constructor, given an ID loads it up.
		public Ecotemplate(string sEcotemplateID)
		{
			try
			{
					if (string.IsNullOrEmpty(sEcotemplateID))
					throw new Exception("Error building Ecotemplate object: ID is required.");	
				
	            dataAccess dc = new dataAccess();
				
				string sErr = "";
	            string sSQL = "select ecotemplate_id, ecotemplate_name, ecotemplate_desc, storm_file_type, storm_file" +
	                " from ecotemplate" +
	                " where ecotemplate_id = '" + sEcotemplateID + "'";
	
	            DataRow dr = null;
	            if (dc.sqlGetDataRow(ref dr, sSQL, ref sErr))
	            {
	                if (dr != null)
	                {
						this.DBExists = true;
						this.ID = dr["ecotemplate_id"].ToString();;
						this.Name = dr["ecotemplate_name"].ToString();
						this.Description = (object.ReferenceEquals(dr["ecotemplate_desc"], DBNull.Value) ? "" : dr["ecotemplate_desc"].ToString());
						this.StormFileType = (object.ReferenceEquals(dr["storm_file_type"], DBNull.Value) ? "" : dr["storm_file_type"].ToString());
						this.StormFile = (object.ReferenceEquals(dr["storm_file"], DBNull.Value) ? "" : dr["storm_file"].ToString());
						
						//get a table of actions and loop the rows
						sSQL = "select action_id, ecotemplate_id, action_name, action_desc, category, original_task_id, task_version, parameter_defaults, action_icon" +
							" from ecotemplate_action" +
							" where ecotemplate_id = '" + sEcotemplateID + "'";
	
						DataTable dtActions = new DataTable();
						if (dc.sqlGetDataTable(ref dtActions, sSQL, ref sErr))
						{
							if (dtActions.Rows.Count > 0)
							{
								foreach(DataRow drAction in dtActions.Rows)
								{
									EcotemplateAction ea = new EcotemplateAction(drAction, this);
									if (ea != null)
										this.Actions.Add(drAction["action_id"].ToString(), ea);
								}
							}
						}
					}
				}
				else 
				{
					throw new Exception("Error building Ecotemplate object: " + sErr);	
				}
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
		
		//from an XML document
		public Ecotemplate FromXML(string sEcotemplateXML, ref string sErr)
		{
			try {
				XDocument xEcotemplate = XDocument.Parse(sEcotemplateXML);
				if (xEcotemplate != null)
				{
					XElement xe = xEcotemplate.Element("ecotemplate");
					
					//some of these properties will not be required coming from the XML.
					
					//if there's no ID we create one
					this.ID = (xe.Attribute("id") != null ? xe.Attribute("id").Value.ToLower() : Guid.NewGuid().ToString().ToLower());
					this.Name = xe.Attribute("name").Value;
					this.Description = xe.Element("description").Value;
					
					this.DBExists = _DBExists();
	
					if (xe.Element("storm_file") != null)
					{
						XElement xeSF = xe.Element("storm_file");
						this.StormFile = xeSF.Value;
						this.StormFileType = (xeSF.Attribute("storm_file_type") != null ? xeSF.Attribute("storm_file_type").Value : ""); //cancel is the default
					}	
					
					//if there are conflicts when we try to save, what do we do?
					this.OnConflict = (xe.Attribute("on_conflict") != null ? xe.Attribute("on_conflict").Value : "cancel"); //cancel is the default
	
					//actions
					foreach (XElement xAction in xe.XPathSelectElements("//actions/action")) {
						EcotemplateAction ea = new EcotemplateAction(xAction, this, ref sErr);
						
						if (ea != null)
						{
							//if the xml contains a complete Task, we have to deal with it
							//otherwise just set the OriginalTaskID and TaskVersion properties.
	
							this.Actions.Add(ea.ID, ea);
						}
					}
					
					return this;
				}
				
				return null;
				
			} catch (Exception ex) {
				sErr = "Ecotemplate.FromXML: " + ex.Message;
				return null;
			}
		}

		private bool _DBExists()
		{	
			try
			{
	
				dataAccess dc = new dataAccess();
				string sErr = "";
				
				//task_id is the PK, and task_name+version is a unique index.
				//so, we check the conflict property, and act accordingly
				string sSQL = "select ecotemplate_id from ecotemplate" +
					" where ecotemplate_name = '" + this.Name + "'" +
					" or ecotemplate_id = '" + this.ID + "'";
				
				DataRow dr = null;
				if (!dc.sqlGetDataRow(ref dr, sSQL, ref sErr))
				{
					throw new Exception("Ecotemplate Object: Unable to check for existing Name or ID. " + sErr);
				}
				
				if (dr != null)
				{
					if (!string.IsNullOrEmpty(dr["ecotemplate_id"].ToString())) {
						//PAY ATTENTION! 
						//if the template exists... it might have been by name, so...
						//we're setting the ids to the same as the database so it's more accurate.
						
						this.ID = dr["ecotemplate_id"].ToString();
						return true;
					}
				}
					
				return false;
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}

		//makes a copy of this template in the database
		public bool DBCopy(string sNewName, ref string sErr)
		{
			try
			{
					Ecotemplate et = new Ecotemplate();
				if (et != null)
				{
					//populate it
					et.ID = Guid.NewGuid().ToString().ToLower();
					et.Name = sNewName;
					et.Description = this.Description;
					et.StormFileType = this.StormFileType;
					et.StormFile = this.StormFile;
					et.Actions = this.Actions;
					
					//we gave it a new name and id, recheck if it exists
					et.DBExists = et._DBExists();
					
					et.DBSave(ref sErr);
					
					if (!string.IsNullOrEmpty(sErr))
						return false;
				
					return true;
				}
				
				return false;
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}

		//saves this template to the database
		//DOES NOT include Actions
		public bool DBUpdate(ref string sErr)
		{
			try
			{	
				dataAccess dc = new dataAccess();
				
				if (string.IsNullOrEmpty(this.Name) || string.IsNullOrEmpty(this.ID)) 
				{
					sErr = "ID and Name are required Ecotemplate properties.";
					return false;
				}
				
				string sSQL = "update ecotemplate" + 
					" set ecotemplate_name = '" + ui.TickSlash(this.Name) + "'," +
					" ecotemplate_desc = " + (string.IsNullOrEmpty(this.Description) ? " null" : " '" + ui.TickSlash(this.Description) + "'") + "," +
					" storm_file_type = " + (string.IsNullOrEmpty(this.StormFileType) ? " null" : " '" + this.StormFileType + "'") + "," +
					" storm_file = " + (string.IsNullOrEmpty(this.StormFile) ? " null" : " '" + ui.TickSlash(this.StormFile) + "'") +
					" where ecotemplate_id = '" + this.ID + "'";
				
				if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
					throw new Exception(sErr);
	
				return true;
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}

		//saves this template as a new template in the db
		public bool DBSave(ref string sErr)
		{
			try
			{
				if (string.IsNullOrEmpty(this.Name) || string.IsNullOrEmpty(this.ID)) 
				{
					sErr = "ID and Name are required Ecotemplate properties.";
					return false;
				}

				dataAccess.acTransaction oTrans = new dataAccess.acTransaction(ref sErr);
				
				if (this.DBExists)
				{
					//uh oh... this ecotemplate exists.  unless told to do so, we stop here.
					if (this.OnConflict == "cancel") {
						sErr = "Another Ecotemplate with that ID or Name exists.  [" + this.ID + "/" + this.Name + "]  Conflict directive set to 'cancel'. (Default is 'cancel' if omitted.)";
						oTrans.RollBack();
						return false;
					}
					else {
						//ok, what are we supposed to do then?
						switch (this.OnConflict) {
						case "replace":
							//whack it all so we can re-insert
							//but by name or ID?  which was the conflict?
							
							//no worries! the _DBExists function called when we created the object
							//will have resolved any name/id issues.
							
							//if the ID existed it doesn't matter, we'll be plowing it anyway.
							//by "plow" I mean drop and recreate the actions... the ecotemplate row will be UPDATED
							oTrans.Command.CommandText = "update ecotemplate" + 
								" set ecotemplate_name = '" + this.Name + "'," +
								" ecotemplate_desc = " + (string.IsNullOrEmpty(this.Description) ? " null" : " '" + ui.TickSlash(this.Description) + "'") + "," +
								" storm_file_type = " + (string.IsNullOrEmpty(this.StormFileType) ? " null" : " '" + this.StormFileType + "'") + "," +
								" storm_file = " + (string.IsNullOrEmpty(this.StormFile) ? " null" : " '" + ui.TickSlash(this.StormFile) + "'") +
								" where ecotemplate_id = '" + this.ID + "'";
		                    if (!oTrans.ExecUpdate(ref sErr))
		                        throw new Exception(sErr);


							oTrans.Command.CommandText = "delete from ecotemplate_action" +
								" where ecotemplate_id = '" + this.ID + "'";
		                    if (!oTrans.ExecUpdate(ref sErr))
		                        throw new Exception(sErr);
							break;
						default:
							//there is no default action... if the on_conflict didn't match we have a problem... bail.
							sErr = "There is an ID or Name conflict, and the on_conflict directive isn't a valid option. (replace/cancel)";
							return false;
						}
					}
				}
				else 
				{
					//doesn't exist, we'll add it				
					oTrans.Command.CommandText = "insert into ecotemplate (ecotemplate_id, ecotemplate_name, ecotemplate_desc, storm_file_type, storm_file)" +
						" values ('" + this.ID + "'," +
							" '" + this.Name + "'," +
							(string.IsNullOrEmpty(this.Description) ? " null" : " '" + ui.TickSlash(this.Description) + "'") + "," +
							(string.IsNullOrEmpty(this.StormFileType) ? " null" : " '" + this.StormFileType + "'") + "," +
							(string.IsNullOrEmpty(this.StormFile) ? " null" : " '" + ui.TickSlash(this.StormFile) + "'") + 
							")";
					
					if (!oTrans.ExecUpdate(ref sErr))
						return false;
					
					//ui.WriteObjectAddLog(acObjectTypes.Ecosystem, this.ID, this.Name, "Ecotemplate created.");
				}
				
				//create the actions
				//actions aren't referenced by id anywhere, so we'll just give them a new guid
				//to prevent any risk of PK issues.
				foreach (EcotemplateAction ea in this.Actions.Values) {
					oTrans.Command.CommandText = "insert into ecotemplate_action" + 
						" (action_id, ecotemplate_id, action_name, action_desc, category, action_icon, original_task_id, task_version, parameter_defaults)" +
						" values (" +
						" uuid()," + 
						" '" + this.ID + "'," + 
						" '" + ui.TickSlash(ea.Name) + "'," + 
						(string.IsNullOrEmpty(ea.Description) ? "null" : " '" + ui.TickSlash(ea.Description) + "'") + "," + 
						(string.IsNullOrEmpty(ea.Category) ? "null" : " '" + ui.TickSlash(ea.Category) + "'") + "," + 
						" '" + ea.Icon + "'," + 
						" '" + ea.OriginalTaskID + "'," + 
						(string.IsNullOrEmpty(ea.TaskVersion) ? "null" : " '" + ea.TaskVersion + "'") + "," + 
						(string.IsNullOrEmpty(ea.ParameterDefaultsXML) ? "null" : " '" + ui.TickSlash(ea.ParameterDefaultsXML) + "'") +
						")";
					
					if (!oTrans.ExecUpdate(ref sErr))
						return false;
					
					//now, does this action contain a <task> section?  If so, we'll branch off and do 
					//the create task logic.
					if (ea.Task != null) 
					{
						if (!ea.Task.DBSave(ref sErr, oTrans))
						{
							//the task 'should' have rolled back on any errors, but in case it didn't.
							try {
								oTrans.RollBack();
								return false;
							} catch (Exception) {
							}
						}
						else
						{
							if (!string.IsNullOrEmpty(sErr))
							{
								try {
									oTrans.RollBack();
									return false;
								} catch (Exception) {
								}
							}
									
							//finally, don't forget to update the action with the new values if any
							ea.OriginalTaskID = ea.Task.OriginalTaskID;
							
							//we don't update the version if the action referenced the default (it was empty)
							if  (!string.IsNullOrEmpty(ea.TaskVersion))
								ea.TaskVersion = ea.Task.Version;
						}
					}
				}
				
				//yay!
				oTrans.Commit();
				return true;

			}
			catch (Exception ex)
			{
				throw new Exception(ex.Message);
			}	
		}

		public XElement AsXElement()
		{					
			try
			{
				XElement xe = new XElement("ecotemplate");
					
				//don't think we need id's in this xml - will just create problems with RI down the road.
				//xe.SetAttributeValue("id", this.ID);
				xe.SetAttributeValue("name", this.Name);
				xe.SetAttributeValue("on_conflict", "cancel");
				xe.SetElementValue("description", this.Description);
	
				//storm
				XElement xStorm = new XElement("storm_file");
				xStorm.SetAttributeValue("storm_file_type", this.StormFileType);
				xStorm.SetValue(this.StormFile);
				xe.Add(xStorm);
	
				//actions
				XElement xActions = new XElement("actions");
				foreach (EcotemplateAction ea in this.Actions.Values) {
					ea.IncludeTask = this.IncludeTasks;
					string sActionXML = ea.AsXML();
					if (!string.IsNullOrEmpty(sActionXML))
					{
						XElement xAction = XElement.Parse(sActionXML);
						if (xAction != null) {	
							xActions.Add(xAction);
						}
					}				
				}
				xe.Add(xActions);
				
				return xe;
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
		public string AsXML()
		{
			XElement xe = this.AsXElement();
			if (xe != null)
				return xe.ToString();
			else 
				return null;
		}
	}
	public class EcotemplateAction
	{
		public string ID;
		public string Name;
		public string Description;
		public string Category;
		public string OriginalTaskID;
		public string TaskVersion;
		public string Icon;
		public string ParameterDefaultsXML;
		public Ecotemplate Ecotemplate; //pointer to our parent Template.
		
		//for export, we might want to tell the action to include the whole referenced task object
		//pretty rare, since for general use we don't wanna be lugging around a whole task.
		public bool IncludeTask = false;
		public Task Task;
		
		//static method, given an ID.
		static public EcotemplateAction FromID(string sActionID)
		{
			try 
			{
				if (string.IsNullOrEmpty(sActionID))
					throw new Exception("Error building Ecotemplate Action object: Action ID is required.");	
				
	            dataAccess dc = new dataAccess();
				
				string sErr = "";
	            string sSQL = "select action_id, ecotemplate_id, action_name, action_desc, category, original_task_id, task_version, parameter_defaults, action_icon" +
	                " from ecotemplate_action" +
	                " where action_id = '" + sActionID + "'";
	
	            DataRow dr = null;
	            if (dc.sqlGetDataRow(ref dr, sSQL, ref sErr))
	            {
	                if (dr != null)
	                {
						Ecotemplate et = new Ecotemplate(dr["ecotemplate_id"].ToString());
						if (et != null)
						{
							EcotemplateAction ea = new EcotemplateAction(dr, et);
							if (ea != null)
							{
								return ea;
							}
							else
							{
								sErr = "Unable to build Action object for ID [" + sActionID + "].";
								return null;
							}
						}
						else
						{
							sErr = "Unable to find Template using ID [" + dr["ecotemplate_id"].ToString() + "] for Action ID [" + sActionID + "].";
							return null;
						}
					}
					else
					{
						sErr = "No Action found using ID [" + sActionID + "].";
						return null;
					}
				}
				else 
				{
					throw new Exception("Error building Ecotemplate Action object from ID: " + sErr);	
				}
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
		
		//another constructor, takes a datarow from ecotemplate_action and creates it from that
		public EcotemplateAction(DataRow dr, Ecotemplate parent)
		{
			try
			{
				Ecotemplate = parent;
				
				ID = dr["action_id"].ToString();
				Name = dr["action_name"].ToString();
				Description = dr["action_desc"].ToString();
				Category = dr["category"].ToString();
				OriginalTaskID = dr["original_task_id"].ToString();
				TaskVersion = dr["task_version"].ToString();
				Icon = dr["action_icon"].ToString();
				ParameterDefaultsXML = dr["parameter_defaults"].ToString();
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}

		//build from an XElement, part of the Ecotemplate XDocument
		public EcotemplateAction(XElement xAction, Ecotemplate parent, ref string sErr)
		{
			try
			{
				if (xAction.Attribute("name") == null) 
					throw new Exception("Error creating Action from XML - 'name' attribute is required.");
				if (string.IsNullOrEmpty(xAction.Attribute("name").Value)) 
					throw new Exception("Error creating Action from XML - 'name' attribute cannot be empty.");
					
				//action ALWAYS gets a new id.  There's no reason to bother reading one from the xml.
				this.ID = Guid.NewGuid().ToString().ToLower();
	
				//(xAction.Element("description") != null ? xAction.Element("description").Value : "");
				Ecotemplate = parent;
				
				this.Name = xAction.Attribute("name").Value;
				this.Description = (xAction.Attribute("description") != null ? xAction.Attribute("description").Value : "");
				
				this.Category = (xAction.Attribute("category") != null ? xAction.Attribute("category").Value : "");
				this.Icon = (xAction.Attribute("icon") != null ? xAction.Attribute("icon").Value : "");
				
				//whether it has a task bundled inside or not, we'll still set these first from the attributes
				//and change them later if we need to.
				this.OriginalTaskID = (xAction.Attribute("original_task_id") != null ? xAction.Attribute("original_task_id").Value : "");
				this.TaskVersion = (xAction.Attribute("task_version") != null ? xAction.Attribute("task_version").Value : "");
	
				this.ParameterDefaultsXML = (xAction.Element("parameters") != null ? 
				                             xAction.Element("parameters").ToString(SaveOptions.DisableFormatting) : 
				                             "");
				
				if (xAction.Element("task") != null) 
				{
					this.Task = new Task().FromXML(xAction.Element("task").ToString(SaveOptions.DisableFormatting), ref sErr);
					
					//if the task we just imported got a new originalID (it was renamed in the xml) ???
					//we have to update the action!
					if (this.Task.OriginalTaskID != this.OriginalTaskID)
						this.OriginalTaskID = this.Task.OriginalTaskID;
				}
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}

		public string AsXML()
		{					
			try
			{
				XElement xe = new XElement("action");
				
				//don't think we need to put id's in this xml
				//xe.SetAttributeValue("id", this.ID);
				xe.SetAttributeValue("name", this.Name);
				xe.SetElementValue("description", this.Description);
				xe.SetAttributeValue("category", this.Category);
				xe.SetAttributeValue("icon", this.Icon);
				
				if (!string.IsNullOrEmpty(this.ParameterDefaultsXML))
				{
					XElement xParameters = XElement.Parse(this.ParameterDefaultsXML);
					if (xParameters != null) {	
						xe.Add(xParameters);
					}
				}				
				
				//we'll always include the original_task_id and version attributes
				//even if the task is included.
				xe.SetAttributeValue("original_task_id", this.OriginalTaskID);
				xe.SetAttributeValue("task_version", this.TaskVersion);
				if (this.IncludeTask == true)
				{
					string sErr = "";
					Task t = new Task(this.OriginalTaskID, this.TaskVersion, ref sErr);
					if (t != null) {
						XElement xTask = t.AsXElement();
						if (xTask != null) {	
							xe.Add(xTask);
						}
					}
				}
				
				return xe.ToString();
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
	}
	#endregion
	
	#region "Cloud"
	/*
	 * The Cloud Providers class contains all the definition of a Cloud Provider, including
	 * object types and their properties.
	 * 
	 * This class is instantiated at login, and the populated class is cached in the session.
	 * 
	 * The CloudProviders class is an Arraylist of Provider objects.
	 * 
	 * The Provider object has a name and other properties, including an ArrayList of CloudObjectType objects.
	 * 
	 * */
	public class CloudProviders : Dictionary<string, Provider>  //CloudProviders IS a named dictionary of Provider objects
	{
		//the constructor requires an XDocument
		public CloudProviders (XDocument xProviders)
		{
			try
			{
				dataAccess dc = new dataAccess();
				
				if (xProviders == null) {
					throw new Exception ("Error: Invalid or missing Cloud Providers XML.");
				} else {
					foreach (XElement xProvider in xProviders.XPathSelectElements("//providers/provider")) {
						if (xProvider.Attribute ("name") == null) 
							throw new Exception ("Cloud Providers XML: All Providers must have the 'name' attribute.");
						
						Provider pv = new Provider(xProvider.Attribute ("name").Value, 
						                           (xProvider.Attribute ("test_product") == null ? "" : xProvider.Attribute ("test_product").Value),
						                           (xProvider.Attribute ("test_object") == null ? "" : xProvider.Attribute ("test_object").Value),
						                           (xProvider.Attribute ("user_defined_clouds") == null ? true : (xProvider.Attribute ("user_defined_clouds").Value == "false" ? false : true))
						                           );

						IEnumerable<XElement> xClouds = xProvider.XPathSelectElements("clouds/cloud");
						
						//if this provider has hardcoded clouds... get them
						if (xClouds != null) {
							if (xClouds.Count() > 0) {
								foreach (XElement xCloud in xProvider.XPathSelectElements("clouds/cloud"))
				                {
									if (xCloud.Attribute("id") == null) 
										throw new Exception("Cloud Providers XML: All Clouds must have the 'id' attribute.");
									if (xCloud.Attribute("name") == null) 
										throw new Exception("Cloud Providers XML: All Clouds must have the 'name' attribute.");
									if (xCloud.Attribute("api_url") == null) 
										throw new Exception("Cloud Providers XML: All Clouds must have the 'api_url' attribute.");
									if (xCloud.Attribute("api_protocol") == null) 
										throw new Exception("Cloud Providers XML: All Clouds must have the 'api_protocol' attribute.");

									//region is an optional attribute
									string sRegion = "";
									if (xCloud.Attribute("region") != null) 
										sRegion = xCloud.Attribute("region").Value;

									Cloud c = new Cloud(pv, false, 
									                    xCloud.Attribute("id").Value, 
									                    xCloud.Attribute("name").Value, 
									                    xCloud.Attribute("api_url").Value, 
									                    xCloud.Attribute("api_protocol").Value, 
									                    sRegion);
									pv.Clouds.Add(c.ID, c);
								}
							}
							
							//Let's also add any clouds that may be in the database...
							//IF the "user_defined_clouds" flag is set.
							if (pv.UserDefinedClouds) {
								string sErr = "";
								string sSQL = "select cloud_id, cloud_name, api_url, api_protocol" +
					                " from clouds" +
					                " where provider = '" + pv.Name + "'" + 
									" order by cloud_name";
					
					            DataTable dt = new DataTable();
					            if (dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
					            {
					                foreach (DataRow dr in dt.Rows)
					                {
										Cloud c = new Cloud(pv, true, 
										                    dr["cloud_id"].ToString(), 
										                    dr["cloud_name"].ToString(), 
										                    dr["api_url"].ToString(), 
										                    dr["api_protocol"].ToString(),
										                    "");
										pv.Clouds.Add(c.ID, c);
									}
								}
								else 
								{
									throw new Exception("Error building Cloud object: " + sErr);	
								}
							}
						}
						
						//get the cloudobjecttypes for this provider.					
						foreach (XElement xProduct in xProvider.XPathSelectElements("products/product"))
		                {
							if (xProduct.Attribute("name") == null) 
								throw new Exception("Cloud Providers XML: All Products must have the 'name' attribute.");
							
							Product p = new Product(pv);
							p.Name = xProduct.Attribute("name").Value;
							//use the name for the label if it doesn't exist.
							p.Label = (xProduct.Attribute("label") == null ? p.Name : xProduct.Attribute("label").Value);
							p.APIUrlPrefix = (xProduct.Attribute("api_url_prefix") == null ? "" : xProduct.Attribute("api_url_prefix").Value);
							p.APIUri = (xProduct.Attribute("api_uri") == null ? "" : xProduct.Attribute("api_uri").Value);
							p.APIVersion = (xProduct.Attribute("api_version") == null ? "" : xProduct.Attribute("api_version").Value);
							
							//the product contains object type definitions
							foreach (XElement xType in xProduct.XPathSelectElements("object_types/type"))
			                {
								if (xType.Attribute("id") == null) 
									throw new Exception("Cloud Providers XML: All Object Types must have the 'id' attribute.");
								if (xType.Attribute("label") == null) 
									throw new Exception("Cloud Providers XML: All Object Types must have the 'label' attribute.");
								
								CloudObjectType cot = new CloudObjectType(p);
								cot.ID = xType.Attribute("id").Value;
								cot.Label = xType.Attribute("label").Value;
								
								cot.APICall = (xType.Attribute("api_call") == null ? "" : xType.Attribute("api_call").Value);
								cot.APIRequestGroupFilter = (xType.Attribute("request_group_filter") == null ? "" : xType.Attribute("request_group_filter").Value);
								cot.APIRequestRecordFilter = (xType.Attribute("request_record_filter") == null ? "" : xType.Attribute("request_record_filter").Value);
								cot.XMLRecordXPath = (xType.Attribute("xml_record_xpath") == null ? "" : xType.Attribute("xml_record_xpath").Value);
								
								//the type contains property definitions
								foreach (XElement xProperty in xType.XPathSelectElements("property"))
				                {
									// name="ImageId" label="" xpath="imageId" id_field="1" has_icon="0" short_list="1" sort_order="1"
									if (xProperty.Attribute("name") == null) 
										throw new Exception("Cloud Providers XML: All Object Type Properties must have the 'name' attribute.");
									
									CloudObjectTypeProperty cotp = new CloudObjectTypeProperty(cot);
									cotp.Name = xProperty.Attribute("name").Value;
									cotp.XPath = (xProperty.Attribute("xpath") == null ? "" : xProperty.Attribute("xpath").Value);
									
									cotp.Label = (xProperty.Attribute("label") == null ? "" : xProperty.Attribute("label").Value);
									cotp.SortOrder = (xProperty.Attribute("sort_order") == null ? "" : xProperty.Attribute("sort_order").Value);
									cotp.IsID = (xProperty.Attribute("id_field") == null ? false : 
										(xProperty.Attribute("id_field").Value == "1" ? true : false));
									cotp.HasIcon = (xProperty.Attribute("has_icon") == null ? false : 
										(xProperty.Attribute("has_icon").Value == "1" ? true : false));
									cotp.ShortList = (xProperty.Attribute("short_list") == null ? false : 
										(xProperty.Attribute("short_list").Value == "1" ? true : false));
									cotp.ValueIsXML = (xProperty.Attribute("value_is_xml") == null ? false : 
										(xProperty.Attribute("value_is_xml").Value == "1" ? true : false));
									
									cot.Properties.Add(cotp);
								}
								
								p.CloudObjectTypes.Add(cot.ID, cot);
							}						
								
							pv.Products.Add(p.Name, p);
						}
	
						this.Add(pv.Name, pv);
					}
				}
			}
            catch (Exception ex)
            {
				throw ex;
            }			
        }
	}
	public class Provider
	{
		private string _Name;
		private string _TestProduct;
		private string _TestObject;
		private bool _UserDefinedClouds;
		
		public string Name { get { return _Name; } }
		public string TestProduct { get { return _TestProduct; } }
		public string TestObject { get { return _TestObject; } }
		public bool UserDefinedClouds { get { return _UserDefinedClouds; } }
		
		//default empty constructor
		public Provider(string sName, string sTestProduct, string sTestObject, bool bUserDefinedClouds)
		{
			_Name = sName;
			_TestProduct = sTestProduct;
			_TestObject = sTestObject;
			_UserDefinedClouds = bUserDefinedClouds;
		}
		
		//get it by ID from the session
		static public Provider GetFromSession(string sProvider)
		{
			try
			{
				acUI.acUI ui = new acUI.acUI();
				
				//get the provider record from the CloudProviders object in the session
				CloudProviders cp = ui.GetCloudProviders();
				if (cp == null) {
					throw new Exception("Error building Provider object: Unable to GetCloudProviders.");	
				}
				
				if (cp.ContainsKey(sProvider))
					return cp[sProvider];
				else
					throw new Exception("Provider [" + sProvider + "] does not exist in the cloud_providers.xml file.");
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
		
		//Provider CONTAINS a named dictionary of Clouds;
		public Dictionary<string, Cloud> Clouds = new Dictionary<string, Cloud>();
		//Provider CONTAINS a named dictionary of Products;
		public Dictionary<string, Product> Products = new Dictionary<string, Product>();
		
		public CloudObjectType GetObjectTypeByName(string sObjectType)
		{
	        foreach (Product p in this.Products.Values)
	        {
				try
				{
					CloudObjectType cot = p.CloudObjectTypes[sObjectType];
					if (cot != null)
						return cot;
				}
	            catch (Exception)
	            {
					//don't crash while it's iterating, it may find it in the next object.
					//don't worry, we'll return null if it doesn't find anything.
				}
			}
			return null;
		}
		public Dictionary<string, CloudObjectType> GetAllObjectTypes()
		{
			try
			{
				Dictionary<string, CloudObjectType> cots = new Dictionary<string, CloudObjectType>();
				
				foreach (Product p in this.Products.Values)
				{
					foreach (CloudObjectType cot in p.CloudObjectTypes.Values)
					{
						if (cot != null)
							cots.Add(cot.ID, cot);
					}
				}
				return cots;
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
		public DataTable GetAllCloudsAsDataTable()
		{
			try
			{
				DataTable dt = new DataTable();
				dt.Columns.Add("cloud_id");
				dt.Columns.Add("cloud_name");
				dt.Columns.Add("api_url");
				dt.Columns.Add("provider", typeof(Provider));
				
				foreach (Cloud c in this.Clouds.Values)
				{
					dt.Rows.Add(c.ID, c.Name, c.APIUrl, this);
				}
				
				return dt;
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
				
		//INSTANCE METHOD - returns the object as JSON
		public string AsJSON()
		{
			try
			{
				StringBuilder sb = new StringBuilder();
				
				sb.Append("{");
				sb.AppendFormat("\"{0}\" : \"{1}\",", "Name", this.Name);
				sb.AppendFormat("\"{0}\" : \"{1}\",", "TestProduct", this.TestProduct);
				sb.AppendFormat("\"{0}\" : {1},", "UserDefinedClouds", this.UserDefinedClouds.ToString().ToLower()); //boolean has no quotes!
				sb.AppendFormat("\"{0}\" : \"{1}\",", "TestObject", this.TestObject);
	
				//clouds
				StringBuilder sbClouds = new StringBuilder();
				sbClouds.Append("{");
				
				int i = 1;
				foreach (Cloud c in this.Clouds.Values)
				{
					sbClouds.AppendFormat("\"{0}\" : {1}", c.ID, c.AsJSON());
					
					//the last one doesn't get a trailing comma
					if (i < this.Clouds.Count)
						sbClouds.Append(",");
					
					i++;
				}
				
				sbClouds.Append("}");
				
				sb.AppendFormat("\"{0}\" : {1}", "Clouds", sbClouds);
				
				sb.Append("}");
				
				return sb.ToString();
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}

		public void RefreshClouds() {
			try
			{
				this.Clouds.Clear();
				
				dataAccess dc = new dataAccess();
				
				string sErr = "";
				string sSQL = "select cloud_id, cloud_name, api_url, api_protocol" +
	                " from clouds" +
	                " where provider = '" + this.Name + "'" + 
					" order by cloud_name";
	
	            DataTable dt = new DataTable();
	            if (dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
	            {
	                foreach (DataRow dr in dt.Rows)
	                {
						Cloud c = new Cloud(this, true, 
						                    dr["cloud_id"].ToString(), 
						                    dr["cloud_name"].ToString(), 
						                    dr["api_url"].ToString(), 
						                    dr["api_protocol"].ToString(),
						                    "");
						this.Clouds.Add(c.ID, c);
					}
				}
				else 
				{
					throw new Exception("Error building Cloud object: " + sErr);	
				}
				
				return;
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
	}

	public class Product
	{
		public Provider ParentProvider { get; set; }
		public string Name { get; set; }
		public string Label { get; set; }
        public string APIUrlPrefix { get; set; }
        public string APIUri { get; set; }
		public string APIVersion { get; set; }
 		
		//constructor
		public Product(Provider parent)
		{
			this.ParentProvider = parent;
		}
		
		//Product CONTAINS a named dictionary of CloudObjectTypes;
		public Dictionary<string, CloudObjectType> CloudObjectTypes = new Dictionary<string, CloudObjectType>();
        
		public bool IsValidForCalls()
        {
            if (string.IsNullOrEmpty(this.Name))
                return false;

            return true;
        }
	}

    public class CloudObjectType
    {
		public Product ParentProduct { get; set; }
        public string ID { get; set; }
        public string Label { get; set; }
        public string APICall { get; set; }
        public string APIRequestGroupFilter { get; set; }
        public string APIRequestRecordFilter { get; set; }
        public string XMLRecordXPath { get; set; }
		
		//constructor
		public CloudObjectType(Product parent)
		{
			this.ParentProduct = parent;
		}
		
		//CloudObjectType CONTAINS an array or properties
        public ArrayList Properties = new ArrayList();

		public bool IsValidForCalls()
        {
            if (string.IsNullOrEmpty(this.XMLRecordXPath) || string.IsNullOrEmpty(this.ID))
                return false;

            return true;
        }
    }
    public class CloudObjectTypeProperty
    {
 		public CloudObjectType ParentObjectType { get; set; }
		public string Name { get; set; }
        public string Label { get; set; }
        public string XPath { get; set; }
		public string SortOrder { get; set; }
        public bool HasIcon { get; set; }
        public bool IsID { get; set; }
        public bool ShortList { get; set; }
        public bool ValueIsXML { get; set; }

		//constructor
		public CloudObjectTypeProperty(CloudObjectType parent)
		{
			this.ParentObjectType = parent;
		}
		
    }
	
	public class Clouds
	{
		public DataTable DataTable = new DataTable();
		
		public Clouds(string sFilter, ref string sErr)
		{
			try
			{
				//builds a list from the db, with the optional filter
				dataAccess dc = new dataAccess();
	            string sWhereString = "";
	
	            if (!string.IsNullOrEmpty(sFilter))
	            {
	                //split on spaces
	                int i = 0;
	                string[] aSearchTerms = sFilter.Split(' ');
	                for (i = 0; i <= aSearchTerms.Length - 1; i++)
	                {
	                    if (aSearchTerms[i].Length > 0)
	                    {
	                        sWhereString = " and (cloud_name like '%" + aSearchTerms[i] + "%' " +
	                            "or provider like '%" + aSearchTerms[i] + "%' " +
	                            "or api_url like '%" + aSearchTerms[i] + "%') ";
	                    }
	                } 
	            }
	
	            string sSQL = "select cloud_id, cloud_name, provider, api_url, api_protocol" +
	                " from clouds" +
	                " where 1=1 " + sWhereString +
	                " order by provider, cloud_name";
	
	            if (!dc.sqlGetDataTable(ref this.DataTable, sSQL, ref sErr))
	                return;
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
	}

	public class Cloud
    {
        public string ID;
		public string Name;
		public Provider Provider;
        public string APIUrl;
		public string APIProtocol;
		public string Region;
		public bool IsUserDefined;
		
		//the default constructor
		public Cloud(string sCloudID)
        {
			try
			{
				if (string.IsNullOrEmpty(sCloudID))
					throw new Exception("Error building Cloud object: Cloud ID is required.");	
				
				acUI.acUI ui = new acUI.acUI();
				
	            //search for the sCloudID in the CloudProvider Class -AND- the database
				CloudProviders cp = ui.GetCloudProviders();
				if (cp == null) {
					throw new Exception("Error building Cloud object: Unable to GetCloudProviders.");	
				}
				
				//check the CloudProvider class first ... it *should be there unless something is wrong.
				foreach (Provider p in cp.Values) {
					Dictionary<string, Cloud> cs = p.Clouds;
					foreach (Cloud c in cs.Values) {
						if (c.ID == sCloudID) {
							IsUserDefined = c.IsUserDefined;
							ID = c.ID;
							Name = c.Name;
							APIUrl = c.APIUrl;
							APIProtocol = c.APIProtocol;
							Region = c.Region;
							Provider = c.Provider;
							return;
						}				
					}
				}
				
				//well, if we got here we have a problem... the ID provided wasn't found anywhere.
				//this should never happen, so bark about it.
				throw new Exception("Unable to build Cloud object. Either no Clouds are defined, or no Cloud with ID [" + sCloudID + "] could be found.");	
			}
            catch (Exception ex)
            {
				throw ex;
            }			
        }

		//an override constructor (manual creation)
		public Cloud(Provider p, bool bUserDefined, string sID, string sName, string sAPIUrl, string sAPIProtocol, string sRegion) {
			IsUserDefined = bUserDefined;
			ID = sID;
			Name = sName;
			APIUrl = sAPIUrl;
			APIProtocol = sAPIProtocol;
			Region = sRegion;
			Provider = p;
		}
		
        public bool IsValidForCalls()
        {
            if (string.IsNullOrEmpty(this.APIUrl) || string.IsNullOrEmpty(this.APIProtocol))
                return false;

            return true;
        }
		
		public string AsJSON()
		{
			try
			{
				StringBuilder sb = new StringBuilder();
				
				sb.Append("{");
				sb.AppendFormat("\"{0}\" : \"{1}\",", "ID", this.ID);
				sb.AppendFormat("\"{0}\" : \"{1}\",", "Name", this.Name);
				sb.AppendFormat("\"{0}\" : \"{1}\",", "Provider", this.Provider.Name);
				sb.AppendFormat("\"{0}\" : \"{1}\",", "APIUrl", this.APIUrl);
				sb.AppendFormat("\"{0}\" : \"{1}\",", "APIProtocol", this.APIProtocol);
				sb.AppendFormat("\"{0}\" : \"{1}\"", "Region", this.Region);
				sb.Append("}");
				
				return sb.ToString();
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
		
		
		//CLASS METHOD
		//creates this Cloud as a new record in the db
		//and returns the object
		static public Cloud DBCreateNew(string sCloudName, string sProvider, string sAPIUrl, string sAPIProtocol, ref string sErr)
		{
			try
			{
	            dataAccess dc = new dataAccess();
	            acUI.acUI ui = new acUI.acUI();
				string sSQL = "";
				
				string sNewID = ui.NewGUID();
				
				sSQL = "insert into clouds (cloud_id, cloud_name, provider, api_url, api_protocol)" +
                    " values ('" + sNewID + "'," +
                    "'" + sCloudName + "'," +
                    "'" + sProvider + "'," +
                    "'" + sAPIUrl + "'," +
                    "'" + sAPIProtocol + "')";
				
				if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
				{
					if (sErr == "key_violation")
					{
						sErr = "A Cloud with that name already exists.  Please select another name.";
						return null;
					}
					else 
						throw new Exception(sErr);
				}
				
				ui.WriteObjectAddLog(Globals.acObjectTypes.Cloud, sNewID, sCloudName, "Cloud Created");
				
				//update the CloudProviders in the session
				CloudProviders cp = ui.GetCloudProviders();  //get the session object
				cp[sProvider].RefreshClouds(); //find the proper Provider IN THE SESSION OBJECT and tell it to refresh it's clouds.
				ui.UpdateCloudProviders(cp); //update the session
				
				//now it's inserted... lets get it back from the db as a complete object for confirmation.
				Cloud c = new Cloud(sNewID);

				//yay!
				return c;
			}
			catch (Exception ex)
			{
				throw new Exception(ex.Message);
			}		
		}
		
		//INSTANCE METHOD
		//updates the current Cloud object to the db
		public bool DBUpdate(ref string sErr)
		{
			try
			{
				acUI.acUI ui = new acUI.acUI();
	            dataAccess dc = new dataAccess();
				string sSQL = "";
				
				//of course we do nothing if this cloud was hardcoded in the xml
				//just return success, which should never happen since the user can't get to edit a hardcoded Cloud anyway.
				if (!this.IsUserDefined)
					return true;
				
				//what's the original name?
				string sOriginalName = "";
				sSQL = "select cloud_name from clouds where cloud_id = '" + this.ID + "'";
				if (!dc.sqlGetSingleString(ref sOriginalName, sSQL, ref sErr))
					throw new Exception("Error getting original cloud name:" + sErr);
	
				sSQL = "update clouds set" +
                        " cloud_name = '" + this.Name + "'," +
                        " provider = '" + this.Provider.Name + "'," +
                        " api_protocol = '" + this.APIProtocol + "'," +
                        " api_url = '" + this.APIUrl + "'" +
                        " where cloud_id = '" + this.ID + "'";
				
				if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
				{
					if (sErr == "key_violation")
					{
						sErr = "A Cloud with that name already exists.  Please select another name.";
						return false;
					}
					else 
						throw new Exception(sErr);
				}
				
				ui.WriteObjectPropertyChangeLog(Globals.acObjectTypes.Cloud, this.ID, this.Name, sOriginalName, this.Name);

				//update the CloudProviders in the session
				CloudProviders cp = ui.GetCloudProviders();  //get the session object
				cp[this.Provider.Name].RefreshClouds(); //find the proper Provider IN THE SESSION OBJECT and tell it to refresh it's clouds.
				ui.UpdateCloudProviders(cp); //update the session

				return true;
			}
			catch (Exception ex)
			{
				throw new Exception(ex.Message);
			}		
		}
   }
	
	//CloudAccounts contains a DataTable
	//more efficient to read from the DB as a DataTable than to loop and create a dictionary.
	//if you want a dictionary, that's an instance method.
	public class CloudAccounts
	{
		public DataTable DataTable = new DataTable();
		
		public CloudAccounts(string sFilter, ref string sErr)
		{
			try
			{
				//builds a list from the db, with the optional filter
				dataAccess dc = new dataAccess();
	            string sWhereString = "";
	
	            if (!string.IsNullOrEmpty(sFilter))
	            {
	                //split on spaces
	                int i = 0;
	                string[] aSearchTerms = sFilter.Split(' ');
	                for (i = 0; i <= aSearchTerms.Length - 1; i++)
	                {
	                    if (aSearchTerms[i].Length > 0)
	                    {
	                        sWhereString = " and (account_name like '%" + aSearchTerms[i] + "%' " +
	                            "or account_number like '%" + aSearchTerms[i] + "%' " +
	                            "or provider like '%" + aSearchTerms[i] + "%' " +
	                            "or login_id like '%" + aSearchTerms[i] + "%') ";
	                    }
	                } 
	            }
	
	            string sSQL = "select account_id, account_name, account_number, provider, login_id, auto_manage_security," +
	                " case is_default when 1 then 'Yes' else 'No' end as is_default," +
					" (select count(*) from ecosystem where account_id = cloud_account.account_id) as has_ecosystems" +
	                " from cloud_account" +
	                " where 1=1 " + sWhereString +
	                " order by is_default desc, account_name";
	
	            if (!dc.sqlGetDataTable(ref this.DataTable, sSQL, ref sErr))
	                return;
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}

		public string AsJSON()
		{
			try
			{
				StringBuilder sb = new StringBuilder();

				sb.Append("[");

				int i = 1;
				foreach (DataRow dr in this.DataTable.Rows)
				{
					sb.Append("{");
					sb.AppendFormat("\"{0}\" : \"{1}\",", "ID", dr["account_id"].ToString());
					sb.AppendFormat("\"{0}\" : \"{1}\"", "Name", dr["account_name"].ToString());
					sb.Append("}");
					
					//the last one doesn't get a trailing comma
					if (i < dr.Table.Rows.Count)
						sb.Append(",");

					i++;
				}

				sb.Append("]");
				
				return sb.ToString();
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
	}

	public class CloudAccount
    {
        public string ID;
		public string Name;
		public string AccountNumber;
        public string LoginID;
        public string LoginPassword;
		public bool IsDefault;

		public Provider Provider;
		
		//the default constructor
		public CloudAccount(string sAccountID)
        {
			try
			{
				if (string.IsNullOrEmpty(sAccountID))
					throw new Exception("Error building Cloud Account object: Cloud Account ID is required.");	
				
	            dataAccess dc = new dataAccess();
				
	            string sErr = "";
	
	            string sSQL = "select account_name, account_number, provider, login_id, login_password, is_default" +
	                " from cloud_account" +
	                " where account_id = '" + sAccountID + "'";
	
	            DataRow dr = null;
	            if (dc.sqlGetDataRow(ref dr, sSQL, ref sErr))
	            {
	                if (dr != null)
	                {
						ID = sAccountID;
						Name = dr["account_name"].ToString();
						AccountNumber = (string.IsNullOrEmpty(dr["account_number"].ToString()) ? "" : dr["account_number"].ToString());
						LoginID = (string.IsNullOrEmpty (dr["login_id"].ToString()) ? "" : dr["login_id"].ToString());
						LoginPassword = (string.IsNullOrEmpty (dr["login_password"].ToString()) ? "" : dc.DeCrypt(dr["login_password"].ToString()));
						IsDefault = (dr["is_default"].ToString() == "1" ? true : false);
						
						Provider p = Provider.GetFromSession(dr["provider"].ToString());
						if (p == null) {
							throw new Exception("Error building CloudAccount object: No Provider for name [" + dr["provider"].ToString() + "] defined in session.");	
						}
						
						Provider = p;
					}
					else 
					{
						throw new Exception("Unable to build Cloud Account object. Either no Cloud Accounts are defined, or no Account with ID [" + sAccountID + "] could be found.");	
					}
				}
				else 
				{
					throw new Exception("Error building Cloud Account object: " + sErr);	
				}
			}
            catch (Exception ex)
            {
				throw ex;
            }			
        }
		
        public bool IsValidForConnections()
        {
			if (string.IsNullOrEmpty (this.LoginID))
				return false;

			if (string.IsNullOrEmpty (this.LoginPassword))
				return false;

            return true;
        }
		
		//INSTANCE METHOD - returns the object as JSON
		public string AsJSON()
		{
			try
			{
				StringBuilder sb = new StringBuilder();
				
				sb.Append("{");
				sb.AppendFormat("\"{0}\" : \"{1}\",", "ID", this.ID);
				sb.AppendFormat("\"{0}\" : \"{1}\",", "Name", this.Name);
				sb.AppendFormat("\"{0}\" : \"{1}\",", "AccountNumber", this.AccountNumber);
				sb.AppendFormat("\"{0}\" : {1},", "IsDefault", this.IsDefault.ToString().ToLower()); //boolean has no quotes!
				sb.AppendFormat("\"{0}\" : \"{1}\",", "LoginID", this.LoginID);
				sb.AppendFormat("\"{0}\" : \"{1}\",", "LoginPassword", this.LoginPassword);
				sb.AppendFormat("\"{0}\" : \"{1}\",", "Provider", this.Provider.Name);
	
				//providers clouds for this account
				StringBuilder sbClouds = new StringBuilder();
				sbClouds.Append("{");
				
				int i = 1;
				foreach (Cloud c in this.Provider.Clouds.Values)
				{
					sbClouds.AppendFormat("\"{0}\" : {1}", c.ID, c.AsJSON());
					
					//the last one doesn't get a trailing comma
					if (i < this.Provider.Clouds.Count)
						sbClouds.Append(",");
					
					i++;
				}
				
				sbClouds.Append("}");
				
				sb.AppendFormat("\"{0}\" : {1}", "Clouds", sbClouds);
				
				sb.Append("}");
				
				return sb.ToString();
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
		
		//CLASS METHOD
		//creates this Cloud as a new record in the db
		//and returns the object
		static public CloudAccount DBCreateNew(string sAccountName, string sAccountNumber, string sProvider, 
		                                       string sLoginID, string sLoginPassword, string sIsDefault, ref string sErr)
		{
			try
			{
	            dataAccess dc = new dataAccess();
	            acUI.acUI ui = new acUI.acUI();
	
				dataAccess.acTransaction oTrans = new dataAccess.acTransaction(ref sErr);
				
				//if there are no rows yet, make this one the default even if the box isn't checked.
				if (sIsDefault == "0")
				{
					int iExists = -1;
					
					string sSQL = "select count(*) as cnt from cloud_account";
					if (!dc.sqlGetSingleInteger(ref iExists, sSQL, ref sErr)) {
						oTrans.RollBack();
						throw new Exception("Unable to count Cloud Accounts: " + sErr);
					}
					
					if (iExists == 0)
						sIsDefault = "1";
				}

				string sNewID = ui.NewGUID();
				
				oTrans.Command.CommandText = "insert into cloud_account" +
					" (account_id, account_name, account_number, provider, is_default, login_id, login_password, auto_manage_security)" +
                    " values ('" + sNewID + "'," +
                    "'" + sAccountName + "'," +
                    "'" + sAccountNumber + "'," +
                    "'" + sProvider + "'," +
                    "'" + sIsDefault + "'," +
                    "'" + sLoginID + "'," +
                    "'" + dc.EnCrypt(sLoginPassword) + "'," +
                    "0)";
				
				if (!oTrans.ExecUpdate(ref sErr))
				{
					if (sErr == "key_violation")
					{
						sErr = "A Cloud Account with that name already exists.  Please select another name.";
						return null;
					}
					else 
						throw new Exception(sErr);
				}
				
                //if "default" was selected, unset all the others
                if (dc.IsTrue(sIsDefault))
                {
                    oTrans.Command.CommandText = "update cloud_account set is_default = 0 where account_id <> '" + sNewID + "'";
                    if (!oTrans.ExecUpdate(ref sErr))
                        throw new Exception("Error resetting default Cloud Account: " + sErr);
                }

				oTrans.Commit();

				ui.WriteObjectAddLog(Globals.acObjectTypes.CloudAccount, sNewID, sAccountName, "Account Created");

				//refresh the cloud account list in the session
	            if (!ui.PutCloudAccountsInSession(ref sErr))
					throw new Exception("Error refreshing Cloud Accounts in session: " + sErr);
				
				//now it's inserted... lets get it back from the db as a complete object for confirmation.
				CloudAccount ca = new CloudAccount(sNewID);

				//yay!
				return ca;
			}
			catch (Exception ex)
			{
				throw new Exception(ex.Message);
			}		
		}

		//INSTANCE METHOD
		//updates the current Cloud object to the db
		public bool DBUpdate(ref string sErr)
		{
			try
			{
				acUI.acUI ui = new acUI.acUI();
	            dataAccess dc = new dataAccess();
				string sSQL = "";
				
				//what's the original name?
				string sOriginalName = "";
				sSQL = "select account_name from cloud_account where account_id = '" + this.ID + "'";
				if (!dc.sqlGetSingleString(ref sOriginalName, sSQL, ref sErr))
					throw new Exception("Error getting original Cloud Account Name:" + sErr);
	
				// only update the passwword if it has changed
                string sNewPassword = "";
                if (this.LoginPassword != "($%#d@x!&")
                {
                    sNewPassword = ", login_password = '" + dc.EnCrypt(this.LoginPassword) + "'";
                }

				sSQL = "update cloud_account set" +
                        " account_name = '" + this.Name + "'," +
                        " account_number = '" + this.AccountNumber + "'," +
                        " provider = '" + this.Provider.Name + "'," +
                        " is_default = '" + (this.IsDefault ? 1 : 0) + "'," +
                        " auto_manage_security = 0," +
                        " login_id = '" + this.LoginID + "'" +
                        sNewPassword +
                        " where account_id = '" + this.ID + "'";
				
				if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
				{
					if (sErr == "key_violation")
					{
						sErr = "A Cloud Account with that name already exists.  Please select another name.";
						return false;
					}
					else 
						throw new Exception(sErr);
				}
				
				ui.WriteObjectPropertyChangeLog(Globals.acObjectTypes.CloudAccount, this.ID, this.Name, sOriginalName, this.Name);

                //if "default" was selected, unset all the others
                if (this.IsDefault)
				{
					sSQL = "update cloud_account set is_default = 0 where account_id <> '" + this.ID + "'";
					//not worth failing... we'll just end up with two defaults.
					dc.sqlExecuteUpdate(sSQL, ref sErr);
                }

				//refresh the cloud account list in the session
	            if (!ui.PutCloudAccountsInSession(ref sErr))
					throw new Exception("Error refreshing Cloud Accounts in session: " + sErr);

				return true;
			}
			catch (Exception ex)
			{
				throw new Exception(ex.Message);
			}		
		}

	}

#endregion
	
	#region "Task Steps, Categories and Functions"
	
	//FunctionCategories IS a named dictionary of task command Category objects
	//it's useful for spinning categories and functions hierarchically, as when building the command toolbox
	public class FunctionCategories : Dictionary<string, Category>
	{
		//this default constructor - an empty object
		public FunctionCategories ()
		{
		}
		
		//method to load from the disk
		public bool Load(string sFileName)
		{
			try 
			{
				XDocument xCategories = XDocument.Load(sFileName);
				if (xCategories == null) {
					//crash... we can't do anything if the XML is busted
					return false;
					//throw new Exception ("Error: (FunctionCategories Class) Invalid or missing Task Command XML.");
				} else {		
					foreach (XElement xCategory in xCategories.XPathSelectElements("//categories/category"))
					{
						Category cat = BuildCategory(xCategory);
						if (cat != null)
							this.Add(cat.Name, cat);
					}
					return true;
				}
			}
            catch (Exception ex)
            {
				throw ex;
            }			
        }
		
		//method to append from the disk
		//nearly identical to Load, but doesn't crash if the file is malformed, just skips it.
		public bool Append(string sFileName)
		{
			try 
			{
				XDocument xCategories = XDocument.Load(sFileName);
				if (xCategories == null) {
					return false;
				} else {
					foreach (XElement xCategory in xCategories.XPathSelectElements("//categories/category"))
					{
						Category cat = BuildCategory(xCategory);
						if (cat != null)
							this.Add(cat.Name, cat);
					}
				}
				return true;
			}
            catch (Exception)
            {
				return false;
            }			
        }
		
		private Category BuildCategory(XElement xCategory)
		{
			//not crashing... just skipping
			if (xCategory.Attribute ("name") == null) 
				return null;
			
			//not crashing... just skipping
			if (string.IsNullOrEmpty(xCategory.Attribute("name").Value)) 
				return null;
			
			//ok, minimal data is intact... proceed...
			Category cat = new Category();
			cat.Name = xCategory.Attribute("name").Value;
			cat.Label = (xCategory.Attribute("label") == null ? xCategory.Attribute("name").Value : xCategory.Attribute("label").Value);
			cat.Description = (xCategory.Attribute("description") == null ? "" : xCategory.Attribute("description").Value);
			cat.Icon = (xCategory.Attribute("icon") == null ? "" : xCategory.Attribute("icon").Value);
		
			
			//load up this category with it's functions
			foreach (XElement xFunction in xCategory.XPathSelectElements("commands/command"))
			{
				//not crashing... just skipping
				if (xFunction.Attribute ("name") == null) 
					continue;
				
				//not crashing... just skipping
				if (string.IsNullOrEmpty(xFunction.Attribute("name").Value)) 
					continue;
				
				//ok, minimal data is intact... proceed...
				Function fn = new Function(cat);
				fn.Name = xFunction.Attribute("name").Value;
				fn.Label = (xFunction.Attribute("label") == null ? xFunction.Attribute("name").Value : xFunction.Attribute("label").Value);
				fn.Description = (xFunction.Attribute("description") == null ? "" : xFunction.Attribute("description").Value);
				fn.Help = (xFunction.Attribute("help") == null ? "" : xFunction.Attribute("help").Value);
				fn.Icon = (xFunction.Attribute("icon") == null ? "" : xFunction.Attribute("icon").Value);
				
				if (xFunction.Element("function") != null)
				{
					if (!string.IsNullOrEmpty(xFunction.Element("function").ToString()))
					{
						fn.TemplateXML = xFunction.Element("function").ToString();
						fn.TemplateXDoc = new XDocument(xFunction.Element("function"));
					}
				}						
				cat.Functions.Add(fn.Name, fn);
			}
			
			return cat;
		}
	}
	
	//Functions IS a named dictionary of ALL Function objects
	//used when you know the function by name and need to lookup all it's details
	//as in when drawing a step
	public class Functions : Dictionary<string, Function>
	{
		//the constructor requires an FunctionCategories class, and it flattens it.
		//should only happen once at login and be cached in the session
		//but searching this dictionary will be faster because it's flat
		public Functions (FunctionCategories fc)
		{
			try
			{
				if (fc == null) {
					//crash... we can't do anything if the XML is busted
					throw new Exception ("Error: (Functions Class) Invalid or missing FunctionCategories Class.");
				} else {
					foreach (Category cat in fc.Values)
					{
						foreach (Function fn in cat.Functions.Values)
						{
							this.Add(fn.Name, fn);
						}
					}
				}
			}
            catch (Exception ex)
            {
				throw ex;
            }			
        }
		
		//this default constructor
		public Functions ()
		{
		}
	}
	
	public class Category
	{
		public string Name;
		public string Label;
		public string Description;
		public string Icon;

		//Category CONTAINS a named dictionary of Function objects;
		public Functions Functions = new Functions();
}
	public class Function
	{
		public string Name;
		public string Label;
		public string Description;
		public string Help;
		public string Icon;
		public Category Category; //Function has a parent Category
		public string TemplateXML;
		public XDocument TemplateXDoc;
		
		//blank constructor
		public Function()
		{
		}
		
		//constructor by Category object
		public Function(Category parent)
		{
			this.Category = parent;
		}
		
		//class method - get Function by function name !! requires session
		public static Function GetFunctionByName(string sFunctionName)
		{
			try
			{
				acUI.acUI ui = new acUI.acUI();
				Function fn = ui.GetTaskFunction(sFunctionName);
				if (fn != null)
					return fn;
				
				return null;
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}

		//class method - get Function from step_id
		public static Function GetFunctionForStep(string sStepID)
		{
			try
			{
				dataAccess dc = new dataAccess();
				string sErr = "";
				
				string sFunctionName = "";
				string sSQL = "select function_name from task_step where step_id = '" + sStepID + "'";
				if (!dc.sqlGetSingleString(ref sFunctionName, sSQL, ref sErr))
					throw new Exception(sErr);
				
				if (sFunctionName.Length > 0)
				{
					Function func = GetFunctionByName(sFunctionName);
					if (func == null)
						throw new Exception("Unable to look up [" + sFunctionName + "] in Function class.");
					
					return func;
				}
				
				return null;
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
	}
	
	//ClipboardSteps is a dictionary of clipboardStep objects
	public class ClipboardSteps : Dictionary<string, ClipboardStep>
	{
		public ClipboardSteps(string sUserID)
		{
			try
			{
				dataAccess dc = new dataAccess();
				string sErr = "";
				
				//note: some literal values are selected here.  That's because DrawReadOnlyStep
	            //requires a more detailed record, but the snip doesn't have some of those values
	            //so we hardcode them.
	            string sSQL = "select s.clip_dt, s.step_id, s.step_desc, s.function_name, s.function_xml," +
	                " s.output_parse_type, s.output_row_delimiter, s.output_column_delimiter, s.variable_xml" +
	                " from task_step_clipboard s" +
	                " where s.user_id = '" + sUserID + "'" +
	                " and s.codeblock_name is null" +
	                " order by s.clip_dt desc";
	
	            DataTable dt = new DataTable();
	            if (!dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
	            {
	                throw new Exception("Unable to get clipboard data for user [" + sUserID + "].<br />" + sErr);
	            }
	
				if (dt.Rows.Count > 0)
	            {
					foreach(DataRow dr in dt.Rows)
					{
						ClipboardStep cs = new ClipboardStep(dr);
						if (cs != null)
							this.Add(cs.ID, cs);
					}
				}
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
	}
	public class ClipboardStep
	{
		public string ID;
		public string ClipDT;
		public int Order;
		public string Description;
		public int OutputParseType;
		public int OutputRowDelimiter;
		public int OutputColumnDelimiter;
		public string FunctionXML;
		public string VariableXML;
		public string FunctionName;
		
		public XDocument FunctionXDoc;
		public XDocument VariableXDoc;

		public ClipboardStep(DataRow dr)
		{
			try
			{
				this.ID = dr["step_id"].ToString();
				this.ClipDT = dr["clip_dt"].ToString();
				this.Order = -1;
				this.Description = (string.IsNullOrEmpty(dr["step_desc"].ToString()) ? "" : dr["step_desc"].ToString());
			
				this.OutputParseType = (int)dr["output_parse_type"];
				this.OutputRowDelimiter = (int)dr["output_row_delimiter"];
				this.OutputColumnDelimiter = (int)dr["output_column_delimiter"];
	
				this.FunctionXML = (string.IsNullOrEmpty(dr["function_xml"].ToString()) ? "" : dr["function_xml"].ToString());
				this.VariableXML = (string.IsNullOrEmpty(dr["variable_xml"].ToString()) ? "" : dr["variable_xml"].ToString());
				
				if (!string.IsNullOrEmpty(this.FunctionXML)) 
					this.FunctionXDoc = XDocument.Parse(this.FunctionXML);
				if (!string.IsNullOrEmpty(this.VariableXML)) 
					this.VariableXDoc = XDocument.Parse(this.VariableXML);
				
				//this.Function = Function.GetFunctionByName(dr["function_name"].ToString());
				this.FunctionName = dr["function_name"].ToString();
			}
            catch (Exception ex)
            {
				throw ex;
            }			
		}
	}
	
	public class Step
	{
		//So, why does the step not have a full Function object associated with it?
		//easy - the function definitions are in an xml file, and we don't wanna be hitting that every single time we draw a step.
		//and since many times these objects are instantiated via web methods, we can't use a session like the gui does.
		//so, it's left to store the function "name" here, and get a function object using that name only when it's necessary.
		
		public string ID;
		public string Codeblock;
		public int Order;
		public string Description;
		public bool Commented;
		public bool Locked;
		public int OutputParseType;
		public int OutputRowDelimiter;
		public int OutputColumnDelimiter;
		public string FunctionXML;
		public string VariableXML;
		public string FunctionName; //denormalized here from the Function object because sometimes all we need is a name not a full function
		
		public XDocument FunctionXDoc;
		public XDocument VariableXDoc;
			
		public Task Task; // step has a parent task
		public StepUserSettings UserSettings = new StepUserSettings(); //user settings cannot be null, they have defaults.
		
		//constructor from an xElement
		public Step(XElement xStep, Codeblock c, Task t)
		{
			try 
			{	
				if (xStep != null)
				{
					this.ID = Guid.NewGuid().ToString().ToLower();
					this.Codeblock = c.Name;
					this.Task = t;
					
					//stuff that shouldn't matter from the XML and we need to work out if it's required.
					this.Order = 0;
					this.Locked = false;
		
					this.Description = (xStep.Element("description") != null ? xStep.Element("description").Value : "");
		
					this.Commented = (xStep.Attribute("commented") != null ? (xStep.Attribute("commented").Value == "1" ? true : false) : false);
					
					int i = 0;
		
					if (xStep.Attribute("output_parse_type") != null)
					{
						int.TryParse(xStep.Attribute("output_parse_type").Value, out i);
						this.OutputParseType = i;
					}
					if (xStep.Attribute("output_row_delimiter") != null)
					{
						int.TryParse(xStep.Attribute("output_row_delimiter").Value, out i);
						this.OutputRowDelimiter = i;
					}
					if (xStep.Attribute("output_column_delimiter") != null)
					{
						int.TryParse(xStep.Attribute("output_column_delimiter").Value, out i);
						this.OutputColumnDelimiter = i;
					}
		
					if (xStep.Element("function") != null)
					{
						this.FunctionXML = (string.IsNullOrEmpty(xStep.Element("function").ToString()) ? "" : xStep.Element("function").ToString());
		
						//once parsed, it's cleaner.  update the object with the cleaner xml
						if (!string.IsNullOrEmpty(this.FunctionXML))
						{
							this.FunctionXDoc = XDocument.Parse(this.FunctionXML);
							if (this.FunctionXDoc != null) 
							{
								//well for now this method is for the API and xml based task creation, not the gui.
								//so, the full function object is not required.
								if (this.FunctionXDoc.Element("function").Attribute("command_type") != null)
									this.FunctionName = this.FunctionXDoc.Element("function").Attribute("command_type").Value;
								else
									throw new Exception("Step from XElement: Function attribute 'command_type' is required and missing.");
								
								this.FunctionXML = this.FunctionXDoc.ToString(SaveOptions.DisableFormatting);
							}
						}
					}
					
					if (xStep.Element("variable_xml") != null)
					{
						this.VariableXML = (string.IsNullOrEmpty(xStep.Element("variable_xml").ToString()) ? "" : xStep.Element("variable_xml").ToString());
		
						//once parsed, it's cleaner.  update the object with the cleaner xml
						if (!string.IsNullOrEmpty(this.VariableXML)) 
						{
							this.VariableXDoc = XDocument.Parse(this.VariableXML);
							this.VariableXML = this.VariableXDoc.ToString(SaveOptions.DisableFormatting);
						}
					}
				}
            }
            catch (Exception ex)
            {
				throw ex;
            }
		}
		
		//constructor from a DataRow
		public Step(DataRow dr, Task oTask)
		{
			PopulateStep(dr, oTask);
		}
		private Step PopulateStep(DataRow dr, Task oTask)
		{
			try
			{	
				this.ID = dr["step_id"].ToString();
				this.Codeblock = (string.IsNullOrEmpty(dr["codeblock_name"].ToString()) ? "" : dr["codeblock_name"].ToString());
				this.Order = (int)dr["step_order"];
				this.Description = (string.IsNullOrEmpty(dr["step_desc"].ToString()) ? "" : dr["step_desc"].ToString());
	
				this.Commented = (dr["commented"].ToString() == "0" ? false : true);
				this.Locked = (dr["locked"].ToString() == "0" ? false : true);
				
				this.OutputParseType = (int)dr["output_parse_type"];
				this.OutputRowDelimiter = (int)dr["output_row_delimiter"];
				this.OutputColumnDelimiter = (int)dr["output_column_delimiter"];
	
				this.FunctionXML = (string.IsNullOrEmpty(dr["function_xml"].ToString()) ? "" : dr["function_xml"].ToString());
				this.VariableXML = (string.IsNullOrEmpty(dr["variable_xml"].ToString()) ? "" : dr["variable_xml"].ToString());
				
				//once parsed, it's cleaner.  update the object with the cleaner xml
				if (!string.IsNullOrEmpty(this.FunctionXML)) 
				{
					this.FunctionXDoc = XDocument.Parse(this.FunctionXML);
					this.FunctionXML = this.FunctionXDoc.ToString(SaveOptions.DisableFormatting);
				}
				if (!string.IsNullOrEmpty(this.VariableXML)) 
				{
					this.VariableXDoc = XDocument.Parse(this.VariableXML);
					this.VariableXML = this.VariableXDoc.ToString(SaveOptions.DisableFormatting);
				}
	
				//this.Function = Function.GetFunctionByName(dr["function_name"].ToString());
				this.FunctionName = dr["function_name"].ToString();
				
				
				//NOTE!! :oTask can possibly be null, in lots of cases where we are just getting a step and don't know the task.
				//if it's null, it will not populate the parent object.
				//this happens all over the place in the HTMLTemplates stuff, and we don't need the extra overhead of the same task
				//object being created hundreds of times.
				
				if (oTask != null)
				{
					this.Task = oTask;
				}
				else 
				{
					//NOTE HACK TODO - this is bad and wrong
					//we shouldn't assume the datarow was a join to the task table... but in a few places it was.
					//so we're populating some stuff here.
					
					//the right approach is to create a full Task object from the ID, but we need to analyze
					//how it's working, so we don't create a bunch more database hits.
					
					//I THINK THIS is only happening on taskStepVarsEdit, but double check.
					this.Task = new Task();
					this.Task.ID = dr["task_id"].ToString();
		
					if (dr["task_name"] != null)
						this.Task.Name = dr["task_name"].ToString();
					if (dr["version"] != null)
						this.Task.Version = dr["version"].ToString();
				}
				
				return this;
            }
            catch (Exception ex)
            {
				throw ex;
            }
		}
		
		//constructor from a step_id AND user_id ... will include settings
		public Step(string sStepID, string sUserID, ref string sErr)
		{
			try
			{
					dataAccess dc = new dataAccess();
	
	            string sSQL = "select t.task_name, t.version," +
	                " s.step_id, s.task_id, s.step_order, s.codeblock_name, s.step_desc, s.function_name, s.function_xml, s.commented, s.locked," +
	                " s.output_parse_type, s.output_row_delimiter, s.output_column_delimiter, s.variable_xml" +
	                " from task_step s" +
	                " join task t on s.task_id = t.task_id" +
	                " where s.step_id = '" + sStepID + "' limit 1";
	
	            DataTable dt = new DataTable();
	            if (!dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
	            {
	                throw new Exception("Unable to get data row for step_id [" + sStepID + "].<br />" + sErr);
	            }
	
				if (dt.Rows.Count == 1)
	            {
					PopulateStep(dt.Rows[0], null);
					GetUserSettings(sUserID);
				}
            }
            catch (Exception ex)
            {
				throw ex;
            }
		}

		//constructor from a clipboard step!
		public Step(ClipboardStep cs)
		{
			try
			{
				this.ID = cs.ID;
				this.Order = cs.Order;
				this.Description = cs.Description;
			
				this.OutputParseType = cs.OutputParseType;
				this.OutputRowDelimiter = cs.OutputRowDelimiter;
				this.OutputColumnDelimiter = cs.OutputColumnDelimiter;
	
				this.FunctionXML = cs.FunctionXML;
				this.VariableXML = cs.VariableXML;
				
				//once parsed, it's cleaner.  update the object with the cleaner xml
				if (!string.IsNullOrEmpty(this.FunctionXML)) 
				{
					this.FunctionXDoc = XDocument.Parse(this.FunctionXML);
					this.FunctionXML = this.FunctionXDoc.ToString(SaveOptions.DisableFormatting);
				}
				if (!string.IsNullOrEmpty(this.VariableXML)) 
				{
					this.VariableXDoc = XDocument.Parse(this.VariableXML);
					this.VariableXML = this.VariableXDoc.ToString(SaveOptions.DisableFormatting);
				}
	
				this.FunctionName = cs.FunctionName;
            }
            catch (Exception ex)
            {
				throw ex;
            }
		}

		public void GetUserSettings(string sUserID)
		{
			try
			{
				dataAccess dc = new dataAccess();
				string sErr = "";
				string sSQL = "select visible, breakpoint, skip, button" +
					" from task_step_user_settings" +
						" where user_id = '" + sUserID + "'" +
						" and step_id = '" + this.ID + "' limit 1";
				
				DataRow dr = null;
				if (!dc.sqlGetDataRow(ref dr, sSQL, ref sErr))
				{
					throw new Exception("Unable to get data row for step_id [" + this.ID + "].<br />" + sErr);
				}
				
				if (dr != null)
				{
					this.UserSettings.Visible = (string.IsNullOrEmpty(dr["visible"].ToString()) ? true : (dr["visible"].ToString() == "0" ? false : true));
					this.UserSettings.Breakpoint = (string.IsNullOrEmpty(dr["breakpoint"].ToString()) ? true : (dr["breakpoint"].ToString() == "0" ? false : true));
					this.UserSettings.Skip = (string.IsNullOrEmpty(dr["skip"].ToString()) ? true : (dr["skip"].ToString() == "0" ? false : true));
					this.UserSettings.Button = (string.IsNullOrEmpty(dr["button"].ToString()) ? "" : dr["button"].ToString());
				}
            }
            catch (Exception ex)
            {
				throw ex;
            }
		}
		
		public XElement AsXElement()
		{					
			try 
			{
				//if there's no function XML we're not doing anything... this step is busted.
				if (this.FunctionXDoc != null) {
					XElement xStep = new XElement("step");
					
					//the ID isn't necessary, unless this step is 'embedded' OR allows embedded.
					//how do we tell?  easy... the codeblock_name is a guid and the step_order is -1
					if (this.Codeblock.Length == 36 && this.Order == -1)
						xStep.SetAttributeValue("id", this.ID);
					if ("if,loop,exists,while".Contains(this.FunctionName.ToLower()))
						xStep.SetAttributeValue("id", this.ID);
					
					xStep.SetAttributeValue("output_parse_type", this.OutputParseType);
					xStep.SetAttributeValue("output_column_delimiter", this.OutputColumnDelimiter);
					xStep.SetAttributeValue("output_row_delimiter", this.OutputRowDelimiter);
					xStep.SetAttributeValue("commented", this.Commented);
					
					xStep.SetElementValue("description", this.Description);
					
					XElement xeFunc = XElement.Parse(this.FunctionXDoc.ToString(SaveOptions.DisableFormatting));
					xStep.Add(xeFunc);
					
					//variables aren't required but might be here.
					if (this.VariableXDoc != null) {	
						XElement xeVars = XElement.Parse(this.VariableXDoc.ToString(SaveOptions.DisableFormatting));
						xStep.Add(xeVars);
					}
					
					return xStep;
				}
				
				return null;
            }
            catch (Exception ex)
            {
				throw ex;
            }
		}
		public string AsXML()
		{
			XElement xd = this.AsXElement();
			if (xd != null)
				return xd.ToString();
			else 
				return null;
		}
	}
	
	public class Codeblock
	{
		public string Name;
		
		//a codeblock contains a dictionary collection of steps
		public Dictionary<string, Step> Steps = new Dictionary<string, Step>();
		
		public Codeblock(string sCodeblockName)
		{
			this.Name = sCodeblockName;
		}
	}
	public class Tasks : Dictionary<string, Task>  //Tasks is a shallow collection of Task objects
	{
		//NOTE: these are NOT complete tasks... just the key properties.
		//IF you wanna get a full task from this collection...
		//do a "new Task(
		public string ID;
		public string OriginalTaskID;
		public string Name;
		public string Code;
		public string Version;
		public string Status;
		public string Description;
		public bool IsDefaultVersion;

		public Tasks(string sFilter)
		{
            DataTable dt = GetFromDB(sFilter);
            if (dt != null)
            {
				if (dt.Rows.Count > 0)
	            {
					foreach(DataRow dr in dt.Rows)
					{
						Task t = new Task();
				        t.ID = dr["task_id"].ToString();
				        t.OriginalTaskID = dr["original_task_id"].ToString();
				        t.Name = dr["task_name"].ToString();
						t.Code = dr["task_code"].ToString();
				        t.Version = dr["version"].ToString();
				        t.Status = dr["task_status"].ToString();
						t.IsDefaultVersion = (dr["default_version"].ToString() == "1" ? true : false);
				        t.Description = ((!object.ReferenceEquals(dr["task_desc"], DBNull.Value)) ? dr["task_desc"].ToString() : "");
					
						this.Add(t.ID, t);
					}
				}
            }
		}
		
		static public DataTable AsDataTable(string sFilter)
		{
			DataTable dt = GetFromDB(sFilter);
			if (dt != null)
				return dt;
			
			return null;
		}
		
		static private DataTable GetFromDB(string sFilter)
		{
			dataAccess dc = new dataAccess();
			string sWhereString = "";

            if (sFilter.Length > 0)
            {
                //split on spaces
                int i = 0;
                string[] aSearchTerms = sFilter.Split(' ');
                for (i = 0; i <= aSearchTerms.Length - 1; i++)
                {

                    //if the value is a guid, it's an existing task.
                    //otherwise it's a new task.
                    if (aSearchTerms[i].Length > 0)
                    {
                        sWhereString = " and (a.task_name like '%" + aSearchTerms[i] +
                           "%' or a.task_desc like '%" + aSearchTerms[i] +
                           "%' or a.task_status like '%" + aSearchTerms[i] +
                           "%' or a.task_code like '%" + aSearchTerms[i] + "%' ) ";
                    }
                } 
            }

            string sSQL = "select a.task_id, a.original_task_id, a.task_name, a.task_code, a.task_desc, a.version, a.task_status," +
                " (select count(*) from task where original_task_id = a.original_task_id) as versions" +   
					" from task a  " +
					" where default_version = 1" +
					sWhereString +
					" order by task_code";

			string sErr = "";
            DataTable dt = new DataTable();
            if (!dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
				throw new Exception(sErr); 
			
			return dt;
		}
	}
	
	public class Task
	{
		public string ID;
		public string OriginalTaskID;
		public string Name;
		public string Code;
		public string Version;
		public string Status;
		public string Description;
		public bool DBExists;
		public string OnConflict = "cancel";  //the default behavior for all conflicts is to cancel the operation
		public bool UseConnectorSystem;
		public bool IsDefaultVersion;
		public string ConcurrentInstances;
		public string QueueDepth;
		public XDocument ParameterXDoc;
		
		public int NumberOfApprovedVersions;
		public int NumberOfOtherVersions;
		
		//a task has a dictionary of codeblocks
		public Dictionary<string, Codeblock> Codeblocks = new Dictionary<string, Codeblock>();

		//empty constructor
		public Task()
		{
		}

		//constructor for a new blank task from a few key values
		public Task(string sTaskName, string sTaskCode, string sTaskDesc)
		{
			this.ID = Guid.NewGuid().ToString().ToLower();
			this.Name = sTaskName;
			this.Code = sTaskCode;
			this.Description = sTaskDesc;
			
			this.Version = "1.000";
			this.Status = "Development";
			this.OriginalTaskID = this.ID;
			this.IsDefaultVersion = true;
			
			this.DBExists = _DBExists();
			
			//blank new task always gets a MAIN codeblock
			Codeblock c = new Codeblock("MAIN");
			this.Codeblocks.Add(c.Name, c);
		}

		//Constructor, from an XML document
		public Task FromXML(string sTaskXML, ref string sErr)
		{
			try
			{
				XDocument xTask = XDocument.Parse(sTaskXML);
				if (xTask != null)
				{
					XElement xeTask = xTask.Element("task");
					
					//name is required
					if (xeTask.Attribute("name") == null) {
						sErr = "Task 'name' attribute is required.";
						return null;
					}
						
					this.Name = xeTask.Attribute("name").Value;

					//some of these properties will not be required coming from the XML.
	
					//if there's no ID we create one
					this.ID = (xeTask.Attribute("id") != null ? xeTask.Attribute("id").Value.ToLower() : Guid.NewGuid().ToString().ToLower());
					this.Code = (xeTask.Attribute("code") != null ? xeTask.Attribute("code").Value : "");
					this.Description = (xeTask.Element("description") != null ? xeTask.Element("description").Value : "");
					
					//if there are conflicts when we try to save this Task, what do we do?
					this.OnConflict = (xeTask.Attribute("on_conflict") != null ? xeTask.Attribute("on_conflict").Value : "cancel"); //cancel is the default
	
					//this stuff needs discussion for how it would run on a non-local task
					
					this.Version = (xeTask.Attribute("version") != null ? xeTask.Attribute("version").Value : "1.000");
					this.Status = (xeTask.Attribute("status") != null ? xeTask.Attribute("status").Value : "Development");
					//original id becomes the id if it's omitted from the xml
					this.OriginalTaskID = (xeTask.Attribute("original_task_id") != null ? xeTask.Attribute("original_task_id").Value : this.ID);
					this.IsDefaultVersion = true;
	
					this.ConcurrentInstances = (xeTask.Attribute("concurrent_instances") != null ? xeTask.Attribute("concurrent_instances").Value : "");
					this.QueueDepth = (xeTask.Attribute("queue_depth") != null ? xeTask.Attribute("queue_depth").Value : "");
					//this.UseConnectorSystem = false;
	
					this.DBExists = _DBExists();
					//if it doesn't exist, here's the place where we reset the original_task_id.
					//it doesn't exist, therefore it's new.
					if (!this.DBExists)
						this.OriginalTaskID = this.ID;
					
					//parameters
					if (xeTask.Element("parameters") != null)
					{
						this.ParameterXDoc = XDocument.Parse(xeTask.Element("parameters").ToString(SaveOptions.DisableFormatting));
					}
	
					//now, codeblocks.
					foreach (XElement xCodeblock in xeTask.XPathSelectElements("//codeblocks/codeblock")) {
						if (xCodeblock.Attribute("name") == null) 
						{
							sErr = ("Task.FromXML: All Codeblocks must have the 'name' attribute.");
							return null;
						}
						Codeblock c = new Codeblock(xCodeblock.Attribute("name").Value);
						
						if (c != null)
						{
							//steps.
							foreach (XElement xStep in xCodeblock.XPathSelectElements("steps/step")) {
								Step s = new Step(xStep, c, this);
								
								if (s != null)
								{
									c.Steps.Add(s.ID, s);
								}
							}
	
							this.Codeblocks.Add(c.Name, c);
						}
					}
					
					return this;
				}
				
				return null;
			} catch (Exception ex) {
				sErr = "Task.FromXML: " + ex.Message;
				return null;
			}
		}

		//constructor - from the database by ID
		public Task(string sTaskID, bool IncludeUserSettings, ref string sErr)
		{
			try
            {
				dataAccess dc = new dataAccess();
				
				string sSQL = "select task_id, original_task_id, task_name, task_code, task_status, version, default_version," +
					" task_desc, use_connector_system, concurrent_instances, queue_depth, parameter_xml" +
					" from task" +
					" where task_id = '" + sTaskID + "'";
				
                DataRow dr = null;
                if (!dc.sqlGetDataRow(ref dr, sSQL, ref sErr)) 
					return;

                if (dr != null)
                {
					PopulateTask(dr, IncludeUserSettings, ref sErr);
				}
            }
            catch (Exception ex)
            {
				throw ex;
            }
		}
		public Task(string sOriginalTaskID, string sVersion, ref string sErr)
		{
			try
            {
				dataAccess dc = new dataAccess();
				
				string sVersionClause = "";
				if (string.IsNullOrEmpty(sVersion))
					sVersionClause = " and default_version = 1";
				else
					sVersionClause = " and version = '" + sVersion + "'";
				
				string sSQL = "select task_id, original_task_id, task_name, task_code, task_status, version, default_version," +
					" task_desc, use_connector_system, concurrent_instances, queue_depth, parameter_xml" +
					" from task" +
					" where original_task_id = '" + sOriginalTaskID + "'" +
					sVersionClause;
				
                DataRow dr = null;
                if (!dc.sqlGetDataRow(ref dr, sSQL, ref sErr)) 
					return;

                if (dr != null)
                {
					PopulateTask(dr, false, ref sErr);
				}
            }
            catch (Exception ex)
            {
				throw ex;
            }
		}
		
		private Task PopulateTask(DataRow dr, bool IncludeUserSettings, ref string sErr)
		{	
			try
            {
				dataAccess dc = new dataAccess();
				acUI.acUI ui = new acUI.acUI();
	
				//of course it exists...
				this.DBExists = true;
				
		        this.ID = dr["task_id"].ToString();
		        this.Name = dr["task_name"].ToString();
				this.Code = dr["task_code"].ToString();
		        this.Version = dr["version"].ToString();
		        this.Status = dr["task_status"].ToString();
		        this.OriginalTaskID = dr["original_task_id"].ToString();
		
				this.IsDefaultVersion = (dr["default_version"].ToString() == "1" ? true : false);
		
		        this.Description = ((!object.ReferenceEquals(dr["task_desc"], DBNull.Value)) ? dr["task_desc"].ToString() : "");
		
		        this.ConcurrentInstances = ((!object.ReferenceEquals(dr["concurrent_instances"], DBNull.Value)) ? dr["concurrent_instances"].ToString() : "");
		        this.QueueDepth = ((!object.ReferenceEquals(dr["queue_depth"], DBNull.Value)) ? dr["queue_depth"].ToString() : "");
		
				this.UseConnectorSystem = ((int)dr["use_connector_system"] == 1 ? true : false);
		
				//parameters
				if (!string.IsNullOrEmpty(dr["parameter_xml"].ToString()))
				{
					XDocument xParameters = XDocument.Parse(dr["parameter_xml"].ToString());
					if (xParameters != null) {	
						this.ParameterXDoc = xParameters;
					}
				}				
	
				/*                    
		         * ok, this is important.
		         * there are some rules for the process of 'Approving' a task and other things.
		         * so, we'll need to know some count information
		         */
		        string sSQL = "select count(*) from task" +
		            " where original_task_id = '" + this.OriginalTaskID + "'" +
		            " and task_status = 'Approved'";
		        int iCount = 0;
		        if (!dc.sqlGetSingleInteger(ref iCount, sSQL, ref sErr))
		            return null;
		
				this.NumberOfApprovedVersions = iCount;
		
		        sSQL = "select count(*) from task" +
		            " where original_task_id = '" + this.OriginalTaskID + "'";
				if (!dc.sqlGetSingleInteger(ref iCount, sSQL, ref sErr))
		            return null;
		
				this.NumberOfOtherVersions = iCount;
				
				
				//now, the fun stuff
				//1 get all the codeblocks and populate that dictionary
				//2 then get all the steps... ALL the steps in one sql
				//..... and while spinning them put them in the appropriate codeblock
				
				//GET THE CODEBLOCKS
				sSQL = "select codeblock_name" +
					" from task_codeblock" +
					" where task_id = '" + this.ID + "'" +
					" order by codeblock_name";
				
				DataTable dt = new DataTable();
				if (!dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
					return null;
				
				if (dt.Rows.Count > 0)
				{
					foreach (DataRow drCB in dt.Rows)
					{
						this.Codeblocks.Add(drCB["codeblock_name"].ToString(), new Codeblock(drCB["codeblock_name"].ToString()));
					}
				}
				else
				{
					//uh oh... there are no codeblocks!
					//since all tasks require a MAIN codeblock... if it's missing,
					//we can just repair it right here.
					sSQL = "insert task_codeblock (task_id, codeblock_name) values ('" + this.ID + "', 'MAIN')";
					if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
						return null;
					
					this.Codeblocks.Add("MAIN", new Codeblock("MAIN"));
				}
				
				
				//GET THE STEPS
				//we need the userID to get the user settings in some cases
				if (IncludeUserSettings) {
					string sUserID = ui.GetSessionUserID();
					
					//NOTE: it may seem like sorting will be an issue, but it shouldn't.
					//sorting ALL the steps by their ID here will ensure they get added to their respective 
					// codeblocks in the right order.
					sSQL = "select s.step_id, s.step_order, s.step_desc, s.function_name, s.function_xml, s.commented, s.locked, codeblock_name," +
		                " s.output_parse_type, s.output_row_delimiter, s.output_column_delimiter, s.variable_xml," +
		                " us.visible, us.breakpoint, us.skip, us.button" +
		                " from task_step s" +
		                " left outer join task_step_user_settings us on us.user_id = '" + sUserID + "' and s.step_id = us.step_id" +
		                " where s.task_id = '" + this.ID + "'" +
		                " order by s.step_order";
				}
				else
				{
					sSQL = "select s.step_id, s.step_order, s.step_desc, s.function_name, s.function_xml, s.commented, s.locked, codeblock_name," +
		                " s.output_parse_type, s.output_row_delimiter, s.output_column_delimiter, s.variable_xml," +
						" 0 as visible, 0 as breakpoint, 0 as skip, '' as button" +
						" from task_step s" +
		                " where s.task_id = '" + this.ID + "'" +
		                " order by s.step_order";
				}
		
				DataTable dtSteps = new DataTable();
		        if (!dc.sqlGetDataTable(ref dtSteps, sSQL, ref sErr))
		            sErr += "Database Error: " + sErr;
		
				if (dtSteps.Rows.Count > 0)
		        {
		            foreach (DataRow drSteps in dtSteps.Rows)
		            {
						Step oStep = new Step(drSteps, this);
						if (oStep != null)
						{
							//a 'REAL' codeblock will be in this collection
							// (the codeblock of an embedded step is not a 'real' codeblock, rather a pointer to another step
							if (this.Codeblocks.ContainsKey(oStep.Codeblock))
							{
								this.Codeblocks[oStep.Codeblock].Steps.Add(oStep.ID, oStep);
							}
							else
							{
								//so, what do we do if we found a step that's not in a 'real' codeblock?
								//well, the gui will take care of drawing those embedded steps...
								
								//but we have a problem with export, version up, etc.
								
								//these steps can't be orphans!
								//so, we'll go ahead and create codeblocks for them.
								//this is terrible, but part of the problem with this embedded stuff.
								//we'll tweak the gui so GUID named codeblocks don't show.
								this.Codeblocks.Add(oStep.Codeblock, new Codeblock(oStep.Codeblock));
								this.Codeblocks[oStep.Codeblock].Steps.Add(oStep.ID, oStep);
	
								//maybe one day we'll do the full recusrive loading of all embedded steps here
								// but not today... it's a big deal and we need to let these changes settle down first.
							}
						}
					}
		        }
			
				return this;
            }
            catch (Exception ex)
            {
				throw ex;
            }
		}

		private bool _DBExists()
		{	
			try
			{
				dataAccess dc = new dataAccess();
				string sErr = "";
				
				//task_id is the PK, and task_name+version is a unique index.
				//so, we check the conflict property, and act accordingly
				string sSQL = "select task_id, original_task_id from task" +
					" where (task_name = '" + this.Name + "' and version = '" + this.Version + "')" +
					" or task_id = '" + this.ID + "'";
				
				DataRow dr = null;
				if (!dc.sqlGetDataRow(ref dr, sSQL, ref sErr))
				{
					throw new Exception("Task Object: Unable to check for existing Name/Version or ID. " + sErr);
				}
				
				if (dr != null)
				{
					if (!string.IsNullOrEmpty(dr["task_id"].ToString())) {
						//PAY ATTENTION! 
						//if the task exists... it might have been by name/version, so...
						//we're setting the ids to the same as the database so it's more accurate.
						
						this.ID = dr["task_id"].ToString();
						this.OriginalTaskID = dr["original_task_id"].ToString();
						return true;
					}
				}
					
				return false;
            }
            catch (Exception ex)
            {
				throw ex;
            }
		}
		//what's the max version allowed for this task?
		public string MaxVersion()
		{
            try
            {
				dataAccess dc = new dataAccess();
				//if the task is in the db, get it's max
				//if it's not, the max is 1.000
                string sMax = "";

				if (this.DBExists) {
					string sErr = "";
					string sSQL = "select max(version) as maxversion from task " +
						" where original_task_id = '" + this.OriginalTaskID + "'";
					if (!dc.sqlGetSingleString(ref sMax, sSQL, ref sErr)) throw new Exception(sErr);
				}

                return sMax;
            }
            catch (Exception ex)
            {
                throw ex;
            }
		}
		
		//this will increment the major version - does NOT save the task.
		public void IncrementMajorVersion()
		{
            try
            {
				string sMaxVer = MaxVersion();
				this.Version = String.Format("{0:0.000}", Math.Round((Convert.ToDouble(sMaxVer) + .5), MidpointRounding.AwayFromZero));
            }
            catch (Exception ex)
            {
                throw ex;
            }
		}
		//this will increment the minor version - does NOT save the task.
		public void IncrementMinorVersion()
		{
            try
            {
				string sMaxVer = MaxVersion();
				this.Version = String.Format("{0:0.000}", (Convert.ToDouble(sMaxVer) + .001));
            }
            catch (Exception ex)
            {
                throw ex;
            }
		}
		
		//Try to save the existing object, resolving conflicts as directed.
		public bool DBSave(ref string sErr, dataAccess.acTransaction oTrans)
		{
			try
			{
				acUI.acUI ui = new acUI.acUI();
				
				bool bLocalTransaction = true;
				//if we weren't given a transaction, create one
				if (oTrans != null)
					bLocalTransaction = false;
				else
					oTrans = new dataAccess.acTransaction(ref sErr);
				
				if (string.IsNullOrEmpty(this.Name) || string.IsNullOrEmpty(this.ID)) 
				{
					sErr = "ID and Name are required Task properties.";
					if (bLocalTransaction) oTrans.RollBack();
					return false;
				}
				
				if (this.DBExists)
				{
					//uh oh... this task exists.  unless told to do so, we stop here.
					if (this.OnConflict == "cancel") {
						sErr = "Another Task with that ID or Name/Version exists." +
							"[" + this.ID + "/" + this.Name + "/" + this.Version + "]" +
								"  Conflict directive set to 'cancel'. (Default is 'cancel' if omitted.)";
						if (bLocalTransaction) oTrans.RollBack();
						return false;
					}
					else {
						//ok, what are we supposed to do then?
						switch (this.OnConflict) {
						case "replace":
							//whack it all so we can re-insert
							//but by name or ID?  which was the conflict?
							
							//no worries! the _DBExists function called when we created the object
							//will have resolved any name/id issues.
							
							//if the ID existed it doesn't matter, we'll be plowing it anyway.
							//by "plow" I mean drop and recreate the codeblocks and steps... the task row will be UPDATED
							
		                    oTrans.Command.CommandText = "delete from task_step_user_settings" +
		                        " where step_id in" +
		                        " (select step_id from task_step where task_id = '" + this.ID + "')";
		                    if (!oTrans.ExecUpdate(ref sErr))
		                        return false;
		
		                    oTrans.Command.CommandText = "delete from task_step where task_id = '" + this.ID + "'";
		                    if (!oTrans.ExecUpdate(ref sErr))
		                        return false;
		
		                    oTrans.Command.CommandText = "delete from task_codeblock where task_id = '" + this.ID + "'";
		                    if (!oTrans.ExecUpdate(ref sErr))
		                        return false;
		
							//update the task row
		                    oTrans.Command.CommandText = "update task set" +
								" version = '" + this.Version + "'," +
								" task_name = '" + ui.TickSlash(this.Name) + "'," +
								" task_code = '" + ui.TickSlash(this.Code) + "'," +
								" task_desc = '" + ui.TickSlash(this.Description) + "'," +
								" task_status = '" + this.Status + "'," +
								" default_version = '" + (this.IsDefaultVersion ? 1 : 0) + "'," +
								" concurrent_instances = '" + this.ConcurrentInstances + "'," +
								" queue_depth = '" + this.QueueDepth + "'," +
								" created_dt = now()," +
								" parameter_xml = " + (this.ParameterXDoc != null ? "'" + ui.TickSlash(this.ParameterXDoc.ToString(SaveOptions.DisableFormatting)) + "'" : "null") +
								" where task_id = '" + this.ID + "'";
		                    if (!oTrans.ExecUpdate(ref sErr))
		                        return false;
		
		                    //need to update this to work without session
							//ui.WriteObjectChangeLog(Globals.acObjectTypes.Task, this.ID, this.Name, "Task Updated");

							break;
						case "minor":
							this.IncrementMinorVersion();
							
							this.DBExists = false;
							this.ID = ui.NewGUID();
							this.IsDefaultVersion = false;

							//insert the new version
							oTrans.Command.CommandText = "insert task" +
								" (task_id, original_task_id, version, default_version," +
									" task_name, task_code, task_desc, task_status, created_dt)" +
									" values " +
									" ('" + this.ID + "'," +
									" '" + this.OriginalTaskID + "'," +
									" " + this.Version + "," +
									" " + (this.IsDefaultVersion ? 1 : 0) + "," +
									" '" + ui.TickSlash(this.Name) + "'," +
									" '" + ui.TickSlash(this.Code) + "'," +
									" '" + ui.TickSlash(this.Description) + "'," +
									" '" + this.Status + "'," +
									" now())";
							if (!oTrans.ExecUpdate(ref sErr))
								return false;

							break;
						case "major":
							this.IncrementMajorVersion();
											
							this.DBExists = false;
							this.ID = ui.NewGUID();
							this.IsDefaultVersion = false;

							//insert the new version
							oTrans.Command.CommandText = "insert task" +
								" (task_id, original_task_id, version, default_version," +
									" task_name, task_code, task_desc, task_status, created_dt)" +
									" values " +
									" ('" + this.ID + "'," +
									" '" + this.OriginalTaskID + "'," +
									" " + this.Version + "," +
									" " + (this.IsDefaultVersion ? 1 : 0) + "," +
									" '" + ui.TickSlash(this.Name) + "'," +
									" '" + ui.TickSlash(this.Code) + "'," +
									" '" + ui.TickSlash(this.Description) + "'," +
									" '" + this.Status + "'," +
									" now())";
							if (!oTrans.ExecUpdate(ref sErr))
								return false;

							break;
						default:
							//there is no default action... if the on_conflict didn't match we have a problem... bail.
							sErr = "There is an ID or Name/Version conflict, and the on_conflict directive isn't a valid option. (replace/major/minor/cancel)";
							return false;
						}
					}
				}
				else 
				{
					//the default action is to ADD the new task row... nothing
					oTrans.Command.CommandText = "insert task" +
						" (task_id, original_task_id, version, default_version," +
							" task_name, task_code, task_desc, task_status, created_dt)" +
							" values " +
							" ('" + this.ID + "'," +
							"'" + this.OriginalTaskID + "'," +
							" " + this.Version + "," +
							" 1," +
							" '" + ui.TickSlash(this.Name) + "'," +
							" '" + ui.TickSlash(this.Code) + "'," +
							" '" + ui.TickSlash(this.Description) + "'," +
							" '" + this.Status + "'," +
							" now())";
					if (!oTrans.ExecUpdate(ref sErr))
						return false;
					
					// add security log
					//need to update this to work without session
							//ui.WriteObjectAddLog(Globals.acObjectTypes.Task, this.ID, this.Name, "");
				}
			
				//by the time we get here, there should for sure be a task row, either new or updated.				
				//now, codeblocks
				foreach (Codeblock c in this.Codeblocks.Values) {
					//PAY ATTENTION to crazy stuff here.
					//for exportability, embedded steps are held in codeblocks that don't really exist in the database
					// they are created on the task object when it's created from the db or xml.
					//BUT, when actually saving it, we don't wanna save these dummy codeblocks.
					//(having real dummy codeblocks in the db would freak out the command engine)
					
					//so ... if the codeblock name is a guid, we:
					//a) DO NOT insert it
					//b) any steps inside it are set to step_order=-1
					bool bIsBogusCodeblock = (ui.IsGUID(c.Name));
					
					if (!bIsBogusCodeblock)
					{
						oTrans.Command.CommandText = "insert task_codeblock (task_id, codeblock_name)" +
							" values ('" + this.ID + "', '" + c.Name + "')";
						if (!oTrans.ExecUpdate(ref sErr))
							return false;
					}
					
					//and steps
					int iStepOrder = 1;
					foreach (Step s in c.Steps.Values) {
						iStepOrder = (bIsBogusCodeblock ? -1 : iStepOrder);
						
						oTrans.Command.CommandText = "insert into task_step (step_id, task_id, codeblock_name, step_order," +
							" commented, locked, output_parse_type, output_row_delimiter, output_column_delimiter," +
								" function_name, function_xml)" +
								" values (" +
								"'" + s.ID + "'," +
								"'" + s.Task.ID + "'," +
								(string.IsNullOrEmpty(s.Codeblock) ? "NULL" : "'" + s.Codeblock + "'") + "," +
								iStepOrder.ToString() + "," +
								"0,0," + 
								s.OutputParseType.ToString() + "," + 
								s.OutputRowDelimiter.ToString() + "," + 
								s.OutputColumnDelimiter.ToString() + "," +
								"'" + s.FunctionName + "'," +
								"'" + ui.TickSlash(s.FunctionXML) + "'" +
								")";
						if (!oTrans.ExecUpdate(ref sErr))
							return false;
						
						iStepOrder++;
					}
				}
				
				if (bLocalTransaction) oTrans.Commit();
			
			}
			catch (Exception ex)
			{
				sErr = "Error updating the DB." + ex.Message;
				return false;
			}
			
			return true;
		}

		public string Copy(int iMode, string sNewTaskName, string sNewTaskCode)
        {
			//iMode 0=new task, 1=new major version, 2=new minor version
			try
			{
					
				//NOTE: this routine is not very object-aware.  It works and was copied in here
				//so it can live with other relevant code.
				//may update it later to be more object friendly
				acUI.acUI ui = new acUI.acUI();
				dataAccess dc = new dataAccess();
				
	            string sErr = "";
	            string sSQL = "";
	
	            string sNewTaskID = ui.NewGUID();
	
				int iIsDefault = 0;
	            string sTaskName = "";
	            string sOTID = "";
	
	            //do it all in a transaction
	            dataAccess.acTransaction oTrans = new dataAccess.acTransaction(ref sErr);
	
	            //figure out the new name and selected version
	            sTaskName = this.Name;
	            sOTID = this.OriginalTaskID;
	
	            //figure out the new version
	            switch (iMode)
	            {
	                case 0:
			            //figure out the new name and selected version
						int iExists = 0;
						oTrans.Command.CommandText = "select count(*) from task where task_name = '" + sNewTaskName + "'";
			            if (!oTrans.ExecGetSingleInteger(ref iExists, ref sErr))
			                throw new Exception("Unable to check name conflicts for  [" + sNewTaskName + "]." + sErr);
		
						sTaskName = (iExists > 0 ? sNewTaskName + " (" + DateTime.Now.ToString() + ")" : sNewTaskName);
	                    iIsDefault = 1;
	                    this.Version = "1.000";
	                    sOTID = sNewTaskID;
	
	                    break;
	                case 1:
	                    this.IncrementMajorVersion();
	                    break;
	                case 2:
	                    this.IncrementMinorVersion();
	                    break;
	                default: //a iMode is required
	                    throw new Exception("A mode required for this copy operation." + sErr);
	            }
	
	            //if we are versioning, AND there are not yet any 'Approved' versions,
	            //we set this new version to be the default
	            //(that way it's the one that you get taken to when you pick it from a list)
	            if (iMode > 0)
	            {
	                sSQL = "select case when count(*) = 0 then 1 else 0 end" +
	                    " from task where original_task_id = '" + sOTID + "'" +
	                    " and task_status = 'Approved'";
	                dc.sqlGetSingleInteger(ref iIsDefault, sSQL, ref sErr);
	                if (sErr != "")
	                {
	                    oTrans.RollBack();
	                    throw new Exception(sErr);
	                }
	            }
	
	            //string sTaskName = (iExists > 0 ? sNewTaskName + " (" + DateTime.Now.ToString() + ")" : sNewTaskName);
	
	
				//drop the temp tables.
				oTrans.Command.CommandText = "drop temporary table if exists _copy_task";
	            if (!oTrans.ExecUpdate(ref sErr))
	                throw new Exception(sErr);
	
	            oTrans.Command.CommandText = "drop temporary table if exists _step_ids";
	            if (!oTrans.ExecUpdate(ref sErr))
	                throw new Exception(sErr);
	
	            oTrans.Command.CommandText = "drop temporary table if exists _copy_task_codeblock";
	            if (!oTrans.ExecUpdate(ref sErr))
	                throw new Exception(sErr);
	
	            oTrans.Command.CommandText = "drop temporary table if exists _copy_task_step";
	            if (!oTrans.ExecUpdate(ref sErr))
	                throw new Exception(sErr);
	
				//start copying
	            oTrans.Command.CommandText = "create temporary table _copy_task" +
	                " select * from task where task_id = '" + this.ID + "'";
	            if (!oTrans.ExecUpdate(ref sErr))
	                throw new Exception(sErr);
	
	            //update the task_id
	            oTrans.Command.CommandText = "update _copy_task set" +
	                " task_id = '" + sNewTaskID + "'," +
	                " original_task_id = '" + sOTID + "'," +
	                " version = '" + this.Version + "'," +
	                " task_name = '" + sTaskName + "'," +
	                " task_code = '" + sNewTaskCode + "'," +
	                " default_version = " + iIsDefault.ToString() + "," +
	                " task_status = 'Development'," +
	                " created_dt = now()";
	            if (!oTrans.ExecUpdate(ref sErr))
	                throw new Exception(sErr);
	
	            //codeblocks
	            oTrans.Command.CommandText = "create temporary table _copy_task_codeblock" +
	                " select '" + sNewTaskID + "' as task_id, codeblock_name" +
	                " from task_codeblock where task_id = '" + this.ID + "'";
	            if (!oTrans.ExecUpdate(ref sErr))
	                throw new Exception(sErr);
	
	
	            //USING TEMPORARY TABLES... need a place to hold step ids while we manipulate them
	            oTrans.Command.CommandText = "create temporary table _step_ids" +
	                " select distinct step_id, uuid() as newstep_id" +
	                " from task_step where task_id = '" + this.ID + "'";
	            if (!oTrans.ExecUpdate(ref sErr))
	                throw new Exception(sErr);
	
	            //steps temp table
	            oTrans.Command.CommandText = "create temporary table _copy_task_step" +
	                " select step_id, '" + sNewTaskID + "' as task_id, codeblock_name, step_order, commented," +
	                " locked, function_name, function_xml, step_desc, output_parse_type, output_row_delimiter," +
	                " output_column_delimiter, variable_xml" +
	                " from task_step where task_id = '" + this.ID + "'";
	            if (!oTrans.ExecUpdate(ref sErr))
	                throw new Exception(sErr);
	
	            //update the step id
	            oTrans.Command.CommandText = "update _copy_task_step a, _step_ids b" +
	                " set a.step_id = b.newstep_id" +
	                " where a.step_id = b.step_id";
	            if (!oTrans.ExecUpdate(ref sErr))
	                throw new Exception(sErr);
	
	            //update steps with codeblocks that reference a step (embedded steps)
	            oTrans.Command.CommandText = "update _copy_task_step a, _step_ids b" +
	                " set a.codeblock_name = b.newstep_id" +
	                " where b.step_id = a.codeblock_name";
	            if (!oTrans.ExecUpdate(ref sErr))
	                throw new Exception(sErr);
	
	
	            //spin the steps and update any embedded step id's in the commands
	            oTrans.Command.CommandText = "select step_id, newstep_id from _step_ids";
	            DataTable dtStepIDs = new DataTable();
	            if (!oTrans.ExecGetDataTable(ref dtStepIDs, ref sErr))
	                throw new Exception("Unable to get step ids." + sErr);
	
	            foreach (DataRow drStepIDs in dtStepIDs.Rows)
	            {
	                oTrans.Command.CommandText = "update _copy_task_step" +
	                    " set function_xml = replace(lower(function_xml), '" + drStepIDs["step_id"].ToString().ToLower() + "', '" + drStepIDs["newstep_id"].ToString() + "')" +
	                    " where function_name in ('if','loop','exists','while')";
	                if (!oTrans.ExecUpdate(ref sErr))
	                    throw new Exception(sErr);
	            }
	
	
	            //finally, put the temp steps table in the real steps table
	            oTrans.Command.CommandText = "insert into task select * from _copy_task";
	            if (!oTrans.ExecUpdate(ref sErr))
	                throw new Exception(sErr);
	
	            oTrans.Command.CommandText = "insert into task_codeblock select * from _copy_task_codeblock";
	            if (!oTrans.ExecUpdate(ref sErr))
	                throw new Exception(sErr);
	
	            oTrans.Command.CommandText = "insert into task_step select * from _copy_task_step";
	            if (!oTrans.ExecUpdate(ref sErr))
	                throw new Exception(sErr);
	
	
				
	            //finally, if we versioned up and we set this one as the new default_version,
	            //we need to unset the other row
	            if (iMode > 0 && iIsDefault == 1)
	            {
	                oTrans.Command.CommandText = "update task" +
	                    " set default_version = 0" +
	                    " where original_task_id = '" + sOTID + "'" +
	                    " and task_id <> '" + sNewTaskID + "'";
	                if (!oTrans.ExecUpdate(ref sErr))
	                    throw new Exception(sErr);
	            }
	
	
				oTrans.Commit();
	
	            return sNewTaskID;
            }
            catch (Exception ex)
            {
				throw ex;
            }
        }

		
		//INSTANCE METHOD - returns the object as XML
		public XElement AsXElement()
		{
			try
			{
				XElement xTask = new XElement("task");
			
				//xTask.SetAttributeValue("id", this.ID);
				xTask.SetAttributeValue("original_task_id", this.OriginalTaskID);
				xTask.SetAttributeValue("name", this.Name);
				xTask.SetAttributeValue("code", this.Code);
				xTask.SetAttributeValue("status", this.Status);
				xTask.SetAttributeValue("version", this.Version);
				xTask.SetAttributeValue("concurrent_instances", this.ConcurrentInstances);
				xTask.SetAttributeValue("queue_depth", this.QueueDepth);
				xTask.SetAttributeValue("on_conflict", "cancel");
				
				xTask.SetElementValue("description", this.Description);
				
				
				//codeblocks
				xTask.Add(new XElement("codeblocks"));
				XElement xCodeblocks = xTask.Element("codeblocks");
				
				foreach (Codeblock c in this.Codeblocks.Values) {
					XElement xCodeblock = new XElement("codeblock");
					xCodeblock.SetAttributeValue("name", c.Name);
					
					//steps
					xCodeblock.Add(new XElement("steps"));
					XElement xSteps = xCodeblock.Element("steps");
					
					foreach (Step s in c.Steps.Values) {
						string sStepXML = s.AsXML();
						if (!string.IsNullOrEmpty(sStepXML))
						{
							XElement xStep = XElement.Parse(sStepXML);
							if (xStep != null) {	
								xSteps.Add(xStep);
							}
						}
					}
					
					xCodeblocks.Add(xCodeblock);
				}
				
				//parameters, if defined
				if (this.ParameterXDoc != null)
					if (this.ParameterXDoc.Root != null)
						xTask.Add(this.ParameterXDoc.Root);
	
				return xTask;
            }
            catch (Exception ex)
            {
				throw ex;
            }
		}
		public string AsXML()
		{
			XElement xe = this.AsXElement();
			if (xe != null)
				return xe.ToString();
			else 
				return null;
		}

	}
	public class StepUserSettings
	{
		public bool Visible = true;
		public bool Breakpoint= false;
		public bool Skip = false;
		public string Button = "";

		//constructor
		public StepUserSettings()
		{
		}
	}
#endregion
}