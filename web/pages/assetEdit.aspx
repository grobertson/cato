<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="assetEdit.aspx.cs" Inherits="Web.pages.assetEdit"
    MasterPageFile="~/pages/site.master" %>
<asp:Content ID="cHead" ContentPlaceHolderID="phHead" runat="server">
    <script type="text/javascript" src="../script/assetEdit.js"></script>
    <script type="text/javascript" src="../script/managePageCommon.js"></script>
    <script type="text/javascript" src="../script/objectTag.js"></script>
    <script type="text/javascript" src="../script/validation.js"></script>

    <style type="text/css">
        .credential_selector
        {
            height: 300px;
            overflow: auto;
        }
        .select_credential
        {
            background: #cccccc;
            cursor: pointer;
        }
        .credentialinputs
        {
            width: 200px;
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
        <input id="hidCredentialID" type="hidden" name="hidCredentialID" />
        <input id="hidCredentialType" type="hidden" name="hidCredentialID" />
        <asp:HiddenField ID="hidPageSize" runat="server" Value="15" />
        <asp:HiddenField ID="hidSortColumn" runat="server" />
        <asp:HiddenField ID="hidSortDirection" runat="server" />
        <asp:HiddenField ID="hidLastSortColumn" runat="server" />
        <asp:HiddenField ID="hidPage" runat="server" />
        <!-- Start visible elements -->
    </div>
    <div id="left_panel">
        <div class="left_tooltip">
            <img src="../images/manage-assets-192x192.png" alt="" />
            <div id="left_tooltip_box_outer">
                <div id="left_tooltip_box_inner">
                    <p>
                        <img src="../images/tooltip.png" alt="" />The Manage Assets screen allows administrators
                        to modify, add and delete Assets.</p>
                    <p>
                        Select one or more Assets from the list to the right, using the checkboxes. Select
                        an action to modify or delete the Assets you've selected.</p>
                </div>
            </div>
        </div>
    </div>
    <div id="content">
        <asp:UpdatePanel ID="uplAssetList" runat="server" UpdateMode="Conditional">
            <ContentTemplate>
                <span id="lblItemsSelected">0</span> Items Selected <span id="clear_selected_btn">
                </span><span id="item_create_btn">Create</span> <span id="item_modify_btn">Modify</span> <span id="item_delete_btn">Delete</span>
                <asp:TextBox ID="txtSearch" runat="server" class="search_text" />
                <span id="item_search_btn">Search</span>
                <asp:ImageButton ID="btnSearch" class="hidden" OnClick="btnSearch_Click" runat="server" />
                <table class="jtable" cellspacing="1" cellpadding="1" width="99%">
                    <tr>
                        <th class="chkboxcolumn">
                            <input type="checkbox" class="chkbox" id="chkAll" />
                        </th>
                        <th sortcolumn="asset_name" width="250px">
                            <img id="imgUpasset_name" src="../images/UpArrow.gif" class="hidden" alt="" />
                            <img id="imgDownasset_name" src="../images/DnArrow.gif" class="hidden" alt="" />
                            Asset
                        </th>
                        <th sortcolumn="asset_status" width="100px">
                            <img id="imgUpasset_status" src="../images/UpArrow.gif" class="hidden" alt="" />
                            <img id="imgDownasset_status" src="../images/DnArrow.gif" class="hidden" alt="" />
                            Status
                        </th>
                        <th sortcolumn="credentials" width="125px">
                            <img id="imgUpcredentials" src="../images/UpArrow.gif" class="hidden" alt="" />
                            <img id="imgDowncredentials" src="../images/DnArrow.gif" class="hidden" alt="" />
                            Credential
                        </th>
                        <th sortcolumn="address" width="50px">
                            <img id="imgUpaddress" src="../images/UpArrow.gif" class="hidden" alt="" />
                            <img id="imgDownaddress" src="../images/DnArrow.gif" class="hidden" alt="" />
                            Address
                        </th>
                        <th sortcolumn="connection_type" width="70px">
                            <img id="imgUpconnection_type" src="../images/UpArrow.gif" class="hidden" alt="" />
                            <img id="imgDownconnection_type" src="../images/DnArrow.gif" class="hidden" alt="" />
                            Conn Type
                        </th>
                    </tr>
                <asp:Repeater ID="rpAssets" runat="server">
                    <ItemTemplate>
                        <tr asset_id="<%# (((System.Data.DataRowView)Container.DataItem)["asset_id"]) %>">
                            <td class="chkboxcolumn" id="<%# (((System.Data.DataRowView)Container.DataItem)["asset_id"]) %>">
                                <input type="checkbox" class="chkbox" id="chk_<%# (((System.Data.DataRowView)Container.DataItem)["asset_id"]) %>"
                                    asset_id="<%# (((System.Data.DataRowView)Container.DataItem)["asset_id"]) %>"
                                    tag="chk" />
                            </td>
                            <td tag="selectable">
                                <%# (((System.Data.DataRowView)Container.DataItem)["asset_name"]) %>
                            </td>
                            <td tag="selectable">
                                <%# (((System.Data.DataRowView)Container.DataItem)["asset_status"]) %>
                            </td>
                            <td tag="selectable">
                                <%# (((System.Data.DataRowView)Container.DataItem)["shared_or_local"]) %><%# (((System.Data.DataRowView)Container.DataItem)["credentials"]) %>
                            </td>
                            <td tag="selectable">
                                <%# (((System.Data.DataRowView)Container.DataItem)["address"]) %>
                            </td>
                            <td tag="selectable">
                                <%# (((System.Data.DataRowView)Container.DataItem)["connection_type"]) %>
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
    <div id="edit_dialog" class="hidden" title="Create Asset">
        <div id="AddAssetTabs" style="height: 500px;">
            <ul>
                <li><a href="#GeneralTab"><span>General</span></a></li>
                <!--<li><a href="#TagsTab"><span>Tags</span></a></li>-->
                <li><a href="#CredentialsTab"><span>Credentials</span></a></li>
            </ul>
            <div id="GeneralTab">
                <table id="tblEdit" width="80%">
                    <tbody>
                        <tr>
                            <td>
                                Asset Name
                            </td>
                            <td>
                                <input id="txtAssetName" style="width: 200px;" type="text" name="txtAssetName" />
                            </td>
                        </tr>
                        <tr>
                            <td>
                                Status
                            </td>
                            <td>
                                <select id="ddlAssetStatus" style="width: 200px;" name="ddlAssetStatus">
                                    <option value="Active">Active</option>
                                    <option value="Inactive">Inactive</option>
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                Address
                            </td>
                            <td>
                                <input validate_as="hostname" id="txtAddress" style="width: 200px;" type="text" name="txtAddress" />
                            </td>
                        </tr>
                        <tr>
                            <td>
                                DB Name
                            </td>
                            <td>
                                <input validate_as="identifier" id="txtDbName" style="width: 200px;" type="text" maxlength="1024" name="txtDbName" />
                            </td>
                        </tr>
                        <tr>
                            <td>
                                Port
                            </td>
                            <td>
                                <input validate_as="posint" id="txtPort" style="width: 200px;" type="text" name="txtPort" />
                            </td>
                        </tr>
                        <tr>
                            <td>
                                Connection Type
                            </td>
                            <td>
                                <div id="ConnectionType">
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                Connection String
                            </td>
                            <td>
                                <textarea id="txtConnString" style="width: 400px;" type="text" name="txtConnString"
                                    rows="4"></textarea>
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
			<div id="TagsTab">
                <span id="tag_add_btn" class="tag_add_btn pointer">
                    <img src="../images/icons/edit_add.png" alt="" />
                    click to add </span>
                <hr />
                <ul id="objects_tags">
                </ul>
            </div>
			-->
            <div id="CredentialsTab">
                <table id="tblCredentials" width="80%">
                    <tbody>
                        <tr>
                            <td>
                                <input id="btnCredSelect" type="submit" value="Select Shared Credential" name="btnCredSelect" />
                                <input id="btnCredAdd" type="submit" value="New Credential" name="btnCredAdd" />
                                <p>
                                    &nbsp;</p>
                                <div id="CredentialDetails" class="col_header">
                                </div>
                                <div id="CredentialSelectorTabs" style="height: 380px;">
                                    <div id="CredentialSelectorShared" class="credential_selector">
                                    </div>
                                </div>
                                <div id="EditCredential">
                                    <table width="100%">
                                        <tr>
                                            <td align="center" colspan="2">
                                                <div id="SharedLocalDiv">
                                                    <input id="rbLocal" type="radio" value="1" name="rbShared" checked="checked" />
                                                    <label for="rbLocal">
                                                        Local</label>
                                                    <input id="rbShared" type="radio" value="0" name="rbShared" />
                                                    <label for="rbShared">
                                                        Shared</label>
                                                </div>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                Username
                                            </td>
                                            <td>
                                                <input validate_as="username" id="txtCredUsername" style="width: 200px;" name="txtCredUsername" />
                                            </td>
                                        </tr>
                                        <tr class="SharedCredFields hidden">
                                            <td>
                                                Name
                                            </td>
                                            <td>
                                                <input id="txtCredName" style="width: 200px;" name="txtCredName" />
                                            </td>
                                        </tr>
                                        <tr class="SharedCredFields hidden">
                                            <td>
                                                Description
                                            </td>
                                            <td>
                                                <input id="txtCredDescription" style="width: 200px;" name="txtCredDescription" />
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                Domain
                                            </td>
                                            <td>
                                                <input id="txtCredDomain" style="width: 200px;" name="txtCredDomain" />
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                Password
                                            </td>
                                            <td>
                                                <input id="txtCredPassword" style="width: 200px;" type="password" name="txtCredPassword" />
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                Password Confirm
                                            </td>
                                            <td>
                                                <input id="txtCredPasswordConfirm" style="width: 200px;" type="password" name="txtCredPasswordConfirm" />
                                            </td>
                                        </tr>
                                        <tr>
                                            <td colspan="2">
                                                &nbsp;
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                Privileged Mode Password
                                            </td>
                                            <td>
                                                &nbsp;
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                Password
                                            </td>
                                            <td>
                                                <input id="txtPrivilegedPassword" style="width: 200px;" type="password" name="txtPrivilegedPassword" />
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                Password Confirm
                                            </td>
                                            <td>
                                                <input id="txtPrivilegedConfirm" style="width: 200px;" type="password" name="txtPrivilegedConfirm" />
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <div id="delete_dialog" class="hidden" title="Delete Asset">
        <table>
            <tr>
                <td>
                    Are You sure you want to delete these assets?
                </td>
            </tr>
            <tr>
                <td>
                    <asp:Label ID="lblDeleteList" runat="server" Text="" />
                </td>
            </tr>
            <tr>
                <td>
                    <asp:Label ID="lblDeleteProgress" runat="server" Text="" />
                </td>
            </tr>
        </table>
    </div>
</asp:Content>
