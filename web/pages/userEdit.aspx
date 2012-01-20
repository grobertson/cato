<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="userEdit.aspx.cs" Inherits="Web.pages.userEdit"
    MasterPageFile="~/pages/site.master" %>

<asp:Content ID="cHead" ContentPlaceHolderID="phHead" runat="server">
    <script type="text/javascript" src="../script/managePageCommon.js"></script>
    <script type="text/javascript" src="../script/userEdit.js"></script>
    <script type="text/javascript" src="../script/objectTag.js"></script>
			
    <style type="text/css">
        .li_assets
        {
            width: 95%;
            padding: 2px;
            border: 1px solid #D3D3D3;
            background-color: #EEEEEE;
            list-style: none;
        }
    </style>
</asp:Content>
<asp:Content ID="cDetail" ContentPlaceHolderID="phDetail" runat="server">
    <div style="display: none;">
        <input id="hidPageSaveType" type="hidden" value="batch" />
        <input id="hidMode" type="hidden" name="hidMode" />
        <input id="hidEditCount" type="hidden" name="hidEditCount" />
        <input id="hidCurrentEditID" type="hidden" name="hidCurrentEditID" />
        <input id="hidSelectedArray" type="hidden" name="hidSelectedArray" />
        <!--codebehind uses this value to set the page size, -->
        <!-- we could possibly use the users current screen size to 'guess' at a decent page size? -->
        <asp:HiddenField ID="hidSortColumn" runat="server" />
        <asp:HiddenField ID="hidSortDirection" runat="server" />
        <asp:HiddenField ID="hidLastSortColumn" runat="server" />
        <asp:HiddenField ID="hidPage" runat="server" />
        <asp:HiddenField ID="hidRequirePasswordChange" runat="server" Value="no" />
        <!-- Start visible elements -->
    </div>
    <div id="left_panel">
        <div class="left_tooltip">
            <img src="../images/user-192x192.png" alt="" />
            <div id="left_tooltip_box_outer">
                <div id="left_tooltip_box_inner">
                    <p>
                        <img src="../images/tooltip.png" alt="" />The Adminster User screen allows administrators
                        to modify user permissions or add and delete users.</p>
                    <p>
                        Select one or more users from the list to the right, using the checkboxes. Select
                        an action to modify or delete the users you've selected.</p>
                </div>
            </div>
        </div>
    </div>
    <div id="content">
        <asp:UpdatePanel ID="uplUserList" runat="server" UpdateMode="Conditional">
            <ContentTemplate>
                <span id="lblItemsSelected">0</span> Items Selected <span id="clear_selected_btn">
                </span><span id="item_create_btn">Create</span> <span id="item_copy_btn">Copy</span>
                <span id="item_modify_btn">Modify</span> <span id="item_delete_btn">Delete</span>
                <asp:TextBox ID="txtSearch" runat="server" class="search_text" />
                <span id="item_search_btn">Search</span>
                <asp:ImageButton ID="btnSearch" class="hidden" OnClick="btnSearch_Click" runat="server" />
                <table class="jtable" cellspacing="1" cellpadding="1" width="99%">
                    <asp:Repeater ID="rpUsers" runat="server">
                        <HeaderTemplate>
                            <tr>
                                <th class="chkboxcolumn">
                                    <input type="checkbox" class="chkbox" id="chkAll" />
                                </th>
                                <th sortcolumn="status" width="80px">
                                    Status
                                </th>
                                <th sortcolumn="full_name" width="235px">
                                    User
                                </th>
                                <th sortcolumn="username">
                                    Login
                                </th>
                                <th sortcolumn="role" width="95px">
                                    Role
                                </th>
                                <th sortcolumn="last_login_dt" width="150px">
                                    Last Login
                                </th>
                            </tr>
                        </HeaderTemplate>
                        <ItemTemplate>
                            <tr user_id="<%# (((System.Data.DataRowView)Container.DataItem)["user_id"]) %>">
                                <td class="chkboxcolumn">
                                    <input type="checkbox" class="chkbox" id="chk_<%# (((System.Data.DataRowView)Container.DataItem)["user_id"]) %>"
                                        user_id="<%# (((System.Data.DataRowView)Container.DataItem)["user_id"]) %>" tag="chk" />
                                </td>
                                <td tag="selectable">
                                    <%# (((System.Data.DataRowView)Container.DataItem)["status"]) %>
                                </td>
                                <td tag="selectable">
                                    <%# (((System.Data.DataRowView)Container.DataItem)["full_name"]) %>
                                </td>
                                <td tag="selectable">
                                    <%# (((System.Data.DataRowView)Container.DataItem)["username"]) %>
                                </td>
                                <td tag="selectable">
                                    <%# (((System.Data.DataRowView)Container.DataItem)["role"]) %>
                                </td>
                                <td tag="selectable">
                                    <%# (((System.Data.DataRowView)Container.DataItem)["last_login_dt"]) %>
                                </td>
                            </tr>
                        </ItemTemplate>
                    </asp:Repeater>
                </table>
                <asp:PlaceHolder ID="phPager" runat="server"></asp:PlaceHolder>
                <div class="hidden">
                    <asp:Button ID="btnGetPage" runat="server" OnClick="btnGetPage_Click" /></div>
            </ContentTemplate>
        </asp:UpdatePanel>
    </div>
    <div id="edit_dialog" class="hidden" title="Add New User">
        <div id="AddUserTabs">
            <ul>
                <li><a href="#GeneralTab"><span>General</span></a></li>
                <!--<li><a href="#GroupsTab"><span>Groups (Tags)</span></a></li>-->
            </ul>
            <div id="GeneralTab" style="height: 350px;">
                <table style="width: 98%;">
                    <tbody>
                        <tr>
                            <td colspan="2">
                                <span id="lblNewUserMessage" />
                            </td>
                        </tr>
                        <tr>
                            <td style="width: 40%">
                                Login ID:
                            </td>
                            <td style="width: 60%">
                                <input id="txtUserLoginID" style="width: 90%;" type="text" name="txtUserLoginID" />
                            </td>
                        </tr>
                        <tr>
                            <td>
                                Full Name:
                            </td>
                            <td>
                                <input id="txtUserFullName" style="width: 90%;" type="text" name="txtUserFullName" />
                            </td>
                        </tr>
                        <tr>
                            <td>
                                Status:
                            </td>
                            <td>
                                <select id="ddlUserStatus" style="width: 90%;" name="ddlUserStatus">
                                    <option value="-1">Locked</option>
                                    <option value="1">Enabled</option>
                                    <option value="0">Disabled</option>
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                User Role:
                            </td>
                            <td>
                                <asp:DropDownList ID="ddlUserRole" runat="server" Style="width: 90%;">
                                </asp:DropDownList>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                Authentication Type:
                            </td>
                            <td>
                                <select id="ddlUserAuthType" style="width: 90%;" name="ddlUserAuthType">
                                    <option value="local">local</option>
                                    <option value="ldap">ldap</option>
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                Email Address:
                            </td>
                            <td>
                                <input id="txtUserEmail" style="width: 90%;" type="text" maxlength="1024" name="txtUserEmail" />
                            </td>
                        </tr>
                        <tr class="password_checkbox">
                            <td>
                                Generate Random Password?:
                            </td>
                            <td>
                                <input type="checkbox" id="chkGeneratePW" name="chkGeneratePW" />
                            </td>
                        </tr>
                        <tr class="password_entry">
                            <td>
                                Password:
                            </td>
                            <td>
                                <input id="txtUserPassword" style="width: 90%;" type="password" name="txtUserPassword" />
                            </td>
                        </tr>
                        <tr class="password_entry">
                            <td>
                                Confirm Password:
                            </td>
                            <td>
                                <input id="txtUserPasswordConfirm" style="width: 90%;" type="password" name="txtUserPasswordConfirm" />
                            </td>
                        </tr>
                        <tr class="password_edit">
                            <td>
                                Force Password Change?
                            </td>
                            <td>
                                <input id="cbNewUserForcePasswordChange" type="checkbox" name="cbNewUserForcePasswordChange" />
                            </td>
                        </tr>
                        <tr class="password_edit" id="trFailedLoginAttempts">
                            <td style="padding-top: 10px;">
                                Failed Login Attempts:
                            </td>
                            <td>
                                <span id="lblFailedLoginAttempts"></span>&nbsp;<span id="clear_failed_btn"></span>
                            </td>
                        </tr>
                        <tr class="password_edit">
                            <td style="padding-top: 10px;">
                                Password Reset:
                            </td>
                            <td>
                                <span id="pw_reset_btn">Reset</span><br />
                                Will send the user an email with a temporary password, which must be changed upon
                                login.
                            </td>
                        </tr>
                    </tbody>
                </table>
                <br />
                <span id="show_log_link" class="pointer">
                <img alt="" src="../images/icons/view_text_16.png" />
                View Change Log</span>
            </div>
            <!--
            <div id="GroupsTab">
                <span id="tag_add_btn" class="tag_add_btn pointer">
                    <img src="../images/icons/edit_add.png" alt="" />
                    click to add </span>
                <hr />
                <ul id="objects_tags">
                </ul>
            </div>
            -->
            <!--end hidden-->
        </div>
    </div>
    <div id="delete_dialog" class="hidden" title="Delete User">
        Are you sure you want to delete these users?
    </div>
    <div style="display: none;">
        Anything you want to hide goes in here.
    </div>
</asp:Content>
