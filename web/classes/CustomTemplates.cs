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
        
        public string GetCustomStepTemplate(string sStepID, string sFunction, XDocument xd, DataRow dr, ref string sOptionHTML, ref string sVariableHTML)
        {
            string sHTML = "";

            switch (sFunction.ToLower())
            {
                case "get_ecosystem_objects":
                    sHTML = GetEcosystemObjects(sStepID, sFunction, xd);
                    break;
                default:
                    //we don't have a special hardcoded case, just render it from the XML directly
                    sHTML = DrawStepFromXMLDocument(ref xd, sStepID, sFunction);
                    break;
            }

            return sHTML;
        }
        public string GetCustomStepTemplate_View(string sStepID, string sFunction, XDocument xd, DataRow dr, ref string sOptionHTML)
        {
            string sHTML = "";

            switch (sFunction.ToLower())
            {
                case "get_ecosystem_objects":
                    sHTML = GetEcosystemObjects_View(sStepID, sFunction, xd);
                    break;
                default:
                    sHTML = DrawReadOnlyStepFromXMLDocument(ref xd, sStepID, sFunction);
                    break;
            }

            return sHTML;
        }


        public string GetEcosystemObjects(string sStepID, string sFunction, XDocument xd)
        {
            XElement xObjectType = xd.XPathSelectElement("//object_type");
            string sObjectType = (xObjectType == null ? "" : xObjectType.Value);
			
            string sHTML = "";

            sHTML += "Select Object Type:" + Environment.NewLine;
            sHTML += "<select " + CommonAttribs(sStepID, sFunction, true, "object_type", "") + ">" + Environment.NewLine;
            sHTML += "  <option " + SetOption("", sObjectType) + " value=\"\"></option>" + Environment.NewLine;

            
			//temporary, waiting on issue #111/#128
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
        public string GetEcosystemObjects_View(string sStepID, string sFunction, XDocument xd)
        {
            XElement xObjectType = xd.XPathSelectElement("//object_type");
            string sObjectType = (xObjectType == null ? "" : xObjectType.Value);
			
			XElement xCloudFilter = xd.XPathSelectElement("//cloud_filter");
            string sCloudFilter = (xCloudFilter == null ? "" : xCloudFilter.Value);

            XElement xResultName = xd.XPathSelectElement("//result_name");
            string sResultName = (xResultName == null ? "" : xResultName.Value);

            XElement xCloudName = xd.XPathSelectElement("//cloud_name");
            string sCloudName = (xCloudName == null ? "" : xCloudName.Value);
			
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

    }
}
