<%@ Page Language="C#" AutoEventWireup="True" MasterPageFile="~/pages/site.master"
    CodeBehind="ecosystemEdit.aspx.cs" Inherits="Web.pages.ecosystemEdit" %>

<asp:Content ID="cHead" ContentPlaceHolderID="phHead" runat="server">
    <script type="text/javascript" src="../script/storm.js"></script>
    <script type="text/javascript" src="../script/ecosystemEdit.js"></script>
    <script type="text/javascript" src="../script/toolbox.js"></script>
    <script type="text/javascript" src="../script/taskedit/taskEditParams.js"></script>
    <script type="text/javascript" src="../script/parametersOnDialog.js"></script>
    <script type="text/javascript" src="../script/taskLaunchDialog.js"></script>
    <script type="text/javascript" src="../script/stormStopDialog.js"></script>
    <script type="text/javascript" src="../script/registry.js"></script>
    <link type="text/css" href="../style/taskEdit.css" rel="stylesheet" />
    <link type="text/css" href="../style/taskView.css" rel="stylesheet" />
    <link type="text/css" href="../style/ecosystemEdit.css" rel="stylesheet" />
    <link type="text/css" href="../style/registry.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="cDetail" ContentPlaceHolderID="phDetail" runat="server">
    <div id="left_panel_te">
        <div id="toolbox">
            <div id="toolbox_tabs" class="toolbox_tabs_1row">
                <span id="tab_details" linkto="div_details" class="ui-state-default ui-corner-top toolbox_tab">Details</span><span 
					id="tab_objects" linkto="div_objects" class="ui-state-default ui-corner-top toolbox_tab">Objects</span><span
                    id="tab_actions" linkto="div_actions" class="ui-state-default ui-corner-top ui-tabs-selected ui-state-active toolbox_tab">Actions</span>
            </div>
            <div id="div_details" class="toolbox_panel hidden">
                <div style="padding: 0 0 0 5px;">
                    <span class="detail_label">Template:</span><br />
                    <asp:Label ID="lblEcotemplateName" runat="server" CssClass="code"></asp:Label><span
                        id="view_ecotemplate_btn" class="pointer">
                        <img alt="" src="../images/icons/edit_16.png" />
                    </span>
                    <br />
                    <span class="detail_label">Name:</span><br />
                    <asp:TextBox ID="txtEcosystemName" runat="server" CssClass="task_details code" te_group="detail_fields" column="Name" validate_as="identifier"></asp:TextBox>
                    <br />
                    <span class="detail_label">Description:</span><br />
                    <asp:TextBox ID="txtDescription" TextMode="MultiLine" Rows="10" runat="server" te_group="detail_fields"
                        column="Description" CssClass="task_details code">
                    </asp:TextBox>
                    <hr />
					<center>
						<span id="show_log_link">View Change Log</span>						
					</center>
                </div>
            </div>
            <div id="div_objects" class="toolbox_panel hidden">
                <!-- I imagine the actions for a specific object would go here. -->
            </div>
            <div id="div_actions" class="toolbox_panel">
                <span class="detail_label">Select a Category:</span>
                <div id="action_categories">
                </div>
            </div>
        </div>
    </div>
    <div id="content_te">
        <center>
            <h3>
                <asp:Label ID="lblEcosystemNameHeader" runat="server"></asp:Label>
            </h3>
        </center>
        <div id="div_objects_detail" class="detail_panel hidden">
            <div class="ui-state-default te_header">
                <div class="step_section_title">
                    <span class="step_title" id="breadcrumbs"><span class="breadcrumb" id="top"><span
                        class="ui-icon ui-icon-arrowreturnthick-1-w floatleft"></span>Ecosystem Objects</span></span>
                </div>
                <div class="step_section_icons">
                </div>
            </div>
            <div id="random_content">
                <asp:Literal ID="ltItems" runat="server"></asp:Literal>
            </div>
        </div>
        <div id="div_actions_detail" class="detail_panel">
            <table id="action_flow">
            </table>
            <div class="category_actions hidden" id="category_actions">
            </div>
        </div>
        <div id="div_details_detail" class="detail_panel hidden">
            <!-- temporarily hiddend until enabled in the CE
           also see line 120is of ecosystemEdit.js

           <div id="div_parameters" class="ui-widget-content ui-corner-bottom">
                <div class="ui-state-default h18px">
                    <div class="floatleft">
                        <span class="detail_label">Parameters</span>
                    </div>
                    <div class="floatright">
                        <span id="parameter_add_btn">Add New</span>
                    </div>
                </div>
                <div id="parameters">
                </div>
            </div>
            <hr />
            -->
            <div id="registry_content">
            </div>
            <hr />
	        <div class="ui-widget-content ui-corner-all">
	            <div class="ui-widget-header">
	                <span>Scheduling</span>
				</div>
				<div style="padding: 5px;">	
	                <div id="ecosystem_schedules">
	                    There are no Actions scheduled to run on this Ecosystem.
	                </div>
				</div>
            </div>
            <hr />
	        <div class="ui-widget-content ui-corner-all">
	            <div class="ui-widget-header">
	                <span>Upcoming Actions</span>
				</div>
				<div style="padding: 5px;">	
	                <div id="ecosystem_plans">
	                    There are no pending Actions on this Ecosystem.
	                </div>
				</div>
			</div>
            <hr />
	        <div id="storm_detail_tabs" class="storm" style="height: 400px;">
	            <ul>
	                <li><a href="#storm_status_tab"><span><img src="../images/icons/storm_32.png" style="height: 16px; width: 16px; vertical-align: middle; padding-right: 6px;"/>Storm</span></a></li>
	                <li><a href="#storm_file_tab"><span>Template</span></a></li>
	                <li><a href="#storm_events_tab"><span>Events</span></a></li>
	                <li><a href="#storm_output_tab"><span>Output</span></a></li>
	                <li><a href="#storm_params_tab"><span>Parameters</span></a></li>
	            </ul>
		        <div id="storm_status_tab">
                    <div class="detail_label">Status: <span id="storm_status"></span><span class="reload_storm_btn"></span></div>
					<br /><br /><br />
					<span id="show_stopstorm_btn">Stop Storm</span>
		        </div>
		        <div id="storm_file_tab">
					<asp:TextBox ID="txtStormFile" TextMode="MultiLine" Rows="18" runat="server" CssClass="w100pct code" ReadOnly="True"></asp:TextBox>
		        </div>
		        <div id="storm_events_tab">
		            <div class="ui-widget-header">
	                    <div class="floatleft">
	                    </div>
	                    <div class="floatright">
	                        <span class="reload_storm_btn"></span>
	                    </div>
	                        <span>Storm Events</span>
					</div>
					<div style="height: 330px; overflow: auto;">	
			            <table id="ecosystem_log"  class="jtable" cellspacing="1" cellpadding="1" width="100%">
							<thead>
								<th>Type</th>
								<th>ID</th>
								<th>Logical ID</th>
								<th>Status</th>
								<th>Log</th>
								<th>Last Update</th>
							</thead>
			            </table>
			        </div>
		        </div>
		        <div id="storm_output_tab">
		            <div class="ui-widget-header">
	                    <div class="floatleft">
	                    </div>
	                    <div class="floatright">
	                        <span class="reload_storm_btn"></span>
	                    </div>
	                        <span>Storm Output</span>
					</div>
					<div>	
			            <table id="storm_output"  class="jtable" cellspacing="1" cellpadding="1" width="100%">
							<thead>
								<th>Name</th>
								<th>Description</th>
								<th>Value</th>
							</thead>
			            </table>
			        </div>
		        </div>
		        <div id="storm_params_tab">
					<div>	
			            <table id="storm_parameters"  class="jtable" cellspacing="1" cellpadding="1" width="100%">
							<thead>
								<th>Name</th>
								<th>Value</th>
							</thead>
			            </table>
			        </div>
		        </div>
        	</div>
		</div>
    </div>
    <div class="te_container_footer">
        <!--The footer has to be here so some element can contain the 'clear:both;' style.-->
    </div>
    <div class="hidden">
        <asp:HiddenField ID="hidEcosystemID" runat="server"></asp:HiddenField>
        <asp:HiddenField ID="hidEcoTemplateID" runat="server"></asp:HiddenField>
        <asp:HiddenField ID="hidParamDelete" runat="server"></asp:HiddenField>
        <input type="hidden" id="hidParamType" value="ecosystem" />
        <input type="hidden" id="selected_object_type" value="" />
    </div>
    <div id="task_launch_dialog" title="Perform Action">
        <div id="plan_edit_dialog" title="Edit Plan">
        </div>
    </div>
    <div id="param_edit_dialog" title="Parameter">
    </div>
    <div id="param_delete_confirm_dialog" title="Remove Parameter">
    </div>
    <!-- Registry dialogs. -->
    <div id="reg_edit_dialog" class="hidden">
    </div>
    <div id="reg_add_dialog" class="hidden">
    </div>
    <input type="hidden" id="reg_type" value="ecosystem" />
    <!-- End Registry dialogs.-->
    <!-- Storm dialogs.-->	
	<div id="storm_stop_dialog" title="Stop Storm" class="hidden"></div>
    <!-- End Storm dialogs.-->	
</asp:Content>
