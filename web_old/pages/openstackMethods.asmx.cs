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
using System.Collections.Specialized;
using System.Linq;
using System.Web;
using System.Web.Services;
using System.Data;
using System.Text;
using System.IO;

using System.Net;
using System.Globalization;

using System.Xml.Linq;
using System.Xml;
using System.Xml.XPath;
using System.Xml.Serialization;

using Globals;

namespace ACWebMethods
{
    /// <summary>
    /// openstackMethods: for interacting with the OpenStack REST API.
    /// </summary>
    [WebService(Namespace = "ACWebMethods")]
    [WebServiceBinding(ConformsTo = WsiProfiles.BasicProfile1_1)]
    [System.ComponentModel.ToolboxItem(false)]
    // To allow this Web Service to be called from script, using ASP.NET AJAX, uncomment the following line. 
    [System.Web.Script.Services.ScriptService]

    public class openstackMethods : System.Web.Services.WebService
    {

		acUI.acUI ui = new acUI.acUI();

//		[WebMethod(EnableSession = true)]
//		public string wmTestCloudConnection(string sAccountID, string sCloudID)
//		{
//			acUI.acUI ui = new acUI.acUI();
//			string sErr = "";
//			
//			Cloud c = new Cloud(sCloudID);
//			if (c.ID == null) {
//				return "{\"result\":\"fail\",\"error\":\"Failed to get Cloud details for Cloud ID [" + sCloudID + "].\"}";
//			}
//			
//			CloudAccount ca = new CloudAccount(sAccountID);
//			if (ca.ID == null) {
//				return "{\"result\":\"fail\",\"error\":\"Failed to get Cloud Account details for Cloud Account ID [" + sAccountID + "].\"}";
//			}
//
//			//get the test cloud object type for this provider
//			CloudObjectType cot = ui.GetCloudObjectType(c.Provider, c.Provider.TestObject);
//			if (cot != null) {
//				if (string.IsNullOrEmpty(cot.ID)) {
//					return "{\"result\":\"fail\",\"error\":\"Cannot find definition for requested object type [" + c.Provider.TestObject + "].\"}";
//				}
//			} else {
//				return "{\"result\":\"fail\",\"error\":\"GetCloudObjectType failed for [" + c.Provider.TestObject + "].\"}";
//			}
//			
//			string sURL = GetURL(ca, c, cot, null, ref sErr);			
//			if (!string.IsNullOrEmpty(sErr))
//				return "{\"result\":\"fail\",\"error\":\"" + ui.packJSON(sErr) +"\"}";
//			
//			string sResult = ui.HTTPGet(sURL, 15000, ref sErr);
//			if (!string.IsNullOrEmpty(sErr))
//				return "{\"result\":\"fail\",\"error\":\"" + ui.packJSON(sErr) + "\"}";
//
//			return "{\"result\":\"success\",\"response\":\"" + ui.packJSON(sResult) + "\"}";
//		}

