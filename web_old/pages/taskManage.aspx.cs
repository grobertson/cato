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
using System.Data;
using System.Web.UI;
using System.Web.UI.WebControls;
using Globals;

namespace Web.pages
{
    public partial class taskManage : System.Web.UI.Page
    {
        acUI.acUI ui = new acUI.acUI();

        int iPageSize;

        string sErr = "";

        protected void Page_Load(object sender, EventArgs e)
        {
            //could be repository settings for default values, and will be options on the page as well
            iPageSize = 50;

            if (!Page.IsPostBack)
            {
                // first time on the page, get the sortcolumn last used if one exists.
				Dictionary<string, string> dSort = ui.GetUsersSort("task");
				if (dSort != null)
				{
					hidSortColumn.Value = (dSort.ContainsKey("sort_column") ? dSort["sort_column"] : "");
					hidSortDirection.Value = (dSort.ContainsKey("sort_direction") ? dSort["sort_direction"] : "");
				}

                BindList();
            }
        }
        private void BindList()
        {
            DataTable dt = Tasks.AsDataTable(txtSearch.Text);
            if (dt != null)
            {
	            //put the datatable in the session
				ui.SetSessionObject("TaskList", dt, "SelectorListTables");
	            //now, actually get the data from the session table and display it
	            GetTasks();
            }
        }
        private void GetTasks()
        {
            //here's how the paging works
            //you can get at the data by explicit ranges, or by pages
            //where pages are defined by properties

            //could come from a field on the page
            int iStart = 0;
            int iEnd = 0;

            //this is the page number you want
            int iPageNum = (string.IsNullOrEmpty(hidPage.Value) ? 1 : Convert.ToInt32(hidPage.Value));
            DataTable dtTotal = (DataTable)ui.GetSessionObject("TaskList", "SelectorListTables");
            dtTotal.TableName = "TaskList";
            DataTable dt = ui.GetPageFromSessionTable(dtTotal, iPageSize, iPageNum, iStart, iEnd, hidSortColumn.Value, hidSortDirection.Value);

            rpTasks.DataSource = dt;
            rpTasks.DataBind();


            // save the last sort used
            ui.SaveUsersSort("task", hidSortColumn.Value, hidSortDirection.Value, ref sErr);


            if ((dt != null))
            {
                if ((dtTotal.Rows.Count > iPageSize))
                {
                    Literal lt = new Literal();
                    lt.Text = ui.DrawPager(dtTotal.Rows.Count, iPageSize, iPageNum);
                    phPager.Controls.Add(lt);
                }
            }
        }

        protected void btnGetPage_Click(object sender, System.EventArgs e)
        {
            GetTasks();
        }
        protected void btnSearch_Click(object sender, EventArgs e)
        {
            // we are searching so clear out the page value
            hidPage.Value = "1";
            BindList();
        }
    }
}
