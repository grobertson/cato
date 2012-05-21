<%@ Page Language="C#" AutoEventWireup="True" CodeBehind="taskPrint.aspx.cs" Inherits="Web.pages.taskPrint"
    MasterPageFile="~/pages/popupwindow.master" %>

<asp:Content ID="cHead" ContentPlaceHolderID="phHead" runat="server">
    <link href="../style/taskEdit.css" rel="stylesheet" type="text/css" />
    <link href="../style/taskView.css" rel="stylesheet" type="text/css" />
</asp:Content>
<asp:Content ID="cDetail" ContentPlaceHolderID="phDetail" runat="server">
    <div id="printable_content" class="printable_content">
        <center>
            <h3>
                <asp:Label ID="lblTaskNameHeader" runat="server"></asp:Label>
                <span id="version_tag">Version:
                    <asp:Label ID="lblVersionHeader" runat="server"></asp:Label></span></h3>
        </center>
        <asp:ImageButton ID="btnExport" Visible="false" runat="server" ImageUrl="../images/icons/pdficon_large.gif"
            OnClick="btnExport_Click" />
        <asp:HiddenField ID="hidExport" runat="server" />
        <div class="codebox">
            <span class="detail_label">Code:</span>
            <asp:Label ID="lblTaskCode" runat="server" CssClass="code" Style="font-size: 1.2em;"></asp:Label>
            <br />
            <span class="detail_label">Status: </span>
            <asp:Label ID="lblStatus" runat="server" CssClass="code" Style="font-size: 1.2em;"></asp:Label>
            <br />
            <span class="detail_label">Concurrent Instances:</span>
            <asp:Label ID="lblConcurrentInstances" runat="server" CssClass="task_details code"
                Style="font-size: 1.2em;"></asp:Label>
            <br />
            <span class="detail_label">Number to Queue:</span>
            <asp:Label ID="lblQueueDepth" runat="server" CssClass="task_details code" Style="font-size: 1.2em;"></asp:Label>
            <br />
            <span class="detail_label">Description:</span>
            <br />
            <asp:Label ID="lblDescription" TextMode="MultiLine" Rows="10" runat="server" CssClass="code"
                Style="font-size: 1.2em;"></asp:Label>
            <!-- *** Commented out per Bug 1029 ***
                     <asp:Label ID="lblDirect" runat="server" CssClass="code"></asp:Label>
                        Direct to Asset?<br />-->
        </div>
        <hr />
		<div id="div_parameters">
            <div id="div_taskxml" class="ui-state-default"><h3>Parameters</h3></div>
            <asp:PlaceHolder ID="phParameters" runat="server"></asp:PlaceHolder>
        </div>
        <hr />
        <div id="div_steps">
            <div id="div_taskxml" class="ui-state-default"><h3>Steps</h3></div>
            <ul id="codeblock_steps">
                <asp:PlaceHolder ID="phSteps" runat="server"></asp:PlaceHolder>
            </ul>
        </div>
		<div id="div_taskxml">
            <div id="div_taskxml" class="ui-state-default"><h3>Task XML</h3></div>
			<pre><asp:Literal ID="ltXML" runat="server"></asp:Literal></pre>
        </div>
    </div>
</asp:Content>