        #region "Request Building Methods"
        public string GetCloudObjectsAsXML(string sCloudID, CloudObjectType cot, ref string sErr, Dictionary<string, string> AdditionalArguments)
        {
            string sXML = "";

			string sAccountID = ui.GetSelectedCloudAccountID();
			CloudAccount ca = new CloudAccount(sAccountID);
			if (ca.ID == null) {
				sErr = "Failed to get Cloud Account details for Cloud Account ID [" + sAccountID + "].";
				return null;
			}

            if (cot != null)
            {
                //many reasons why we'd bail here.  Rather than a bunch of testing below, let's just crash
                //if a key field is missing.
                if (string.IsNullOrEmpty(cot.ID))
                { sErr = "Cannot find definition for requested object type [" + cot.ID + "]"; return null; }
//                if (string.IsNullOrEmpty(prod.APIUrlPrefix))
//                { sErr = "APIUrlPrefix not defined for requested object type [" + cot.ID + "]"; return null; }
//                if (string.IsNullOrEmpty(cot.APICall))
//                { sErr = "APICall not defined for requested object type [" + cot.ID + "]"; return null; }
            }
            else
            {
                sErr = "GetCloudObjectType failed for [" + cot.ID + "]";
                return null;
            }
			
			//get the cloud object
			Cloud c = new Cloud(sCloudID);
			if (c.ID == null) {
                sErr = "Failed to get Cloud details for Cloud ID [" + sCloudID + "].";
                return null;
			}
			
			string sAuthToken = "";
			string sURL = GetURL(ca, c, cot, ref sAuthToken, ref sErr);			
			if (!string.IsNullOrEmpty(sErr))
				return null;
			
			NameValueCollection nvcHeaders = new NameValueCollection();
			nvcHeaders.Add("X-Auth-Token", sAuthToken);
			nvcHeaders.Add("Accept", "application/xml");
			
			sXML = ui.HTTPGet(sURL, 15000, nvcHeaders, ref sErr);
			if (!string.IsNullOrEmpty(sErr))
				return null;

            return sXML;
        }
		private string GetURL(CloudAccount ca, Cloud c, CloudObjectType cot, ref string sAuthToken, ref string sErr)
		{
			Product prod = cot.ParentProduct;
		
			//for openstack, the url has "region" information at the beginning, 
			//THEN it has the "product"...
			//THEN the host name.
			//https://az-1.region-a.geo-1.compute.hpcloudsvc.com/v1/70599487453338/servers
			
			//NOTE: we will use the Identity product to get this token...
			//so make sure the identity product is configured correctly.
			
			//the "tenant id" is our "AccountNumber" (that we don't use for AWS).
			//we'll need to provide these three values to the identity server request.
			string sTenantID = ca.AccountNumber;
			string sAccessKeyID = ca.LoginID;
			string sSecretAccessKeyID = ca.LoginPassword;

			if (!ca.Provider.Products.ContainsKey("identity")) {
                sErr = "Unable to continue.  Cloud Provider [" + ca.Provider.Name + "] does not have an Identity product defined.";
                return null;
			}
			
			Product idProd = ca.Provider.Products["identity"];
			if (idProd == null) {
                sErr = "Failed to get Identity Product definition for Cloud [" + c.Name + "].";
                return null;
			}
			//we need the identity url
			//for the time being, we've hardcoded the identity url in the cloud_providers.xml
			//it should not be there, it should be a cloud property.
			//but all these pieces of the URL are just goofy and I'm not sure other openstack instances
			//will be the same.
			
			string sIdentityHost = c.APIUrl.Replace("{product}", idProd.Name);	
			string sIdentityURL = c.APIProtocol.ToLower() + "://" + sIdentityHost + idProd.APIUri + idProd.APIVersion + "/tokens";;
			
			Console.Write("IDURL:" + sIdentityURL + ":IDURL\n");
			
			string sData = "{\"auth\":{\"apiAccessKeyCredentials\":{" +
				"\"accessKey\": \"" + sAccessKeyID + "\", \"secretKey\":\"" + sSecretAccessKeyID + "\"" +
				"}, \"tenantId\":\"" + sTenantID + "\"}}";
			
			NameValueCollection nvcHeaders = new NameValueCollection();
			nvcHeaders.Add("Content-Type", "application/json");
			nvcHeaders.Add("Accept", "application/xml");

			string sTokenXML = ui.HTTPPost(sIdentityURL, sData, 10000, nvcHeaders, ref sErr);
			if (!string.IsNullOrEmpty(sErr))
				return null;

			sTokenXML = ui.RemoveDefaultNamespacesFromXML(sTokenXML);
			
			XDocument xTokenDoc = XDocument.Parse(sTokenXML);
			if (xTokenDoc == null) { sErr = "Identity Response XML document could not be parsed."; return null; }
			
			XElement xeToken = xTokenDoc.XPathSelectElement("access/token");
			if (xeToken == null) { sErr = "Token not found in Identity response."; return null; }
			
			XAttribute xaToken = xeToken.Attribute("id");
			if (string.IsNullOrEmpty(xaToken.Value))  { sErr = "Token found but id attribute is empty."; return null; }
			
			//whew, we made it and now we have a token!
			sAuthToken = xaToken.Value;

			
			
			string sHostName = "";
		
			if (!string.IsNullOrEmpty(prod.APIUrlPrefix) && !string.IsNullOrEmpty(c.APIUrl))
				sHostName = prod.APIUrlPrefix + c.APIUrl;
			else if (string.IsNullOrEmpty(prod.APIUrlPrefix) && !string.IsNullOrEmpty(c.APIUrl))
				sHostName = c.APIUrl;
			else if (!string.IsNullOrEmpty(prod.APIUrlPrefix) && string.IsNullOrEmpty(c.APIUrl))
				sHostName = prod.APIUrlPrefix;
		
			if (string.IsNullOrEmpty(sHostName)) {
				sErr = "Unable to reconcile an endpoint from the Cloud [" + c.Name + "] or Cloud Object [" + cot.ID + "] definitions." + sErr;
				return null;
			}

			
			//so, we allow the user to put the variable {product} in the url, and we replace it here.
			sHostName = sHostName.Replace("{product}", prod.Name);
			//and some api calls require a tenant_id, also replaced here
			string sAPICall = cot.APICall.Replace("{tenant}", sTenantID);
			
			string sHostURL = c.APIProtocol.ToLower() + "://" + sHostName + prod.APIUri + prod.APIVersion + sAPICall;
						
			Console.Write("URL:" + sHostURL + ":URL\n");

			return sHostURL;
		}

        #endregion
	}
}
