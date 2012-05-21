<%@ Page Language="C#" AutoEventWireup="True" MasterPageFile="~/pages/site.master"
    CodeBehind="ecoTemplateEdit.aspx.cs" Inherits="Web.pages.ecoTemplateEdit" %>
<asp:Content ID="cHead" ContentPlaceHolderID="phHead" runat="server">
    <link type="text/css" href="../style/taskEdit.css" rel="stylesheet" />
    <link type="text/css" href="../style/taskView.css" rel="stylesheet" />
    <link type="text/css" href="../style/ecoTemplateEdit.css" rel="stylesheet" />
    <script type="text/javascript" src="../script/toolbox.js"></script>
    <script type="text/javascript" src="../script/storm.js"></script>
    <script type="text/javascript" src="../script/stormRunDialog.js"></script>
    <script type="text/javascript" src="../script/parametersOnDialog.js"></script>
    <script type="text/javascript" src="../script/ecoTemplateEdit.js"></script>
    <script type="text/javascript" src="../script/stormEcotemplateEdit.js"></script>
	<!--for jsonlint-->
	<script type="text/javascript" src="../script/jsonlint/c/js/json2.js"></script>
    <script type="text/javascript" src="../script/jsonlint/c/js/jsl.parser.js"></script>
    <script type="text/javascript" src="../script/jsonlint/c/js/jsl.format.js"></script>
    <script type="text/javascript" src="../script/jsonlint/c/js/jsl.interactions.js"></script>
	<!--end jsonlint-->
