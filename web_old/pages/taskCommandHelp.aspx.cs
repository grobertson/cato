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
using System.Web.UI.HtmlControls;
using System.Data;
using Globals;

namespace Web.pages
{
    public partial class taskCommandHelp : System.Web.UI.Page
    {
        acUI.acUI ui = new acUI.acUI();

        private void Page_Load(object sender, System.EventArgs e)
        {
            if (!Page.IsPostBack)
            {
				Functions funcs = ui.GetTaskFunctions();

                if (funcs == null)
                {
                    ui.RaiseError(Page, "Error: Task Functions class is not in the session.", false, "");
                } 
				else 
				{
					string sFunHTML = "";
					foreach (Function fn in funcs.Values)
					{
						sFunHTML += "<p>";
						sFunHTML += "<img src=\"../images/" + fn.Icon + "\" alt=\"\" />";
						sFunHTML += "<span>" + fn.Category.Label + " : " + fn.Label + "</span>";
						sFunHTML += "<div>";
						sFunHTML += fn.Help;
						sFunHTML += "</div>";
						sFunHTML += "</p><hr />";
					}
					ltHelp.Text = sFunHTML;
				}

            }
        }
    }
}
