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
using System.Collections.Specialized;
using System.Data;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Web.Services;
using System.Xml.Linq;
using System.Xml.XPath;
using System.IO;
using Globals;

namespace ACWebMethods
{
    [WebService(Namespace = "ACWebMethods")]
    [WebServiceBinding(ConformsTo = WsiProfiles.BasicProfile1_1)]
    [System.ComponentModel.ToolboxItem(false)]
    // To allow this Web Service to be called from script, using ASP.NET AJAX, uncomment the following line. 
    [System.Web.Script.Services.ScriptService]
    public class api : System.Web.Services.WebService
    {
		/*
		AUTHENTICATION PROCESS
		
		for GET requests
		initially it's simple: 
		1) use the user_password to hash a specifically formatted part of the request
		this is precicely what should be hashed for the signature (with the proper values of course):
		     HelloWorld?key=0002bdaf-bfd5-4b9d-82d1-fd39c2947d19&timestamp=2011-12-20T13%3a58%3a14
		2) send me the request with "&signature=sha-256-hash" on the end

		 */
		
		private bool Authenticate(string sMethodName, NameValueCollection nvcQuerystring)
		{
			string sSQL = "";
			string sErr = "";
			
			// "key" is the user_id guid
			string sUserID = nvcQuerystring["key"];
			if (string.IsNullOrEmpty(sUserID))
				return false;
			
			// "timestamp" is a recent timestamp
			string sTimestamp = nvcQuerystring["timestamp"];
			if (string.IsNullOrEmpty(sTimestamp))
				return false;
			//url decoded
			sTimestamp = Server.UrlEncode(sTimestamp);
			
			//signature is the methodname, key and timestamp, SHA-256 hashed using the password
			string sSignature = nvcQuerystring["signature"];
			if (string.IsNullOrEmpty(sSignature))
				return false;
			

			//ok it had a signature... let's try to unpack it.

			dataAccess dc = new dataAccess();
			//1) get the password for the user_id provided
			sSQL = "select user_password from users where user_id = '" + sUserID + "'";
			string sDBUserPassword = "";
			if (!dc.sqlGetSingleString(ref sDBUserPassword, sSQL, ref sErr))
				return false;
			if (string.IsNullOrEmpty(sDBUserPassword))
				return false;
			sDBUserPassword = dc.DeCrypt(sDBUserPassword);
			
			//ok, we have a password and the necessary pieces of the querystring and method call.
			//let's see if the hash of the user_id using the password matches the signature
			
			//this is hardcoded and inflexible.  That rigidness is part of the security by design... the format must be *exact*
			string sStringToSign = sMethodName + "?key=" + sUserID + "&timestamp=" + sTimestamp;
			
			//init a hash class using the user_password as the key
			System.Security.Cryptography.HMACSHA256 MySigner = new System.Security.Cryptography.HMACSHA256(Encoding.UTF8.GetBytes(sDBUserPassword));
			
			//get the hash from sStringToSign
			byte[] bHash = MySigner.ComputeHash(Encoding.UTF8.GetBytes(sStringToSign));
            
//			StringBuilder sb = new StringBuilder();
//			for (int i = 0; i < bHashedDBPassword.Length; i++)
//			{
//				sb.Append(bHashedDBPassword[i].ToString("x"));
//			}
//			string sHashedDBPassword = sb.ToString();			
			
			//convert the hash to a hex string
			string sHashedString = BitConverter.ToString(bHash).Replace("-","").ToLower();
			
			if (sHashedString == sSignature)		
				return true;
			else
				return false;
		}
		
//		//this is an idea to validate the request if it were xml.
//		private bool ValidateRequest(string sRequestXML)
//		{
//			apiResponse res = new apiResponse();
//			
//			XDocument xRequest = XDocument.Parse(sRequestXML);
//			if (xRequest == null)
//			{
//                res.ErrorCode = 2300;
//				res.ErrorMessage = "Request Document is not valid XML or is empty.";
//			}
//			
//            XElement x = xDoc.XPathSelectElement("/parameters");
//            if (xParams == null)
//                throw new Exception("Parameter XML data does not contain 'parameters' root node.");
//			
//			
//		}
		
		//a method to test authentication
		[WebMethod(EnableSession = true)]
        public string HelloWorld()
        {
			apiResponse res = new apiResponse("HelloWorld");
			
			bool bSuccess = Authenticate("HelloWorld", this.Context.Request.QueryString);
			if (bSuccess)
			{
				res.Response = "Hello there!";
				return res.AsXML();
			}
			else
			{
				res.CommonResponse("1004");
				return res.AsXML();
			}
		}
		
        #region "Tasks"
        [WebMethod(EnableSession = true)]
        public string CreateTask(string TaskXML, string ParameterXML)
		{
			try
			{
				apiResponse res = new apiResponse("CreateTask");
				
				bool bSuccess = Authenticate("CreateTask", this.Context.Request.QueryString);
				if (bSuccess)
				{
					acUI.acUI ui = new acUI.acUI();
					uiMethods um = new uiMethods();
					
					string sErr = "";
					
					//we encoded this in javascript before the ajax call.
					TaskXML = ui.unpackJSON(TaskXML).Replace("'", "''");
					ParameterXML = ui.unpackJSON(ParameterXML).Replace("'", "''");
					
					//we gotta peek into the XML and encrypt any "encrypt" flagged values
					um.PrepareAndEncryptParameterXML(ref ParameterXML);				
					
					//should be easy ... convert the XML into a real task
					// insert that task into the db
					
					//the reason it goes into the db is for history's sake.
					//the "adhoc" tasks remain in the db, possibly hidden from the user
					//but at least for a while we retain a full record of what happened.
					
					//and, as a bonus, it's possible to take one of those ad-hoc tasks and "save" it as a regular task so it can be scheduled, etc.
					
					//will return a standard XML error document if there's a problem.
					//or a standard result XML if it's successful.
					
					Task t = new Task(TaskXML);
					
					//ok, now we have a task object.
					//call it's "create" method to save the whole thing in the db.
					if (t.DBCreate(ref sErr))
					{
						//success, but was there an error?
						if (!string.IsNullOrEmpty(sErr))
						{
							res.ErrorCode = "3014";
							res.ErrorMessage = "Task Create Failed";
							res.ErrorDetail = sErr;
							return res.AsXML();
						}
					}	
					else
					{
						res.ErrorCode = "3015";
						res.ErrorMessage = "Task Create Failed";
						res.ErrorDetail = sErr;
						return res.AsXML();
					}
					
					
					res.Response = "<task_id>" + t.ID + "</task_id>";
					return res.AsXML();
				}
				else
				{
					res.CommonResponse("1004");
					return res.AsXML();
				}
			}
			catch (Exception ex)
			{
				throw ex;
			}
        }

        [WebMethod(EnableSession = true)]
        public void wmStopTask(string sInstance)
        {
            taskMethods tm = new taskMethods();

            try
            {
                if (sInstance != "")
                {
					tm.wmStopTask(sInstance);
                    return;
                }
                else
                {
                    throw new Exception("Unable to stop task. Missing or invalid task_instance.");
                }

            }
            catch (Exception ex)
            {
                throw ex;
            }
        }
        #endregion
    }
}
