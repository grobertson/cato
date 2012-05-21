<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="fileUpload.aspx.cs"
    Inherits="Web.pages.fileUpload" %>
<html>
	<head>
		<script type="text/javascript" src="../script/jquery/jquery-1.6.1.js"></script>
    	<script type="text/javascript" src="../script/jquery/jquery-ui-1.8.12.js"></script>
		<link rel="stylesheet" type="text/css" href="../style/jquery-ui-1.8.13.custom.css" />		
		<style type="text/css">
		<!--
		input:focus {
			background-color: transparent;
		}
		
		div.fileinputs {
			position: relative;
			height: 30px;
			width: 220px;
		}
		
		input.file {
			width: 220px;
			margin: 0;
		}
		
		input.file.invisible {
			position: relative;
			text-align: right;
			-moz-opacity:0 ;
			filter:alpha(opacity: 0);
			opacity: 0;
			z-index: 2;
		}
		
		div.fakefile {
			position: absolute;
			top: 0px;
			left: 0px;
			width: 220px;
			padding: 0;
			margin: 0;
			z-index: 1;
			line-height: 90%;
		}
		
		div.fakefile input {
			margin-bottom: 5px;
			margin-left: 0;
		}
		-->
		</style>
		<script type="text/javascript">
		<!--
		
		var W3CDOM = (document.createElement && document.getElementsByTagName);
		
		function init() {
			if (!W3CDOM) return;
			var fakeFileUpload = document.createElement('div');
			fakeFileUpload.className = 'fakefile';
			fakeFileUpload.appendChild(document.createElement('input'));
			var btn = document.createElement('input');
			btn.type='button';
			btn.value='Select';
			btn.className='ui-widget ui-state-default ui-corner-all ui-button-text-only';
			btn.style.fontWeight='normal';
			btn.style.fontSize='10pt';
			btn.style.marginLeft='4px';
			fakeFileUpload.appendChild(btn);
			var x = document.getElementsByTagName('input');
			for (var i=0;i<x.length;i++) {
				if (x[i].type != 'file') continue;
				if (x[i].getAttribute('noscript')) continue;
				if (x[i].parentNode.className != 'fileinputs') continue;
				x[i].className = 'file invisible';
				var clone = fakeFileUpload.cloneNode(true);
				x[i].parentNode.appendChild(clone);
				x[i].relatedElement = clone.getElementsByTagName('input')[0];
				if (x[i].value)
					x[i].onchange();
				x[i].onchange = x[i].onmouseout = function () {
					this.relatedElement.value = this.value;
				}
			}
		}
		
		function fileWasSaved(filename) {
			parent.fileWasSaved(filename);
		}
		// -->
		
		</script>	
	</head>
	<body style="margin: 0px; padding: 0px;">
		<form id="Form1" method="post" enctype="multipart/form-data" runat="server">
	        <asp:ScriptManager ID="ScriptManager" runat="server" EnablePageMethods="true">
	        </asp:ScriptManager>
			<table>
				<tr>
					<td>
						<div class="fileinputs">
							<input type="file" class="file" id="fupFile" runat="server" />
						</div>
					</td>
					<td>
						<asp:Button CssClass="ui-widget ui-state-default ui-corner-all ui-button-text-only" Style="margin-top: -10px; font-weight: normal; font-size: 10pt;" ID="btnImport" runat="server" Text="Load" OnClick="btnImport_Click" />
					</td>
				</tr>
			</table>
		</form>
		<script type="text/javascript">init();</script>
	</body>
</html>		