</asp:Content>
<asp:Content ID="cDetail" ContentPlaceHolderID="phDetail" runat="server">
    <div id="left_panel_te">
        <div id="toolbox">
            <div id="toolbox_tabs" class="toolbox_tabs_1row">
                <span id="tab_details" linkto="div_details" class="ui-state-default ui-corner-top ui-state-active toolbox_tab">Details</span><span 
					id="tab_storm" linkto="div_storm" class="ui-state-default ui-corner-top toolbox_tab storm">Storm</span><span 
					id="tab_tasks" linkto="div_tasks" class="ui-state-default ui-corner-top toolbox_tab">Tasks</span><span 
					id="tab_ecosystems" linkto="div_ecosystems" class="ui-state-default ui-corner-top toolbox_tab">Ecosystems</span>
            </div>
            <div id="div_details" class="toolbox_panel">
                <div style="padding: 0 0 0 5px;">
                    <span class="detail_label">Name:</span>
                    <asp:TextBox ID="txtEcoTemplateName" runat="server" CssClass="task_details code" te_group="detail_fields" column="Name"></asp:TextBox>
                    <br />
                    <span class="detail_label">Description:</span>
                    <br />
                    <asp:TextBox ID="txtDescription" TextMode="MultiLine" Rows="5" runat="server" CssClass="code" te_group="detail_fields" column="Description"></asp:TextBox>
                    <br />
                    <br />
                    <hr />
					<center>
						<span id="show_log_link">View Change Log</span>
					</center>
                </div>
            </div>
            <div id="div_storm" class="toolbox_panel hidden">
                <div style="padding: 0 0 0 5px;">
                    <img src="../images/icons/storm_32.png" /><span class="detail_label">Storm File</span>
                    <hr />
                    <span class="detail_label">Source: </span><span id="storm_file_source"></span>
					<div id="storm_file_url"></div>
					<br />
                    <span class="detail_label">Description:</span>
                    <div id="storm_file_desc">Getting Storm File ...</div>
					<hr />
					<center>
						<span id="edit_storm_btn">Edit Storm</span><span id="run_storm_btn">Run Storm</span>
					</center>
                </div>
            </div>
            <div id="div_tasks" class="toolbox_panel hidden">
                <div style="padding: 0 0 0 5px;">
                    <span>Search:</span>
                    <input id="task_search_text" />
                    <span id="task_search_btn">Search</span>
                    <div id="task_picker_results">
                    </div>
                </div>
            </div>
            <div id="div_ecosystems" class="toolbox_panel hidden">
                <div style="padding: 0 0 0 5px;">
                    <span id="ecosystem_create_btn">New Ecosystem</span>
                    <hr />
                    <div id="ecosystem_results">
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div id="content_te">
        <center>
            <h3>
                <asp:Label ID="lblEcoTemplateHeader" runat="server"></asp:Label>
            </h3>
        </center>
       	 <div id="div_details_detail" class="detail_panel">
	        <div id="all">
	            <div class="ui-state-default te_header">
	                <div class="step_section_title">
	                    <span id="step_toggle_all_btn" class="pointer">
	                    <img class="step_toggle_all_btn" src="../images/icons/expand.png" alt="Expand/Collapse All Tasks" title="Expand/Collapse All Tasks" />
	                    </span>
	                    <span class="step_title">
	                        <asp:Label ID="lblActionTitle" runat="server"></asp:Label>
	                    </span>
	                </div>
	                <div class="step_section_icons">
	                    <span id="print_link" class="pointer">
	                    <img class="task_print_link" alt="" src="../images/icons/printer.png" />
	                    </span>
	                </div>
	            </div>
	            <div id="actions">
	                <div id="action_add" class="ui-widget-content ui-corner-all ui-state-active">
	                    <div id="action_name_helper">
	                        Drag a Task from the Tasks tab here to create a new Action.
	                    </div>
	                    <div id="action_add_form" class="ui-widget-content hidden">
	                        <input type="hidden" id="action_add_otid" />
	                        <div class="ui-state-default">
	                            Task: <span id="action_add_task_name"></span>
	                        </div>
	                        Action:
	                        <input id="new_action_name" />
	                        <br />
	                        <span id="action_add_btn">Add</span> <span id="action_add_cancel_btn">Cancel</span>
	                    </div>
	                </div>
	                <ul class="category_actions" id="category_actions">
	                    <asp:PlaceHolder ID="phActions" runat="server"></asp:PlaceHolder>
	                </ul>
	            </div>
	        </div>
		</div>
        <div id="div_storm_detail" class="detail_panel hidden">
			<div class="ui-widget-content ui-corner-all">
				<div class="ui-state-default step_header">
					<div class="step_header_title"><span class="action_name_lbl">Storm File</span></div>
				</div>
				<pre id="storm_file_error" class="ui-state-highlight hidden"></pre>
				<pre><div id="storm_file_text"></div></pre>
			</div>
		</div>
	</div>
    <div class="hidden">
        <input type="hidden" id="hidParamType" value="task" />
        <asp:HiddenField ID="hidEcoTemplateID" runat="server"></asp:HiddenField>
    </div>
    <div id="task_remove_confirm_dialog" title="Remove Task" class="hidden ui-state-highlight">
        <p>
            <span class="ui-icon
    ui-icon-info" style="float: left; margin: 0 7px 50px 0;"></span><span>Are you sure you
            want to remove this Task?</span>
        </p>
    </div>
    <div id="action_delete_confirm_dialog" title="Delete Action" class="hidden ui-state-highlight">
        <p>
            <span class="ui-icon
    ui-icon-info" style="float: left; margin: 0 7px 50px 0;"></span><span>Are you sure you
            want to delete this Action?</span>
        </p>
    </div>
    <div id="action_edit_dialog" title="Edit Action" class="hidden">
        <p>
            Name:
        </p>
        <input id="txtActionNameAdd" />
    </div>
    <div id="action_parameter_dialog" title="Edit Parameters" class="hidden">
        <div id="action_parameter_dialog_params">
        </div>
        <input type="hidden" id="action_parameter_dialog_action_id" />
    </div>
    <div id="ecosystem_add_dialog" class="hidden" title="New Ecosystem">
        <table width="100%">
            <tbody>
                <tr>
                    <td>
                        Name
                    </td>
                    <td>
                        <input type="text" id="new_ecosystem_name" class="w300px" />
                    </td>
                </tr>
                <tr>
                    <td>
                        Description
                    </td>
                    <td>
                        <textarea id="new_ecosystem_desc" rows="3"></textarea>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    <div id="storm_run_dialog" title="Run Storm" class="hidden"></div>
    <div id="storm_edit_dialog" title="Edit Storm" class="hidden">
		<select id="storm_edit_dialog_type"><option>URL</option><option>Text</option><option>File</option></select>
		<span id="url_to_text_btn" class="hidden">Convert to Text</span>
        <div class="stormfileimport hidden">
            <iframe src="fileUpload.aspx?ref_id=new_template" style="width: 100%; height: 28px;"></iframe>
		</div>
		<textarea id="storm_edit_dialog_text" class="code w100pct" rows="25"></textarea>
		<div class="validation">
			<span id="validate">Validate</span><input type="checkbox" id="chk_reformat" checked="checked" /><label for="chk_format">Format?</label>
			<pre id="json_parse_msg"></pre>
		</div>
	</div>
    <div id="action_icon_dialog" title="Action Icon" class="hidden">
		<div id="action_icons">
			<asp:Literal id="ltActionPickerIcons" runat="server"></asp:Literal>
		</div>
		<input type="text" id="selected_action_id" class="hidden" />
		<input type="text" id="selected_action_icon" class="hidden" />
	</div>
</asp:Content>