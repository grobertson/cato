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
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.Security;
using System.Data;
using System.Xml.Linq;
using System.Xml.XPath;
using Globals;

namespace Web
{
    public partial class sitemaster : System.Web.UI.MasterPage
    {
        acUI.acUI ui = new acUI.acUI();
        public acUI.AppGlobals ag = new acUI.AppGlobals();
		
        public string sUserID = "";
        protected void Page_Init(object sender, System.EventArgs e)
        {
            //check if the user is logged in.
            sUserID = ui.GetSessionUserID();
            if (string.IsNullOrEmpty(sUserID)) ui.Logout("");
        }

        protected void Page_Load(object sender, EventArgs e)
        {
			if (!Page.IsPostBack)
            {
				/*
                 * NOW! this app has a lot of pages, and each one needs to check whether or not the current user
                 * has the 'privilege' of viewing this page.
                 * 
                 * Rather than put code on each page to check the role, we'll just put it here and look 
                 * in a master list.
                 * */
				
				//this does a response.redirect.  Wont' work from ajax, we'll have to do something different.
                ui.IsPageAllowed("");
				
				//log page views if logging is enabled
				//this won't work from a web method either, it needs the Page object.  Figure it out.
				ui.addPageViewLog();


			}
        }
    }
}
