<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="home.aspx.cs" Inherits="Web.pages.home"
    MasterPageFile="~/pages/site.master" %>

<asp:Content ID="cHead" ContentPlaceHolderID="phHead" runat="server">
<script type="text/javascript" src="../script/home.js"></script>	
	<style type="text/css">	
        #getting_started
        {
            padding: 20px;
			width: 500px;
			margin-left: auto;
			margin-right: auto;
        }
    </style>
</asp:Content>
<asp:Content ID="cDetail" ContentPlaceHolderID="phDetail" runat="server">
    <div id="fullwidthcontent">
		<asp:Panel id="pnlGettingStarted" runat="server">
		    <div id="getting_started" class="ui-widget-content ui-corner-all">
				<h1>Welcome to Cloud Sidekick Cato!</h1>
				<p>There are just a few more things you need to do to get started.</p>
				<asp:Literal id="ltGettingStartedItems" runat="server"></asp:Literal>
			</div>
		</asp:Panel>
	</div>
</asp:Content>
