<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="importLoadFile.aspx.cs"
    Inherits="Web.pages.importLoadFile" MasterPageFile="~/pages/site.master" %>

<asp:Content ID="cDetail" ContentPlaceHolderID="phDetail" runat="server">
    <div id="content">
        Select a file to import.<br />
        <input type="file" id="fupFile" runat="server" />
        <asp:Button ID="btnImport" runat="server" Text="Load File" OnClick="btnImport_Click" />
        <asp:Panel ID="pnlResume" runat="server">
            -OR-<br />
            <a href="importReconcile.aspx">Resume reconcilation of the last import session.
            </a>
        </asp:Panel>
    </div>
    <div id="left_panel">
        <div class="left_tooltip">
            <img src="../images/terminal-192x192.png" alt="" />
            <div id="left_tooltip_box_outer">
                <div id="left_tooltip_box_inner">
					<h2>Import</h2>
                        <p>Select an Export package to Import. This will be a .csk file format.</p>
                </div>
            </div>
        </div>
    </div>
</asp:Content>
