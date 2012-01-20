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
	
	#region "Ecostemplates"
	//Ecotemplates contains a DataTable
	//more efficient to read from the DB as a DataTable than to loop and create a dictionary.
	//if you want a dictionary, that's an instance method.
	public class Ecotemplates
	{
		public DataTable DataTable = new DataTable();
		
		public Ecotemplates(string sFilter, ref string sErr)
		{
			//buids a list of ecotemplates from the db, with the optional filter
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
		public Dictionary<string, Ecotemplate> AsDictionary()
		{
			//spin "this" and turn it into a dictionary
			Dictionary<string, Ecotemplate> et = new Dictionary<string, Ecotemplate>();
			
			foreach (DataRow dr in this.DataTable.Rows)
			{
				
			}
			
			
			return et;
		}
	}
	public class Ecotemplate 
	{
		acUI.acUI ui = new acUI.acUI();
		
		public string ID;
		public string Name;
		public string Description;
		public string StormFileSource;
		public string StormFile;
		public Dictionary<string, EcotemplateAction> Actions = new Dictionary<string, EcotemplateAction>();
		
		//an empty constructor
		public Ecotemplate()
		{
			this.ID = ui.NewGUID();
		}
		
		//aname and desc
		public Ecotemplate(string sName, string sDesription)
		{
			this.ID = ui.NewGUID();
			this.Name = sName;
			this.Description = sDesription;
		}
		
		//the default constructor, given an ID loads it up.
		public Ecotemplate(string sEcotemplateID)
		{
			if (string.IsNullOrEmpty(sEcotemplateID))
				throw new Exception("Error building Ecotemplate object: ID is required.");	
			
            dataAccess dc = new dataAccess();
			
			string sErr = "";
            string sSQL = "select ecotemplate_id, ecotemplate_name, ecotemplate_desc" +
                " from ecotemplate" +
                " where ecotemplate_id = '" + sEcotemplateID + "'";

            DataRow dr = null;
            if (dc.sqlGetDataRow(ref dr, sSQL, ref sErr))
            {
                if (dr != null)
                {
					ID = dr["ecotemplate_id"].ToString();;
					Name = dr["ecotemplate_name"].ToString();
					Description = (object.ReferenceEquals(dr["ecotemplate_desc"], DBNull.Value) ? "" : dr["ecotemplate_desc"].ToString());
					
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
		
		//makes a copy of this template in the database
		public bool DBCopy(string sNewName, ref string sErr)
		{
            dataAccess dc = new dataAccess();
			
			//1) create a new template in the db
			//2) batch copy all the steps from the old template to the new
			
			//1) 
			Ecotemplate et = new Ecotemplate(sNewName, this.Description);
			if (et != null)
			{
				//2
				string sSQL = "insert into ecotemplate_action" + 
					" select uuid() as action_id, '" + et.ID + "', action_name, action_desc, category, original_task_id, task_version, parameter_defaults, action_icon" +
					" from ecotemplate_action" +
					" where ecotemplate_id = '" + this.ID + "'";
				
				if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
					throw new Exception(sErr);
			
				return true;
			}
			
			return false;
		}

		//saves this template as a new template in the db
		public bool DBCreateNew(ref string sErr)
		{
            dataAccess dc = new dataAccess();
			string sSQL = "";
			
			try
			{
				sSQL = "insert into ecotemplate (ecotemplate_id, ecotemplate_name, ecotemplate_desc)" +
					" values ('" + this.ID + "'," +
						" '" + this.Name + "'," +
						(string.IsNullOrEmpty(this.Description) ? " null" : " '" + this.Description + "'") + ")";
				
				if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
				{
					if (sErr == "key_violation")
					{
						sErr = "An Ecotemplate with that name already exists.  Please select another name.";
						return false;
					}
					else 
						throw new Exception(sErr);
				}
				
				ui.WriteObjectAddLog(acObjectTypes.Ecosystem, this.ID, this.Name, "Ecotemplate created.");
				
				//yay!
				return true;
			}
			catch (Exception ex)
			{
				throw new Exception(ex.Message);
			}		
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
		
		//static method, given an ID.
		static public EcotemplateAction GetFromID(string sActionID)
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
		
		//another constructor, takes a datarow from ecotemplate_action and creates it from that
		public EcotemplateAction(DataRow dr, Ecotemplate parent)
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

	}
#endregion
	
	#region "Database Settings"
	public class DatabaseSettings
    {

        private static int iConnectionTimeout = 90;
        public static int ConnectionTimeout
        {
            get { return iConnectionTimeout; }
            set { iConnectionTimeout = value; }
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
								
								Cloud c = new Cloud(pv, false, xCloud.Attribute("id").Value, xCloud.Attribute("name").Value, xCloud.Attribute("api_url").Value, xCloud.Attribute("api_protocol").Value);
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
									Cloud c = new Cloud(pv, true, dr["cloud_id"].ToString(), dr["cloud_name"].ToString(), dr["api_url"].ToString(), dr["api_protocol"].ToString());
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
								if (xProperty.Attribute("xpath") == null) 
									throw new Exception("Cloud Providers XML: All Object Type Properties must have the 'xpath' attribute.");
								
								CloudObjectTypeProperty cotp = new CloudObjectTypeProperty(cot);
								cotp.Name = xProperty.Attribute("name").Value;
								cotp.XPath = xProperty.Attribute("xpath").Value;
								
								cotp.Label = (xProperty.Attribute("label") == null ? "" : xProperty.Attribute("label").Value);
								cotp.SortOrder = (xProperty.Attribute("sort_order") == null ? "" : xProperty.Attribute("sort_order").Value);
								cotp.IsID = (xProperty.Attribute("id_field") == null ? false : 
									(xProperty.Attribute("id_field").Value == "1" ? true : false));
								cotp.HasIcon = (xProperty.Attribute("has_icon") == null ? false : 
									(xProperty.Attribute("has_icon").Value == "1" ? true : false));
								cotp.ShortList = (xProperty.Attribute("short_list") == null ? false : 
									(xProperty.Attribute("short_list").Value == "1" ? true : false));
								
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
            acUI.acUI ui = new acUI.acUI();

			//get the provider record from the CloudProviders object in the session
			CloudProviders cp = ui.GetCloudProviders();
			if (cp == null) {
				throw new Exception("Error building Provider object: Unable to GetCloudProviders.");	
			}

			return cp[sProvider];
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
		public DataTable GetAllCloudsAsDataTable()
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
				
		//INSTANCE METHOD - returns the object as JSON
		public string AsJSON()
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

		public void RefreshClouds() {
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
					Cloud c = new Cloud(this, true, dr["cloud_id"].ToString(), dr["cloud_name"].ToString(), dr["api_url"].ToString(), dr["api_protocol"].ToString());
					this.Clouds.Add(c.ID, c);
				}
			}
			else 
			{
				throw new Exception("Error building Cloud object: " + sErr);	
			}
			
			return;
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
            if (string.IsNullOrEmpty(this.APICall) || string.IsNullOrEmpty(this.XMLRecordXPath) || string.IsNullOrEmpty(this.ID))
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

		//constructor
		public CloudObjectTypeProperty(CloudObjectType parent)
		{
			this.ParentObjectType = parent;
		}
		
    }
	
	public class Cloud
    {
        public string ID;
		public string Name;
		public Provider Provider;
        public string APIUrl;
		public string APIProtocol;
		public bool IsUserDefined;
		
		//the default constructor
		public Cloud(string sCloudID)
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
						Provider = c.Provider;
						return;
					}				
				}
			}
			
			//well, if we got here we have a problem... the ID provided wasn't found anywhere.
			//this should never happen, so bark about it.
			throw new Exception("Unable to build Cloud object. Either no Clouds are defined, or no Cloud with ID [" + sCloudID + "] could be found.");	

        }

		//an override constructor (manual creation)
		public Cloud(Provider p, bool bUserDefined, string sID, string sName, string sAPIUrl, string sAPIProtocol) {
			IsUserDefined = bUserDefined;
			ID = sID;
			Name = sName;
			APIUrl = sAPIUrl;
			APIProtocol = sAPIProtocol;
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
			StringBuilder sb = new StringBuilder();
			
			sb.Append("{");
			sb.AppendFormat("\"{0}\" : \"{1}\",", "ID", this.ID);
			sb.AppendFormat("\"{0}\" : \"{1}\",", "Name", this.Name);
			sb.AppendFormat("\"{0}\" : \"{1}\",", "Provider", this.Provider.Name);
			sb.AppendFormat("\"{0}\" : \"{1}\",", "APIUrl", this.APIUrl);
			sb.AppendFormat("\"{0}\" : \"{1}\"", "APIProtocol", this.APIProtocol);
			sb.Append("}");
			
			return sb.ToString();
		}
		
		
		//CLASS METHOD
		//creates this Cloud as a new record in the db
		//and returns the object
		static public Cloud DBCreateNew(string sCloudName, string sProvider, string sAPIUrl, string sAPIProtocol, ref string sErr)
		{
            dataAccess dc = new dataAccess();
            acUI.acUI ui = new acUI.acUI();
			string sSQL = "";
			
			try
			{
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
			acUI.acUI ui = new acUI.acUI();
            dataAccess dc = new dataAccess();
			string sSQL = "";
			
			try
			{
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
				
				ui.WriteObjectChangeLog(Globals.acObjectTypes.Cloud, this.ID, this.Name, sOriginalName, this.Name);

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
		
		//CLASS METHOD
		//creates this Cloud as a new record in the db
		//and returns the object
		static public CloudAccount DBCreateNew(string sAccountName, string sAccountNumber, string sProvider, 
		                                       string sLoginID, string sLoginPassword, string sIsDefault, ref string sErr)
		{
            dataAccess dc = new dataAccess();
            acUI.acUI ui = new acUI.acUI();

			try
			{
				dataAccess.acTransaction oTrans = new dataAccess.acTransaction(ref sErr);
				
				//if there are no rows yet, make this one the default even if the box isn't checked.
				if (sIsDefault == "0")
				{
					int iExists = -1;
					
					//as a reminder, we were doing this because of a random screws mysql connection error.
					string sSQL = "select count(*) as cnt from cloud_account";
                	if (!dc.sqlGetSingleInteger(ref iExists, sSQL, ref sErr))
					{
						System.Threading.Thread.Sleep(300);
						if (!dc.sqlGetSingleInteger(ref iExists, sSQL, ref sErr))
						{
							System.Threading.Thread.Sleep(300);
							if (!dc.sqlGetSingleInteger(ref iExists, sSQL, ref sErr))
								throw new Exception("Unable to count Cloud Accounts: " + sErr);
						}
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
			acUI.acUI ui = new acUI.acUI();
            dataAccess dc = new dataAccess();
			string sSQL = "";
			
			try
			{
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
				
				ui.WriteObjectChangeLog(Globals.acObjectTypes.CloudAccount, this.ID, this.Name, sOriginalName, this.Name);

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
		
		//class method to load from the disk
		static public FunctionCategories Load(string sFileName)
		{
			XDocument xCategories = XDocument.Load(sFileName);
			if (xCategories == null) {
				//crash... we can't do anything if the XML is busted
				throw new Exception ("Error: (FunctionCategories Class) Invalid or missing Task Command XML.");
			} else {
				
				FunctionCategories fc = new FunctionCategories();
				
				foreach (XElement xCategory in xCategories.XPathSelectElements("//categories/category"))
				{
					//not crashing... just skipping
					if (xCategory.Attribute ("name") == null) 
						continue;
					
					//not crashing... just skipping
					if (string.IsNullOrEmpty(xCategory.Attribute("name").Value)) 
						continue;
					
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
				
					fc.Add(cat.Name, cat);
				}
				return fc;
			}
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
			acUI.acUI ui = new acUI.acUI();
			Function fn = ui.GetTaskFunction(sFunctionName);
			if (fn != null)
				return fn;
			
			return null;
		}

		//class method - get Function from step_id
		public static Function GetFunctionForStep(string sStepID)
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

	}
	
	//ClipboardSteps is a dictionary of clipboardStep objects
	public class ClipboardSteps : Dictionary<string, ClipboardStep>
	{
		public ClipboardSteps(string sUserID)
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
		public StepUserSettings UserSettings; //Step has user settings from the db
		
		//constructor from an xElement
		public Step(XElement xStep, Codeblock c, Task t)
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
					this.FunctionXML = this.FunctionXDoc.ToString(SaveOptions.DisableFormatting);
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
			
			//well for now this method is for the API and xml based task creation, not the gui.
			//so, the full function object is not required.
			this.FunctionName = this.FunctionXDoc.Element("function").Attribute("command_type").Value;
		}
		
		//constructor from a DataRow
		public Step(DataRow dr, Task oTask)
		{
			PopulateStep(dr, oTask);
		}
		private Step PopulateStep(DataRow dr, Task oTask)
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
			
			this.UserSettings = new StepUserSettings();
			this.UserSettings.Visible = (string.IsNullOrEmpty(dr["visible"].ToString()) ? true : (dr["visible"].ToString() == "0" ? false : true));
			this.UserSettings.Breakpoint = (string.IsNullOrEmpty(dr["breakpoint"].ToString()) ? true : (dr["breakpoint"].ToString() == "0" ? false : true));
			this.UserSettings.Skip = (string.IsNullOrEmpty(dr["skip"].ToString()) ? true : (dr["skip"].ToString() == "0" ? false : true));
			
			this.UserSettings.Button = (string.IsNullOrEmpty(dr["button"].ToString()) ? "" : dr["button"].ToString());
			
			
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
		
		//constructor from a step_id AND user_id ... will include settings
		public Step(string sStepID, string sUserID, ref string sErr)
		{
			dataAccess dc = new dataAccess();

            string sSQL = "select t.task_name, t.version," +
                " s.step_id, s.task_id, s.step_order, s.codeblock_name, s.step_desc, s.function_name, s.function_xml, s.commented, s.locked," +
                " s.output_parse_type, s.output_row_delimiter, s.output_column_delimiter, s.variable_xml," +
                " us.visible, us.breakpoint, us.skip, us.button" +
                " from task_step s" +
                " join task t on s.task_id = t.task_id" +
                " left outer join task_step_user_settings us on us.user_id = '" + sUserID + "' and s.step_id = us.step_id" +
                " where s.step_id = '" + sStepID + "' limit 1";

            DataTable dt = new DataTable();
            if (!dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
            {
                throw new Exception("Unable to get data row for step_id [" + sStepID + "].<br />" + sErr);
            }

			if (dt.Rows.Count == 1)
            {
				PopulateStep(dt.Rows[0], null);
			}
		}

		//constructor from a clipboard step!
		public Step(ClipboardStep cs)
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
			
			//blank new task always gets a MAIN codeblock
			Codeblock c = new Codeblock("MAIN");
			this.Codeblocks.Add(c.Name, c);
		}

		//Constructor, from an XML document
		public Task(string sTaskXML)
		{
			XDocument xTask = XDocument.Parse(sTaskXML);
			if (xTask != null)
			{
				XElement xeTask = xTask.Element("task");
				
				//some of these properties will not be required coming from the XML.
				
				//if there's no ID we create one
				this.ID = (xeTask.Attribute("id") != null ? xeTask.Attribute("id").Value.ToLower() : Guid.NewGuid().ToString().ToLower());
				this.Name = xeTask.Attribute("name").Value;
				this.Code = xeTask.Attribute("code").Value;
				this.Description = xeTask.Element("description").Value;
				
				//if there are conflicts when we try to save this Task, what do we do?
				this.OnConflict = (xeTask.Attribute("on_conflict") != null ? xeTask.Attribute("on_conflict").Value : "cancel"); //cancel is the default

				//this stuff needs discussion for how it would run on a non-local task
				
				this.Version = (xeTask.Attribute("version") != null ? xeTask.Attribute("version").Value : "1.000");
				this.Status = (xeTask.Attribute("status") != null ? xeTask.Attribute("status").Value : "Development");
				this.OriginalTaskID = this.ID;
				this.IsDefaultVersion = true;

				this.ConcurrentInstances = (xeTask.Attribute("concurrent_instances") != null ? xeTask.Attribute("concurrent_instances").Value : "");
				this.QueueDepth = (xeTask.Attribute("queue_depth") != null ? xeTask.Attribute("queue_depth").Value : "");
				//this.UseConnectorSystem = false;
				
				//parameters
				if (xeTask.Element("parameters") != null)
				{
					this.ParameterXDoc = XDocument.Parse(xeTask.Element("parameters").ToString(SaveOptions.DisableFormatting));
				}

				//now, codeblocks.
				foreach (XElement xCodeblock in xeTask.XPathSelectElements("//codeblocks/codeblock")) {
					if (xCodeblock.Attribute("name") == null) 
						throw new Exception("Task XML: All Codeblocks must have the 'name' attribute.");
					
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
			}
		}

		//constructor - from the database by ID
		public Task(string sTaskID, bool IncludeUserSettings, ref string sErr)
		{
			try
            {
				dataAccess dc = new dataAccess();
				acUI.acUI ui = new acUI.acUI();
				
				string sSQL = "select task_id, original_task_id, task_name, task_code, task_status, version, default_version," +
					" task_desc, use_connector_system, concurrent_instances, queue_depth, parameter_xml" +
					" from task" +
					" where task_id = '" + sTaskID + "'";
				
                DataRow dr = null;
                if (!dc.sqlGetDataRow(ref dr, sSQL, ref sErr)) 
					return;

                if (dr != null)
                {
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

					/*                    
                     * ok, this is important.
                     * there are some rules for the process of 'Approving' a task and other things.
                     * so, we'll need to know some count information
                     */
                    sSQL = "select count(*) from task" +
                        " where original_task_id = '" + this.OriginalTaskID + "'" +
                        " and task_status = 'Approved'";
                    int iCount = 0;
                    if (!dc.sqlGetSingleInteger(ref iCount, sSQL, ref sErr))
                    {
                        return;
                    }

					this.NumberOfApprovedVersions = iCount;

                    sSQL = "select count(*) from task" +
                        " where original_task_id = '" + this.OriginalTaskID + "'";
					if (!dc.sqlGetSingleInteger(ref iCount, sSQL, ref sErr))
                    {
                        return;
                    }

					this.NumberOfOtherVersions = iCount;
					
					
					//now, the fun stuff
					//1 get all the codeblocks and populate that dictionary
					//2 then get all the steps... ALL the steps in one sql
					//..... and while spinning them put them in the appropriate codeblock
					
					//GET THE CODEBLOCKS
					sSQL = "select codeblock_name" +
						" from task_codeblock" +
						" where task_id = '" + sTaskID + "'" +
						" order by codeblock_name";
					
					DataTable dt = new DataTable();
					if (!dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
					{
						return;
					}
					
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
						sSQL = "insert task_codeblock (task_id, codeblock_name) values ('" + sTaskID + "', 'MAIN')";
						if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
						{
							return;
						}
						
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
			                " where s.task_id = '" + sTaskID + "'" +
			                " order by s.step_order";
					}
					else
					{
						sSQL = "select s.step_id, s.step_order, s.step_desc, s.function_name, s.function_xml, s.commented, s.locked, codeblock_name," +
			                " s.output_parse_type, s.output_row_delimiter, s.output_column_delimiter, s.variable_xml," +
							" 0 as visible, 0 as breakpoint, 0 as skip, '' as button" +
							" from task_step s" +
			                " where s.task_id = '" + sTaskID + "'" +
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
									//nothing!  the gui will take care of drawing those embedded steps! 
									
									//maybe one day we'll do the full recusrive loading of all embedded steps here
									// but not today... it's a big deal and we need to let these changes settle down first.
								}
							}
						}
		            }
				}
            }
            catch (Exception ex)
            {
				throw ex;
            }
		}
		
		//take this Task and create the database records 
		public bool DBCreate(ref string sErr)
		{
			try
			{
                dataAccess dc = new dataAccess();
                acUI.acUI ui = new acUI.acUI();
				
				//task_id is the PK, and task_name+version is a unique index.
				//so, we check the conflict property, and act accordingly
				string sSQL = "select task_id from task where task_name = '" + this.Name + "' and version = '" + this.Version + "'";
	
				string sExistingTaskID = "";
				if (!dc.sqlGetSingleString(ref sExistingTaskID, sSQL, ref sErr))
				{
					sErr = "Unable to check for existing Name/Version. " + sErr;
					return false;
				}
				
				sSQL = "select count(*) from task where task_id = '" + this.ID + "'";
	
				int iIDExists = 0;
				if (!dc.sqlGetSingleInteger(ref iIDExists, sSQL, ref sErr))
				{
					sErr = "Unable to check for existing IDs. " + sErr;
					return false;
				}
				
				dataAccess.acTransaction oTrans = new dataAccess.acTransaction(ref sErr);
				
				if (iIDExists > 0 || !string.IsNullOrEmpty(sExistingTaskID))
				{
					//uh oh... this task exists.  unless told to do so, we stop here.
					if (this.OnConflict == "cancel") {
						sErr = "Another Task with that ID or Name/Version exists.  Conflict directive set to 'cancel'.";
						return false;
					}
					else {
						//ok, what are we supposed to do then?
						switch (this.OnConflict) {
						case "replace":
							//whack it all so we can re-insert
							//but by name or ID?  which was the conflict?
							//if it's the ID no problem, the history will be fine.
							//but if it's the name, we'll need to change our ID here to the ID of the one in the database.
							
							//task_id first, means we had a name/version collision we'll just plow and go
							//but we need to use the ID from the database
							if (ui.IsGUID(sExistingTaskID))
							    this.ID = sExistingTaskID;
							
							//if the ID existed it doesn't matter, we'll be plowing it anyway.
							//by "plow" I mean drop and recreate the codeblocks and steps... the task row will be UPDATED
							
		                    oTrans.Command.CommandText = "delete from task_step_user_settings" +
		                        " where step_id in" +
		                        " (select step_id from task_step where task_id = '" + this.ID + "')";
		                    if (!oTrans.ExecUpdate(ref sErr))
		                        throw new Exception(sErr);
		
		                    oTrans.Command.CommandText = "delete from task_step where task_id = '" + this.ID + "'";
		                    if (!oTrans.ExecUpdate(ref sErr))
		                        throw new Exception(sErr);
		
		                    oTrans.Command.CommandText = "delete from task_codeblock where task_id = '" + this.ID + "'";
		                    if (!oTrans.ExecUpdate(ref sErr))
		                        throw new Exception(sErr);
		
							//update the task row
		                    oTrans.Command.CommandText = "update task set" +
								" version = '" + this.Version + "'," +
								" task_name = '" + this.Name.Replace("'","") + "'," +
								" task_code = '" + this.Code.Replace("'","") + "'," +
								" task_desc = '" + this.Description.Replace("'","") + "'," +
								" task_status = '" + this.Status + "'," +
								" default_version = '" + (this.IsDefaultVersion ? 1 : 0) + "'," +
								" concurrent_instances = '" + this.ConcurrentInstances + "'," +
								" queue_depth = '" + this.QueueDepth + "'," +
								" created_dt = now()," +
								" parameter_xml = " + (this.ParameterXDoc != null ? "'" + this.ParameterXDoc.ToString(SaveOptions.DisableFormatting).Replace("'","") + "'" : "null") +
								" where task_id = '" + this.ID + "'";
		                    if (!oTrans.ExecUpdate(ref sErr))
		                        throw new Exception(sErr);
		
		                    //need to update this to work without session
							//ui.WriteObjectChangeLog(Globals.acObjectTypes.Task, this.ID, this.Name, "Task Updated");

							break;
						case "minor":
							//THIS WILL CALL THE asNewMinorVersion
							sErr = "Not yet implemented.";
							return false;
							//break;
						case "major":
							//THIS WILL CALL THE asNewMajorVersion method
							sErr = "Not yet implemented.";
							return false;
							//break;
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
					sSQL = "insert task" +
						" (task_id, original_task_id, version, default_version," +
							" task_name, task_code, task_desc, task_status, created_dt)" +
							" values " +
							"('" + this.ID + "', '" + this.ID + "', " + this.Version + ", 1, '" +
							this.Name.Replace("'","''") + "', '" + this.Code.Replace("'","") + "'," +
							"'" + this.Description.Replace("'","''") + "','" + this.Status + "', now())";
					oTrans.Command.CommandText = sSQL;
					if (!oTrans.ExecUpdate(ref sErr))
						return false;
					
					// add security log
					//need to update this to work without session
							//ui.WriteObjectAddLog(Globals.acObjectTypes.Task, this.ID, this.Name, "");
				}
			
				//by the time we get here, there should for sure be a task row, either new or updated.				
				//now, codeblocks
				foreach (Codeblock c in this.Codeblocks.Values) {
					sSQL = "insert task_codeblock (task_id, codeblock_name)" +
						" values ('" + this.ID + "', '" + c.Name + "')";
					oTrans.Command.CommandText = sSQL;
					if (!oTrans.ExecUpdate(ref sErr))
						return false;
									
					//and steps
					int iStepOrder = 1;
					foreach (Step s in c.Steps.Values) {
						sSQL = "insert into task_step (step_id, task_id, codeblock_name, step_order," +
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
								"'" + s.FunctionXML + "'" +
								")";
						oTrans.Command.CommandText = sSQL;
						if (!oTrans.ExecUpdate(ref sErr))
							return false;
						
						iStepOrder++;
					}
				}
				
				oTrans.Commit();
			
			}
			catch (Exception ex)
			{
				sErr = "Error updating the DB." + ex.Message;
				return false;
			}
			
			return true;
		}

		//INSTANCE METHOD - returns the object as XML
		public string AsXML()
		{
			XDocument xd = new XDocument();
			
			xd.Add(new XElement("task"));
			XElement xTask = xd.Element("task");
			
			xTask.SetAttributeValue("id", this.ID);
			xTask.SetAttributeValue("original_id", this.OriginalTaskID);
			xTask.SetAttributeValue("name", this.Name);
			xTask.SetAttributeValue("code", this.Code);
			xTask.SetAttributeValue("status", this.Status);
			xTask.SetAttributeValue("version", this.Version);
			xTask.SetAttributeValue("concurrent_instances", this.ConcurrentInstances);
			xTask.SetAttributeValue("queue_depth", this.QueueDepth);
			
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
					//if there's no function XML we're not doing anything... this step is busted.
					if (s.FunctionXDoc != null) {
						XElement xStep = new XElement("step");
						
						xStep.SetAttributeValue("id", s.ID);
						xStep.SetAttributeValue("output_parse_type", s.OutputParseType);
						xStep.SetAttributeValue("output_column_delimiter", s.OutputColumnDelimiter);
						xStep.SetAttributeValue("output_row_delimiter", s.OutputRowDelimiter);
						xStep.SetAttributeValue("commented", s.Commented);
						
						xStep.SetElementValue("description", s.Description);
						
						XElement xeFunc = XElement.Parse(s.FunctionXDoc.ToString(SaveOptions.DisableFormatting));
						xStep.Add(xeFunc);
						
						//variables aren't required but might be here.
						if (s.VariableXDoc != null) {	
							XElement xeVars = XElement.Parse(s.VariableXDoc.ToString(SaveOptions.DisableFormatting));
							xStep.Add(xeVars);
						}
						
						xSteps.Add(xStep);
					}
				}
				
				xCodeblocks.Add(xCodeblock);
			}
			
			
			//parameters should already be an XDocument
			xd.Add(this.ParameterXDoc);

					
			return xd.ToString();
		}

	}
	public class StepUserSettings
	{
		public bool Visible;
		public bool Breakpoint;
		public bool Skip;
		public string Button;

		//constructor
		public StepUserSettings()
		{

		}
	}
#endregion
}
