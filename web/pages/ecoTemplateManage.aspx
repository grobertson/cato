<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="ecoTemplateManage.aspx.cs"
    Inherits="Web.pages.ecoTemplateManage" MasterPageFile="~/pages/site.master" %>

<asp:Content ID="cHead" ContentPlaceHolderID="phHead" runat="server">
    <script type="text/javascript" src="../script/managePageCommon.js"></script>
    <script type="text/javascript" src="../script/ecoTemplateManage.js"></script>
    <script type="text/javascript" src="../script/storm.js"></script>
</asp:Content>
<asp:Content ID="cDetail" ContentPlaceHolderID="phDetail" runat="server">
    <div style="display: none;">
        <input id="hidMode" type="hidden" name="hidMode" />
        <input id="hidEditCount" type="hidden" name="hidEditCount" />
        <input id="hidCurrentEditID" type="hidden" name="hidCurrentEditID" />
        <input id="hidSelectedArray" type="hidden" name="hidSelectedArray" />
        <asp:HiddenField ID="hidSortColumn" runat="server" />
        <asp:HiddenField ID="hidSortDirection" runat="server" />
        <asp:HiddenField ID="hidLastSortColumn" runat="server" />
        <asp:HiddenField ID="hidPage" runat="server" />
        <!-- Start visible elements -->
    </div>
    <div id="left_panel">
        <div id="left_tooltip_img">
			<img src="../images/icons/ecotemplates_128.png" alt="" />
        </div>
		<div class="left_tooltip">
            <div id="left_tooltip_box_outer">
                <div id="left_tooltip_box_inner">
					<h2>Manage EcoTemplates</h2>
                    <p>
                        The Manage Ecosystem Templates screen allows
                        administrators to modify, add and delete Templates for Ecosystems.</p>
                    <p>
                        Select one or more Templates from the list to the right, using the checkboxes. Select
                        an action to modify or delete the Templates you've selected.</p>
                    <p>
                        Templates cannot be deleted if they are referenced by any Ecosystems.</p>
					<p><a href="http://projects.cloudsidekick.com/projects/cato/wiki/Ecosystems?utm_source=cato_app&amp;utm_medium=helplink&amp;utm_campaign=app" target="_blank"><img src="../images/icons/info.png" alt="" />Click here</a>
						for a more detailed introduction to Ecosystem Templates.</p>
                </div>
            </div>
        </div>
    </div>
    <div id="content">
        <asp:UpdatePanel ID="udpList" runat="server" UpdateMode="Conditional">
            <ContentTemplate>
                <span id="lblItemsSelected">0</span> Items Selected <span id="clear_selected_btn">
                </span><span id="item_create_btn">Create</span><span id="item_copy_btn">Copy</span><span id="item_delete_btn">Delete</span>
                <asp:TextBox ID="txtSearch" runat="server" class="search_text" />
                <span id="item_search_btn">Search</span>
                <asp:ImageButton ID="btnSearch" class="hidden" OnClick="btnSearch_Click" runat="server" />
                <table class="jtable" cellspacing="1" cellpadding="1" width="99%">
                    <asp:Repeater ID="rpTasks" runat="server">
                        <HeaderTemplate>
                            <tr>
                                <th class="chkboxcolumn">
                                    <input class="chkbox" type="checkbox" id="chkAll" />
                                </th>
                                <th sortcolumn="ecotemplate_name" width="200px">
                                    Name
                                </th>
                                <th sortcolumn="ecotemplate_desc" width="200px">
                                    Description
                                </th>
                            </tr>
                        </HeaderTemplate>
                        <ItemTemplate>
                            <tr ecotemplate_id="<%#Eval("ecotemplate_id")%>">
                                <td class="chkboxcolumn">
                                    <input type="checkbox" class="chkbox" id="chk_<%#Eval("ecotemplate_id")%>" ecotemplate_id="<%#Eval("ecotemplate_id")%>"
                                        tag="chk" />
                                </td>
                                <td tag="selectable">
                                    <%#Eval("ecotemplate_name")%>
                                </td>
                                <td tag="selectable">
                                    <%#Eval("ecotemplate_desc")%>
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
    <div id="edit_dialog" class="hidden" title="New Eco Template">
        <table width="100%">
            <tbody>
                <tr>
                    <td colspan="2">
                        <span id="lblNewMessage" />
                    </td>
                </tr>
                <tr>
                    <td>
                        Name
                    </td>
                    <td>
                        <input type="text" id="txtTemplateName" class="w400px" />
                    </td>
                </tr>
				<tr>
                     <td>
                        Description
                     </td>
                     <td>
						<input type="text" id="txtTemplateDesc" class="w400px" />
                     </td>
                 </tr>
                <tr class="storm">
                    <td colspan="2">
                        <hr />
                    </td>
                </tr>
                <tr class="storm">
                    <td>
                        <img src="../images/icons/storm_32.png" />
                    </td>
                    <td style="vertical-align: middle;">
                        <input id="use_storm_btn" type="checkbox" />Provision with Storm?
                    </td>
                </tr>
                <tr class="stormfields hidden">
                    <td>
                        File Source
                    </td>
                    <td>
                        <select id="ddlStormFileSource"><option>URL</option><option>Text</option><option>File</option></select>
                    </td>
                </tr>
                <!--<tr class="stormfields hidden">
                    <td colspan="2">
					<input id="storm_file_picker" type="file" />
                        <textarea class="w500px" id="txtStormFile"></textarea>
						<div id="json_parse_msg"></div>
                    </td>
                </tr>-->
                <tr class="stormfields hidden">
                    <td colspan="2">
                        <hr />
                    </td>
                </tr>
                <tr class="stormfields hidden">
                    <td>
                    </td>
                    <td style="vertical-align:middle;">
                        <input type="checkbox" /> Run Storm Now?
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    <div id="delete_dialog" class="hidden" title="Delete Eco Templates">
        Are you sure you want to delete these Eco Templates?
    </div>
    <div id="copy_dialog" class="hidden" title="Copy Eco Template">
        <table id="tblCopy" width="100%">
            <tr>
                <td>
                    New Eco Template Name
                </td>
                <td>
                    <input type="text" id="txtCopyEcotemplateName" class="w400px" />
                </td>
            </tr>
        </table>
    </div>
</asp:Content>
