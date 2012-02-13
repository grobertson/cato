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
    /// Summary description for awsMethods
    /// </summary>
    [WebService(Namespace = "ACAWSMethods")]
    [WebServiceBinding(ConformsTo = WsiProfiles.BasicProfile1_1)]
    [System.ComponentModel.ToolboxItem(false)]
    // To allow this Web Service to be called from script, using ASP.NET AJAX, uncomment the following line. 
    [System.Web.Script.Services.ScriptService]

    //class used to create our canonical list.
    class ParamComparer : IComparer<string>
    {
        public int Compare(string p1, string p2)
        {
            return string.CompareOrdinal(p1, p2);
        }
    }
    public class awsMethods : System.Web.Services.WebService
    {

		acUI.acUI ui = new acUI.acUI();

		[WebMethod(EnableSession = true)]
		public string wmTestCloudConnection(string sAccountID, string sCloudID)
		{
			acUI.acUI ui = new acUI.acUI();
			string sErr = "";
			
			Cloud c = new Cloud(sCloudID);
			if (c.ID == null) {
				return "{\"result\":\"fail\",\"error\":\"Failed to get Cloud details for Cloud ID [" + sCloudID + "].\"}";
			}
			
			CloudAccount ca = new CloudAccount(sAccountID);
			if (ca.ID == null) {
				return "{\"result\":\"fail\",\"error\":\"Failed to get Cloud Account details for Cloud Account ID [" + sAccountID + "].\"}";
			}

			//get the test cloud object type for this provider
			CloudObjectType cot = ui.GetCloudObjectType(c.Provider, c.Provider.TestObject);
			if (cot != null) {
				if (string.IsNullOrEmpty(cot.ID)) {
					return "{\"result\":\"fail\",\"error\":\"Cannot find definition for requested object type [" + c.Provider.TestObject + "].\"}";
				}
			} else {
				return "{\"result\":\"fail\",\"error\":\"GetCloudObjectType failed for [" + c.Provider.TestObject + "].\"}";
			}
			
			string sURL = GetURL(ca, c, cot, null, ref sErr);			
			if (!string.IsNullOrEmpty(sErr))
				return "{\"result\":\"fail\",\"error\":\"" + ui.packJSON(sErr) +"\"}";
			
			string sResult = ui.HTTPGet(sURL, 15000, ref sErr);
			if (!string.IsNullOrEmpty(sErr))
				return "{\"result\":\"fail\",\"error\":\"" + ui.packJSON(sErr) + "\"}";

			return "{\"result\":\"success\",\"response\":\"" + ui.packJSON(sResult) + "\"}";
		}

        #region "Request Building Methods"
        //this method looks up a cloud object in our database, and executes a call based on CloudObjectType parameters.
        //the columns created as part of the object are defined as CloudObjectTypeProperty.
        public DataTable GetCloudObjectsAsDataTable(string sCloudID, string sObjectType, ref string sErr)
        {
            try
            {
                //build the DataTable
                DataTable dt = new DataTable();

                //get the cloud object type from the session
				Provider p = ui.GetSelectedCloudProvider();
				CloudObjectType cot = ui.GetCloudObjectType(p, sObjectType);
                if (cot != null)
                {
                    if (string.IsNullOrEmpty(cot.ID))
                    { sErr = "Cannot find definition for requested object type [" + sObjectType + "]"; return null; }
                }
                else
                {
                    sErr = "GetCloudObjectType failed for [" + sObjectType + "]";
                    return null;
                }

                string sXML = GetCloudObjectsAsXML(sCloudID, cot, ref sErr, null);
                if (sErr != "") return null;
				
				if (string.IsNullOrEmpty(sXML))
				{
					sErr = "GetCloudObjectsAsXML returned an empty document.";
					return null;
				}

                //OK look, all this namespace nonsense is annoying.  Every AWS result I've witnessed HAS a namespace
                // (which messes up all our xpaths)
                // but I've yet to see a result that actually has two namespaces 
                // which is the only scenario I know of where you'd need them at all.

                //So... to eliminate all namespace madness
                //brute force... parse this text and remove anything that looks like [ xmlns="<crud>"] and it's contents.
                sXML = ui.RemoveNamespacesFromXML(sXML);

                XDocument xDoc = XDocument.Parse(sXML);
                if (xDoc == null) { sErr = "API Response XML document is invalid."; return null; }


                //what columns go in the DataTable?
                if (cot.Properties.Count > 0)
                {
					//this is for the hardcoded properties in the cloud_providers.xml file.
					//if we want to show ALL object tags from the xml tagSet,
					//perhaps that whole xml snip should go in a column on this datatable.
					
                    foreach (CloudObjectTypeProperty prop in cot.Properties)
                    {
                        //the column on the data table *becomes* the property.
                        //we'll load it up with all the goodness we need anywhere else
                        DataColumn dc = new DataColumn();

                        dc.ColumnName = prop.Name;

                        //This is important!  Places in the GUI expect the first column to be the ID column.
                        //hoping to stop doing that in favor of this property.
                        dc.ExtendedProperties.Add("IsID", prop.IsID.ToString());
                        //will we try to draw an icon?
                        dc.ExtendedProperties.Add("HasIcon", prop.HasIcon.ToString());
                        //a "short list" property is one that will always show up... it's a shortcut in some places.
                        dc.ExtendedProperties.Add("ShortList", prop.ShortList.ToString());
						//what was the xpath for this property?
                        dc.ExtendedProperties.Add("XPath", prop.XPath.ToString());
						//do we grab the "value" for this property, or the xml?
                        dc.ExtendedProperties.Add("ValueIsXML", prop.ValueIsXML.ToString());
                        
						//it might have a custom caption
                        if (!string.IsNullOrEmpty(prop.Label)) dc.Caption = prop.Label;

                        //add the column
                        dt.Columns.Add(dc);
                    }
                }
                else
                {
                    sErr = "No properties defined for type [" + sObjectType + "]";
                    //if this is a power user, write out the XML of the response as a debugging aid.
                    if (ui.UserIsInRole("Developer") || ui.UserIsInRole("Administrator"))
                    {
                        sErr += "<br />RESPONSE:<br /><pre>" + ui.SafeHTML(sXML) + "</pre>";
                    }
                    return null;
                }
				
                //ok, columns are added.  Parse the XML and add rows.
                foreach (XElement xeRecord in xDoc.XPathSelectElements(cot.XMLRecordXPath))
                {
                    DataRow drNewRow = dt.NewRow();

                    //we could just loop the Cloud Type Properties again, but doing the DataColumn collection
                    //ensures all the info we need got added
                    foreach (DataColumn dc in dt.Columns)
                    {
						//if it's a tagset column put the tagset xml in it
						// for all other columns, they get a lookup
                        XElement xeProp = xeRecord.XPathSelectElement(dc.ExtendedProperties["XPath"].ToString());
                        if (xeProp != null) {
							//does this column have the extended property "ValueIsXML"?
							bool bAsXML = (dc.ExtendedProperties["ValueIsXML"] != null ? 
							               (dc.ExtendedProperties["ValueIsXML"].ToString() == "True" ? true : false): false);
							
							if (bAsXML)
								drNewRow[dc.ColumnName] = xeProp.ToString(SaveOptions.DisableFormatting);
							else
								drNewRow[dc.ColumnName] = xeProp.Value;
						}
					}

                    //build the row
                    dt.Rows.Add(drNewRow);
                }

                //all done
                return dt;
            }
            catch (Exception ex)
            {
                sErr = ex.Message;
                return null;
            }
        }
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
			
			string sURL = GetURL(ca, c, cot, AdditionalArguments, ref sErr);			
			if (!string.IsNullOrEmpty(sErr))
				return null;
			
			sXML = ui.HTTPGet(sURL, 15000, ref sErr);
			if (!string.IsNullOrEmpty(sErr))
				return null;

            return sXML;
        }
		private string GetURL(CloudAccount ca, Cloud c, CloudObjectType cot, Dictionary<string, string> AdditionalArguments, ref string sErr)
		{
			//!!! OK, PAY ATTENTION HERE
			//there's a possibility of a timestamp signature collision when making API calls very quickly back to back.
			//AWS/Eucalyptus recommends trapping for the HTTP 403 error, waiting 1 second, and trying again.
			
			//Since our HTTP function is shared in many places even by non-cloud code, we don't wanna muddy it up with 
			//a case specific handler.
			
			//One second isn't terribly long.  So, we're just sleeping a second here before every api call, just to ensure
			// enough space between.
			
			System.Threading.Thread.Sleep(1000);
			
			
			//we have to use the provided cloud and object type to construct an endpoint
			//if either of these values is missing, we will attempt to use the other one standalone.
			string sHostName = "";
		
			Product prod = cot.ParentProduct;
		
			//if both are there, concatenate them
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
			
			//HOST URI
			//what's the URI... (if any)
			string sResourceURI = "";
			if (!string.IsNullOrEmpty(prod.APIUri))
				sResourceURI = prod.APIUri;
			
			
			//AWS auth parameters
			string sAccessKeyID = ca.LoginID;
			string sSecretAccessKeyID = ca.LoginPassword;
			
			
			//this object helps sort the parameters into canonicalized order
			ParamComparer pc = new ParamComparer();
			SortedDictionary<string, string> sortedRequestParams = new SortedDictionary<string, string>(pc);
		
			sortedRequestParams.Add("AWSAccessKeyId", sAccessKeyID);
			
			string sSignature = "";
			string sQueryString = "";
			
			if (prod.Name == "s3" || prod.Name == "walrus") {
				//HARDCODE ALERT
				//Currently (2-10-2010) AWS has goofy endpoints for the s3 services, using a "s3-" instead of "ec2.", etc.
				//MOREOVER, unlike all the other products, you cannot explicitly ask for the us-east-1 region.
				//so, we do a little interception here.
				sHostName = sHostName.Replace("s3-us-east-1","s3");
				//all other regions should work as defined.
				
				//s3 seems to need the epoch time "expires" value
				string sEpoch = ((int)(DateTime.UtcNow - new DateTime(1970, 1, 1)).TotalSeconds + 300).ToString();
				sortedRequestParams.Add("Expires", sEpoch);

				//per http://docs.amazonwebservices.com/AmazonS3/latest/dev/RESTAuthentication.html
				string sStringToSign = "GET\n" +
					"\n" + //Content-MD5
					"\n" + //Content-Type
					sEpoch + "\n" + //Expires
					(string.IsNullOrEmpty(sResourceURI) ? "/" : sResourceURI); //CanonicalizedResource

				Console.Write("STS:\n" + sStringToSign + ":STS\n");

				
				sQueryString = ui.GetSortedParamsAsString(sortedRequestParams, true);

				//and sign it
				sSignature = ui.GetSHA1(sSecretAccessKeyID, sStringToSign);
				Console.Write("SIG:" + sSignature + ":SIG\n");
				//finally, urlencode the signature
				sSignature = ui.PercentEncodeRfc3986(sSignature);
				Console.Write("SIG:" + sSignature + ":SIG\n");
				
			}
			else {
				//other AWS/Euca calls use the current Timestamp
				string sDate = DateTime.UtcNow.ToString("yyyy'-'MM'-'dd'T'HH':'mm':'ss", DateTimeFormatInfo.InvariantInfo);
				sortedRequestParams.Add("Timestamp", sDate);
			
		
				sortedRequestParams.Add("Action", cot.APICall);

				//do we need to apply a group filter?  If it's defined on the table then YES!
				if (!string.IsNullOrEmpty(cot.APIRequestGroupFilter)) {
					string[] sTmp = cot.APIRequestGroupFilter.Split('=');
					sortedRequestParams.Add(sTmp[0], sTmp[1]);
				}
		
				//ADDITIONAL ARGUMENTS
				if (AdditionalArguments != null) {
					//we have custom arguments... use them
					//for each... add to sortedRequestParams
					//if the same key from the group filter is defined as sAdditionalArguments it overrides the table!
				}
		
				sortedRequestParams.Add("Version", prod.APIVersion);
		
				sortedRequestParams.Add("SignatureMethod", "HmacSHA256");
				sortedRequestParams.Add("SignatureVersion", "2");
			
				//now we have all the parameters in a list, build a sorted, encoded querystring string
				//After the parameters are sorted in natural byte order and URL encoded, the next step is to concatenate them into a single text string.  
				//The following method uses the PercentEncodeRfc3986 method to create the parameter string.
				sQueryString = ui.GetSortedParamsAsString(sortedRequestParams, true);
		
			
				//use the URL/URI plus the querystring to build the full request to be signed
				//per http://docs.amazonwebservices.com/AWSEC2/latest/UserGuide/using-query-api.html
				string sStringToSign = "GET\n" +
					sHostName + "\n" + //ValueOfHostHeaderInLowercase
					(string.IsNullOrEmpty(sResourceURI) ? "/" : sResourceURI) + "\n" + //HTTPRequestURI
					sQueryString;  //CanonicalizedQueryString  (don't worry about encoding... was already encoded.)

				Console.Write("STS:" + sStringToSign + ":STS\n");

				//and sign it
				//string sSignature = GetAWS3_SHA1AuthorizationValue(sSecretAccessKeyID, sStringToSign);
				sSignature = ui.GetSHA256(sSecretAccessKeyID, sStringToSign);
				Console.Write("SIG:" + sSignature + ":SIG\n");
				//finally, urlencode the signature
				sSignature = ui.PercentEncodeRfc3986(sSignature);
				Console.Write("SIG:" + sSignature + ":SIG\n");
			}
		
			
			string sHostURL = c.APIProtocol.ToLower() + "://" + sHostName + sResourceURI;
						
			Console.Write("URL:" + sHostURL + "?" + sQueryString + "&Signature=" + sSignature + ":URL\n");

			return sHostURL + "?" + sQueryString + "&Signature=" + sSignature;
		}

        #endregion
    }
}
