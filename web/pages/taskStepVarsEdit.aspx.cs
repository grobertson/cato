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
using System.Web.Services;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Xml.Linq;
using Globals;

namespace Web.pages
{
    /// <summary>
    /// Description of taskStepVarsEdit
    /// </summary>
    public partial class taskStepVarsEdit : System.Web.UI.Page
    {
        acUI.acUI ui = new acUI.acUI();
        FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();

        string sUserID;
        string sStepID;

        private void Page_Load(object sender, System.EventArgs e)
        {
            sUserID = ui.GetSessionUserID();

            sStepID = ui.GetQuerystringValue("step_id", typeof(string)).ToString();
            hidStepID.Value = sStepID;

            if (!Page.IsPostBack)
            {
                BuildVars(sStepID);
            }
        }

        private void BuildVars(string sStepID)
        {
            string sErr = "";
            Step oStep = ft.GetSingleStep(sStepID, sUserID, ref sErr);

			Function fn = ui.GetTaskFunction(oStep.FunctionName);
			if (fn == null)
				throw new Exception("Error - Unable to get the details for the Command type '" + oStep.FunctionName + "'.");
			
            //we need these on the page
            hidOutputParseType.Value = oStep.OutputParseType.ToString();
            hidRowDelimiter.Value = oStep.OutputRowDelimiter.ToString();
            hidColDelimiter.Value = oStep.OutputColumnDelimiter.ToString();

            //header
            lblTaskName.Text = "[ " + oStep.Task.Name + " ] Version: [ " + oStep.Task.Version + " ]";
            lblCommandName.Text = oStep.Order.ToString() + " : " +
                fn.Category.Label + " - " + fn.Label;


            Literal lt = new Literal();
            
            if (sErr == "")
                lt.Text = ft.DrawVariableSectionForEdit(oStep);
            else
                lt.Text = "<span class=\"red_text\">" + sErr + "</span>";

            phVars.Controls.Add(lt);

            return;
        }


        [WebMethod(EnableSession = true)]
        public static string wmGetVars(string sStepID)
        {
            FunctionTemplates.HTMLTemplates ft = new FunctionTemplates.HTMLTemplates();
			string sErr = "";
			Step oStep = new Step(sStepID, "", ref sErr);
			if (!string.IsNullOrEmpty(sErr))
				throw new Exception("No data row found for step_id [" + sStepID + "].<br />" + sErr);

			if (oStep != null)
				return ft.GetVariablesForStepForEdit(oStep);
			else 
				return "";
        }

        [WebMethod(EnableSession = true)]
        public static string wmUpdateVars(string sStepID, string sOutputProcessingType, string sRowDelimiter, string sColDelimiter, object[] oVarArray)
        {
            dataAccess dc = new dataAccess();
			acUI.acUI ui = new acUI.acUI();
			
            string sErr = "";
            string sSQL = "";
            int i = 0;
			
			//if every single variable is delimited, we can sort them!
			bool bAllDelimited = true;
			
            ////update the processing method
            //sOutputProcessingType = sOutputProcessingType.Replace("'", "''");

            //we might need to do something special for some function types

            //removed this on 10/6/09 because we are hiding "output type"
            //                " output_parse_type = '" + sOutputProcessingType + "'," +

            sSQL = "update task_step set " +
                " output_row_delimiter = '" + sRowDelimiter + "'," +
                " output_column_delimiter = '" + sColDelimiter + "'" +
                " where step_id = '" + sStepID + "';";

            if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
            {
                throw new Exception(sErr);
            }


            //1 - create a new xdocument
            //2 - spin thru adding the variables
            //3 - commit the whole doc at once to the db

            XDocument xVarsDoc = new XDocument(new XElement("variables"));
            XElement xVars = xVarsDoc.Element("variables");

            //spin thru the variable array from the client
            for (i = 0; i <= oVarArray.Length - 1; i++)
            {
                //[0 - var type], [1 - var_name], [2 - left property], [3 - right property]

                ArrayList oVar = (ArrayList)oVarArray[i];

                //I'm just declaring named variable here for readability
                string sVarName = oVar[0].ToString();  //no case conversion
                string sVarType = oVar[1].ToString().ToLower();
                string sLProp = oVar[2].ToString(); //should we trim values, no?
                string sRProp = oVar[3].ToString();
                string sLType = oVar[4].ToString(); //should we trim values, no?
                string sRType = oVar[5].ToString();

                XElement xVar = new XElement("variable");
                xVar.Add(new XElement("name", sVarName));
                xVar.Add(new XElement("type", sVarType));


                //now that we've added it, based on the type let's add the custom properties
                switch (sVarType)
                {
                    case "delimited":
                        xVar.Add(new XElement("position", sLProp));
                        break;
                    case "regex":
					    bAllDelimited = false;
                        xVar.Add(new XElement("regex", sLProp));
                        break;
                    case "range":
					    bAllDelimited = false;
                        //we favor the 'string' mode over the index.  If a person selected 'index' that's fine
                        //but if something went wrong, we default to prefix/suffix.
                        if (sLType == "index")
                            xVar.Add(new XElement("range_begin", sLProp));
                        else
                            xVar.Add(new XElement("prefix", sLProp));

                        if (sRType == "index")
                            xVar.Add(new XElement("range_end", sRProp));
                        else
                            xVar.Add(new XElement("suffix", sRProp));
                        break;
                    case "xpath":
					    bAllDelimited = false;
                        xVar.Add(new XElement("xpath", sLProp));
                        break;
                }

                xVars.Add(xVar);

            }

            //if it's delimited, sort it
            if (sOutputProcessingType == "1" || bAllDelimited == true)
            {
				List<XElement> ordered = xVars.Elements("variable")
					.OrderBy(element => (int?)element.Element("position"))
						.ToList();
				
				xVars.RemoveAll();
				xVars.Add(ordered);
			
			}

            sSQL = "update task_step set " +
                " variable_xml = '" + ui.TickSlash(xVarsDoc.ToString(SaveOptions.DisableFormatting)) + "'" +
                " where step_id = '" + sStepID + "';";

            if (!dc.sqlExecuteUpdate(sSQL, ref sErr))
            {
                throw new Exception(sErr);
            }

            return "";
        }
    }
}
