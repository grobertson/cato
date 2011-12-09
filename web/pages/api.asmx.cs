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

        #region "Tasks"
        [WebMethod(EnableSession = true)]
        public string wmRunTask(string TaskXML, string ParameterXML)
        {
            acUI.acUI ui = new acUI.acUI();
			uiMethods um = new uiMethods();
			
            //we encoded this in javascript before the ajax call.
            TaskXML = ui.unpackJSON(TaskXML).Replace("'", "''");
            ParameterXML = ui.unpackJSON(ParameterXML).Replace("'", "''");
							
			//we gotta peek into the XML and encrypt any "encrypt" flagged values
			um.PrepareAndEncryptParameterXML(ref ParameterXML);				

            try
            {
				//should be easy ... convert the XML into a real task
				// insert that task into the db
				// and launch it
				
				//the reason it goes into the db is for history's sake.
				//the "adhoc" tasks remain in the db, possibly hidden from the user
				//but at least for a while we retain a full record of what happened.
				
				//and, as a bonus, it's possible to take one of those ad-hoc tasks and "save" it as a regular task so it can be scheduled, etc.
				
				//will return a standard XML error document if there's a problem.
				//or a standard result XML if it's successful.
				
				Task t = new Task(TaskXML);
					
				//ok, now we have a task object.
				//call it's "create" method to save the whole thing in the db.
				t.Status = "adhoc";
						
				//t.Save();
						
						
				string sInstance = "";
				return "<result><task_instance>" + sInstance + "</task_instance></result>";
				//return "<result><error>Unable to parse and load TaskXML.</error></result>";
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
