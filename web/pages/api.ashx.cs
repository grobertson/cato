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
using System.Web;
using System.Web.UI;
using System.Collections.Specialized;
using System.Text;
using Globals;
using ACWebMethods;

namespace Web
{
	public class api2 : System.Web.IHttpHandler
	{
		//some globals
		NameValueCollection QS;
		NameValueCollection FORM;
		apiResponse RESPONSE = new apiResponse();
		
		public virtual void ProcessRequest(HttpContext context)
		{
			// some examples
			//text
			// context.Response.ContentType = "text/plain";
			// context.Response.Write("Hello World");
			
			//an image
			// context.Response.ContentType = "image/png";
			// context.Response.WriteFile("~/Flower1.png");
			
			try 
			{
				//xml
				HttpResponse r = context.Response;
				r.ContentType = "text/xml";
				
				//querystring
				QS = context.Request.QueryString;
				//form
				FORM = context.Request.Form;
				
				//authenticate
				bool bSuccess = Authenticate();
				if (bSuccess)
				{
					string sAction = QS["action"];
					if (string.IsNullOrEmpty(sAction))
					{
						RESPONSE.ErrorCode = "0001";
						RESPONSE.ErrorMessage = "Action argument was not provided.";
						ThrowResponseAndEnd(ref context);
					}
					
					RESPONSE.Method = sAction;
					
					//the big switch statement
					//we will fall down through this, and every function call simply builds the response.
					//this might get big enough to be it's own function
					switch (sAction) {
					case "RunTask":
						//RunTask(ref context);
						break;
					case "StopTask":
						//StopTask(ref context);
						break;
					case "CreateTask":
						CreateTask(ref context);
						break;
					case "HelloWorld":
						RESPONSE.Response = "Hello there!";
						break;
					default:
						context.Response.Write("<error>unrecognized action specified</error>");
						break;
					}
				}
			else {
					RESPONSE.CommonResponse("1004");
				}
				
			}
			catch (Exception ex)
			{
				RESPONSE.ErrorCode = "0000";
				RESPONSE.ErrorMessage = "Exception";
				RESPONSE.ErrorDetail = ex.Message;
			}
			finally
			{
				ThrowResponseAndEnd(ref context);
			}
				
			//all done
			return;
		}
		
		private void ThrowResponseAndEnd(ref HttpContext context)
		{
			context.Response.Write(RESPONSE.AsXML());
			return;
		}
		/*
		AUTHENTICATION PROCESS
		
		for GET requests
		initially it's simple: 
		1) use the user_password to hash a specifically formatted part of the request
		this is precicely what should be hashed for the signature (with the proper values of course):
		     HelloWorld?key=0002bdaf-bfd5-4b9d-82d1-fd39c2947d19&timestamp=2011-12-20T13%3a58%3a14
		2) send me the request with "&signature=sha-256-hash" on the end

		 */
		
		private bool Authenticate()
		{
			string sSQL = "";
			string sErr = "";

			// "action" is the function we wanna perform
			string sAction = QS["action"];
			if (string.IsNullOrEmpty(sAction))
				return false;

			// "key" is the user_id guid
			string sUserID = QS["key"];
			if (string.IsNullOrEmpty(sUserID))
				return false;
			
			//HACK workaround for testing, a specific key skips the authentication
			if (sUserID == "12-34-56-78-90")
				return true;
			
			// "timestamp" is a recent timestamp
			string sTimestamp = QS["timestamp"];
			if (string.IsNullOrEmpty(sTimestamp))
				return false;
			//url decoded
			sTimestamp = Uri.EscapeDataString(sTimestamp);
			
			//signature is the methodname, key and timestamp, SHA-256 hashed using the password
			string sSignature = QS["signature"];
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
			string sStringToSign = "action=" + sAction + "&key=" + sUserID + "&timestamp=" + sTimestamp;
			
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

        #region "Tasks"
        private void CreateTask(ref HttpContext context)
		{
			acUI.acUI ui = new acUI.acUI();
			uiMethods um = new uiMethods();
			
			//required arguments from the form post
			//how to get them??
			string sParameterXML = "";

			string sTaskXML = FORM["TaskXML"];
			if (string.IsNullOrEmpty(sTaskXML))
			{
				RESPONSE.ErrorCode = "3000";
				RESPONSE.ErrorMessage = "TaskXML argument was not provided.";
				ThrowResponseAndEnd(ref context);
			}

			
			string sErr = "";
			
			//we encoded this in javascript before the ajax call.
			sTaskXML = ui.unpackJSON(sTaskXML).Replace("'", "''");
			sParameterXML = ui.unpackJSON(sParameterXML).Replace("'", "''");
			
			//we gotta peek into the XML and encrypt any "encrypt" flagged values
			um.PrepareAndEncryptParameterXML(ref sParameterXML);				
			
			//should be easy ... convert the XML into a real task
			// insert that task into the db
			
			//the reason it goes into the db is for history's sake.
			//the "adhoc" tasks remain in the db, possibly hidden from the user
			//but at least for a while we retain a full record of what happened.
			
			//and, as a bonus, it's possible to take one of those ad-hoc tasks and "save" it as a regular task so it can be scheduled, etc.
			
			//will return a standard XML error document if there's a problem.
			//or a standard result XML if it's successful.
			
			Task t = new Task(sTaskXML);
			
			//ok, now we have a task object.
			//call it's "create" method to save the whole thing in the db.
			if (t.DBCreate(ref sErr))
			{
				//success, but was there an error?
				if (!string.IsNullOrEmpty(sErr))
				{
					RESPONSE.ErrorCode = "3000";
					RESPONSE.ErrorMessage = "Task Create Failed";
					RESPONSE.ErrorDetail = sErr;
				}
			}	
			else
			{
				RESPONSE.ErrorCode = "3001";
				RESPONSE.ErrorMessage = "Task Create Failed";
				RESPONSE.ErrorDetail = sErr;
			}
			
			RESPONSE.Response = "<task_id>" + t.ID + "</task_id>";
        }

        private void RunTask(string TaskID, string EcosystemID, string AccountID, string AssetID, string ParameterXML, int DebugLevel)
        {
			taskMethods tm = new taskMethods();
			
			if (!string.IsNullOrEmpty(TaskID))
			{
				string sInstance = tm.wmRunTask(TaskID, EcosystemID, AccountID, AssetID, ParameterXML, DebugLevel);
				if (!string.IsNullOrEmpty(sInstance))
				{
					RESPONSE.Response = "<task_instance>" + sInstance + "</task_instance>";
				}
				else
				{
					RESPONSE.ErrorCode = "3010";
					RESPONSE.ErrorMessage = "Run Task Failed";
					RESPONSE.ErrorDetail = "Unable to run Task. No Instance returned.";
				}
			}
			else
			{
				RESPONSE.ErrorCode = "3011";
				RESPONSE.ErrorMessage = "Run Task Failed";
				RESPONSE.ErrorDetail = "Unable to run Task. Missing or invalid Task ID.";
			}
        }


        private void StopTask(string Instance)
        {
			taskMethods tm = new taskMethods();
			
			if (!string.IsNullOrEmpty(Instance))
			{
				tm.wmStopTask(Instance);
				RESPONSE.Response = "Success";
			}
			else
			{
				RESPONSE.ErrorCode = "3020";
				RESPONSE.ErrorMessage = "Task Stop Failed";
				RESPONSE.ErrorDetail = "Unable to stop Task. Missing or invalid Task Instance.";
			}
        }
        #endregion

		
		public virtual bool IsReusable {
			get {
				return false;
			}
		}
		
	}
}

