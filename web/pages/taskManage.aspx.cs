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
using System.Linq;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Xml.Linq;

namespace Web.pages
{
    public partial class taskManage : System.Web.UI.Page
    {
        dataAccess dc = new dataAccess();
        acUI.acUI ui = new acUI.acUI();

        int iPageSize;

        string sSQL = "";
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
            string sWhereString = "";

            if (txtSearch.Text.Length > 0)
            {
                //split on spaces
                int i = 0;
                string[] aSearchTerms = txtSearch.Text.Split(' ');
                for (i = 0; i <= aSearchTerms.Length - 1; i++)
                {

                    //if the value is a guid, it's an existing task.
                    //otherwise it's a new task.
                    if (aSearchTerms[i].Length > 0)
                    {
                        sWhereString = " and (a.task_name like '%" + aSearchTerms[i] +
                           "%' or a.task_desc like '%" + aSearchTerms[i] +
                           "%' or a.task_status like '%" + aSearchTerms[i] +
                           "%' or a.task_code like '%" + aSearchTerms[i] + "%' ) ";
                    }
                } 
            }

            sSQL = "select a.task_id, a.original_task_id, a.task_name, a.task_code, a.task_desc, a.version, a.task_status" +
                   " from task a  " +
                   " where default_version = 1" +
                   sWhereString +
                   " order by task_code";


            DataTable dt = new DataTable();
            if (!dc.sqlGetDataTable(ref dt, sSQL, ref sErr))
            {
                ui.RaiseError(Page, sErr, true, "");
            }

            ui.SetSessionObject("TaskList", dt, "SelectorListTables");

            //now, actually get the data from the session table and display it
            GetTasks();
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

        #region "Buttons"

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

        #endregion

    }
}
