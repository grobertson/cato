<%@ Page Language="C#" AutoEventWireup="true" Inherits="Web.pages.taskCommandHelp"
    MasterPageFile="~/pages/popupwindow.master" %>

<asp:Content ID="cHead" ContentPlaceHolderID="phHead" runat="server">
    <link type="text/css" href="../style/taskEdit.css" rel="stylesheet" />
    <link type="text/css" href="../style/taskSteps.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="cDetail" ContentPlaceHolderID="phDetail" runat="server">
    <div class="embedded_step_header">
        <div class="step_header_title">
            Command Help</div>
    </div>
	<div>
		<asp:Literal id="ltHelp" runat="server"></asp:Literal>
	</div>
</asp:Content>
