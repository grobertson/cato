<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="importLoadFile.aspx.cs"
    Inherits="Web.pages.importLoadFile" MasterPageFile="~/pages/site.master" %>

<asp:Content ID="cHead" ContentPlaceHolderID="phHead" runat="server">
<script>
$(document).ready(function () {
	$("#import_xml_btn").button({ icons: { primary: "ui-icon-check"} });
    $("#import_xml_btn").click(function() {
		var xml = packJSON($("#xml_to_import").val());
	    $.ajax({
	        type: "POST",
	        async: false,
	        url: "uiMethods.asmx/wmCreateObjectFromXML",
	        data: '{"sXML":"' + xml + '"}',
	        contentType: "application/json; charset=utf-8",
	        dataType: "json",
	        success: function (response) {
				try
				{
		            var resp = jQuery.parseJSON(response.d);
		        	if (resp) {
			        	if (resp.error) {
		        			showAlert(resp.error);
		        		} else {
							$("#xml_to_import").val("");
							if (resp.ids.length = 1)
							{
								var url = "";
								if (resp.type == "task")
									url = "taskEdit.aspx?task_id=" + resp.ids[0];
								if (resp.type == "ecotemplate")
									url = "ecoTemplateEdit.aspx?ecotemplate_id=" + resp.id[0];
								
								showInfo("Success!", "Click <a href='" + url + "'>here</a> to edit.", true);
							} else {
								if (resp.type == "task")
									showInfo("Success!", "Click <a href='taskManage.aspx'>here</a> to manage Tasks.", true);
								if (resp.type == "ecotemplate")
									showInfo("Success!", "Click <a href='ecotemplateManage.aspx'>here</a> to manage Ecotemplates.", true);
							}
						}		
					}
				}
				catch(err)
				{
					showAlert(err);
				}
	        },
	        error: function (response) {
	            showAlert(response.responseText);
	        }
	    });
    });
});

function fileWasSaved(filename) {
	//get the file text from the server and populate the text field.
	//alert(filename);
    $.ajax({
        type: "POST",
        url: "uiMethods.asmx/wmGetFile",
        data: '{"sFileName":"' + filename + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (msg) {
            if (msg.d.length > 0) {
                var txt = unpackJSON(msg.d);
                $("#xml_to_import").val(txt);
            } else {
                showInfo(msg.d);
            }
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
}
</script>
</asp:Content>
<asp:Content ID="cDetail" ContentPlaceHolderID="phDetail" runat="server">
    <div id="content">
        <div class="ui-widget-content ui-corner-all">
            <div class="ui-widget-header">
                <span>Import a .csk backup package.</span>
			</div>
			<div style="padding: 5px;">	
			    Select a .csk Task bundle file to import.<br />
			    <input type="file" id="fupFile" runat="server" />
			    <asp:Button ID="btnImport" runat="server" Text="Load File" OnClick="btnImport_Click" />
			    <asp:Panel ID="pnlResume" runat="server">
			        -OR-<br />
			        <a href="importReconcile.aspx">Resume reconcilation of the last import session.
			        </a>
			    </asp:Panel>
			</div>
		</div>
	<hr />
        <div class="ui-widget-content ui-corner-all">
            <div class="ui-widget-header">
                <span>Edit and load an object definition.</span>
			</div>
			<div style="padding: 5px;">
				<iframe src="fileUpload.aspx?ref_id=new_template" style="width: 100%; height: 28px;"></iframe>	
				<textarea id="xml_to_import" class="w100pct code" rows="24"></textarea>
				<span id="import_xml_btn">Import</span>
			</div>
		</div>
    </div>
    <div id="left_panel">
        <div class="left_tooltip">
            <img src="../images/terminal-192x192.png" alt="" />
            <div id="left_tooltip_box_outer">
                <div id="left_tooltip_box_inner">
					<h2>Import</h2>
						<p>There are several ways to import data into Cato:</p>
                        <p>1) Select a "package" to import. (This will be a .csk file format.)</p>
                        <p>2) Select a single object backup file, edit, and import. (This will be a .xml file format.)</p>
                </div>
            </div>
        </div>
    </div>
</asp:Content>
