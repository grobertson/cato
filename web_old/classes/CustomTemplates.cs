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
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Xml.Linq;
using System.Xml;
using System.Xml.XPath;
using System.Data;
using Globals;

namespace FunctionTemplates
{
    public partial class HTMLTemplates
    {
        
        public string GetCustomStepTemplate(Step oStep, ref string sOptionHTML, ref string sVariableHTML)
        {
			string sFunction = oStep.FunctionName;
            string sHTML = "";

            switch (sFunction.ToLower())
            {
                case "get_ecosystem_objects":
                    sHTML = GetEcosystemObjects(oStep);
                    break;
                default:
                    //we don't have a special hardcoded case, just render it from the XML directly
                    sHTML = DrawStepFromXMLDocument(oStep, ref sOptionHTML);
				
					//is the variables xml attribute true?
					XDocument xd = oStep.FunctionXDoc;
					if (xd != null) {
						if (xd.XPathSelectElement("//function") != null)
						{
							XElement xe = xd.XPathSelectElement("//function");
							if (xe != null) {
								{
									string sPopulatesVars = (xe.Attribute("variables") == null ? "" : xe.Attribute("variables").Value);
									
									if (sPopulatesVars == "true")
										sVariableHTML += DrawVariableSectionForDisplay(oStep, true);
								}
							}
						}
					}
				
                    break;
            }

            return sHTML;
        }
        public string GetCustomStepTemplate_View(Step oStep, ref string sOptionHTML)
        {
			string sFunction = oStep.FunctionName;
            string sHTML = "";

            switch (sFunction.ToLower())
            {
                case "get_ecosystem_objects":
                    sHTML = GetEcosystemObjects_View(oStep);
                    break;
                default:
                    sHTML = DrawReadOnlyStepFromXMLDocument(oStep);
                    break;
            }

            return sHTML;
        }


        public string GetEcosystemObjects(Step oStep)
        {
			string sStepID = oStep.ID;
			string sFunction = oStep.FunctionName;
			XDocument xd = oStep.FunctionXDoc;

            XElement xObjectType = xd.XPathSelectElement("//object_type");
            string sObjectType = (xObjectType == null ? "" : xObjectType.Value);			
            string sHTML = "";

            sHTML += "Select Object Type:" + Environment.NewLine;
            sHTML += "<select " + CommonAttribs(sStepID, sFunction, true, "object_type", "") + ">" + Environment.NewLine;
            sHTML += "  <option " + SetOption("", sObjectType) + " value=\"\"></option>" + Environment.NewLine;

            
			CloudProviders cp = ui.GetCloudProviders();
			if (cp != null)
			{
				foreach (Provider p in cp.Values) {
					Dictionary<string, CloudObjectType> cots = p.GetAllObjectTypes();
					foreach (CloudObjectType cot in cots.Values) {
						sHTML += "<option " + SetOption(cot.ID, sObjectType) + " value=\"" + cot.ID + "\">" + p.Name + " - " + cot.Label + "</option>" + Environment.NewLine;			
					}
				}
			}
			
			
            sHTML += "</select>" + Environment.NewLine;

            XElement xCloudFilter = xd.XPathSelectElement("//cloud_filter");
            string sCloudFilter = (xCloudFilter == null ? "" : xCloudFilter.Value);
            sHTML += "Cloud Filter: " + Environment.NewLine + "<input type=\"text\" " +
            CommonAttribs(sStepID, sFunction, false, "cloud_filter", "") +
            " help=\"Enter all or part of a cloud name to filter the results.\" value=\"" + sCloudFilter + "\" />" + Environment.NewLine;

            XElement xResultName = xd.XPathSelectElement("//result_name");
            string sResultName = (xResultName == null ? "" : xResultName.Value);
            sHTML += "<br />Result Variable: " + Environment.NewLine + "<input type=\"text\" " +
            CommonAttribs(sStepID, sFunction, false, "result_name", "") +
            " help=\"This variable array will contain the ID of each Ecosystem Object.\" value=\"" + sResultName + "\" />" + Environment.NewLine;

            XElement xCloudName = xd.XPathSelectElement("//cloud_name");
            string sCloudName = (xCloudName == null ? "" : xCloudName.Value);
            sHTML += " Cloud Name Variable: " + Environment.NewLine + "<input type=\"text\" " +
            CommonAttribs(sStepID, sFunction, false, "cloud_name", "") +
            " help=\"This variable array will contain the name of the Cloud for each Ecosystem Object.\" value=\"" + sCloudName + "\" />" + Environment.NewLine;

            return sHTML;
        }
        public string GetEcosystemObjects_View(Step oStep)
        {
			XDocument xd = oStep.FunctionXDoc;

            XElement xObjectType = xd.XPathSelectElement("//object_type");
            string sObjectType = (xObjectType == null ? "" : ui.SafeHTML(xObjectType.Value));
			
			XElement xCloudFilter = xd.XPathSelectElement("//cloud_filter");
            string sCloudFilter = (xCloudFilter == null ? "" : ui.SafeHTML(xCloudFilter.Value));

            XElement xResultName = xd.XPathSelectElement("//result_name");
            string sResultName = (xResultName == null ? "" : ui.SafeHTML(xResultName.Value));

            XElement xCloudName = xd.XPathSelectElement("//cloud_name");
            string sCloudName = (xCloudName == null ? "" : ui.SafeHTML(xCloudName.Value));
			
			string sHTML = "";

            sHTML += "Object Type: " + Environment.NewLine;
            sHTML += "<span class=\"code\">" + sObjectType + "</span>" + Environment.NewLine;
            sHTML += "Cloud Filter: " + Environment.NewLine;
            sHTML += "<span class=\"code\">" + sCloudFilter + "</span>" + Environment.NewLine;
            sHTML += "<br />Result Variable:" + Environment.NewLine;
            sHTML += "<span class=\"code\">" + sResultName + "</span>" + Environment.NewLine;
            sHTML += "Cloud Name Variable:" + Environment.NewLine;
            sHTML += "<span class=\"code\">" + sCloudName + "</span>" + Environment.NewLine;


            return sHTML;
		}

		//NOTE: the following functions are internal, but support dynamic dropdowns on step functions.
		//the function name is referenced by the "dataset" value of a dropdown type of input, where the datasource="function"
		//dropdowns expect a Dictionary<string,string> object return
		private Dictionary<string,string> ddDataSource_GetAWSClouds()
		{
			Dictionary<string,string> data = new Dictionary<string,string>();
			
			//AWS regions
			Provider p = Provider.GetFromSession("Amazon AWS");
			if (p != null)
			{
				foreach (Cloud c in p.Clouds.Values)
				{
					data.Add(c.Name, c.Name);
				}
			}
			//Eucalyptus clouds
			p = Provider.GetFromSession("Eucalyptus");
			if (p != null)
			{
				foreach (Cloud c in p.Clouds.Values)
				{
					data.Add(c.Name, c.Name);
				}
			}

			return data;
		}

	}
}
