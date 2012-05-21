//#########################################################################
//# 
//# Copyright 2012 Cloud Sidekick
//# __________________
//# 
//#  All Rights Reserved.
//# 
//# NOTICE:  All information contained herein is, and remains
//# the property of Cloud Sidekick and its suppliers,
//# if any.  The intellectual and technical concepts contained
//# herein are proprietary to Cloud Sidekick
//# and its suppliers and may be covered by U.S. and Foreign Patents,
//# patents in process, and are protected by trade secret or copyright law.
//# Dissemination of this information or reproduction of this material
//# is strictly forbidden unless prior written permission is obtained
//# from Cloud Sidekick.
//#
//#########################################################################

$(document).ready(function () {
    //any page that includes this script will get the following dialog inner code
    //but the page requires a placeholder div... called "storm_stop_dialog"
    var d = '<span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>' + 
    	'This will shut down, terminate and remove all Storm created Cloud resources on this Ecosystem.' +
        '	<br /><br />' +
        '	Are you sure?' +
        '	<br /><br />' +
        '	<input id="storm_stop_confirm" type="checkbox" /><label for="storm_stop_confirm">Yes, stop Storm.</label>' +
        '   <hr />' +
        '   <span id="stop_btn" class="floatright">Stop Storm</span>' +
        '</div>' +
        '<input type="hidden" id="storm_stop_dialog_ecosystem_id" />';

    $("#storm_stop_dialog").prepend(d);

    //dialog was drawn dynamically, have to do some bindings
    $("#stop_btn").button({ icons: { primary: "ui-icon-stop"}, disabled: true });
    $("#stop_btn").click(function () {
    	if ($(this).hasClass("ui-state-disabled")) { return false; }
		var confirm = ($('#storm_stop_confirm').attr('checked') == "checked" ? 1 : 0);
		if (confirm) {
	    	StopStorm();
    	}
    });

    $("#storm_stop_confirm").click(function () {
		var checked = ($('#storm_stop_confirm').attr('checked') == "checked" ? 1 : 0);
		if (checked) {
	    	$("#stop_btn").button("enable");
    	} else {
	    	$("#stop_btn").button( "option", "disabled", true );
    	}
    });

    //init the dialogs
    $("#storm_stop_dialog").dialog({
        autoOpen: false,
        modal: true,
        height: 250,
        width: 400,
        open: function (event, ui) { $(".ui-dialog-titlebar-close", ui).hide(); },
        buttons: {
            "Close": function () {
                CloseStopStormDialog();
            }
        }
    });

});

function ShowStopStormDialog(ecosystem_id) {
    $.unblockUI();
    $("#storm_stop_dialog_ecosystem_id").val(ecosystem_id);
    $("#storm_stop_dialog").dialog('open');
}

function CloseStopStormDialog() {
    $("#storm_stop_dialog").dialog('close');
	$('#storm_run_dialog_compatibility').attr('checked', '');
}

function StopStorm() {

    showPleaseWait();
    $("#update_success_msg").text("Stopping Storm...");

	//args are a json document too
	var ecosystem_id = $("#storm_stop_dialog_ecosystem_id").val();

	if (ecosystem_id.length == 36) {
		var args = '{"ecosystem_id":"' + ecosystem_id + '"}';
		
	    $.ajax({
	        async: false,
	        type: "POST",
	        url: "ecoMethods/wmCallStormAPI",
	        data: '{"sMethod":"stopstorm", "sArgs":"' + packJSON(args) + '"}',
	        contentType: "application/json; charset=utf-8",
	        dataType: "json",
	        success: function (response) {
	        	if (response.info) {
	    			showInfo(response.info);
	        	} else if (response.error) {
	        		showAlert(response.error);
	            } else if (response.xml != "") {
	                var data = unpackJSON(response.xml);
	                response_xml = $.parseXML(data);
	
					err = $(response_xml).find("error");
					response = $(response_xml).find("response");
	        	
		        	if (err.length > 0) {
	                	showAlert(err.find("code").text() + " : " + err.find("detail").text());
	                	CloseStopStormDialog(); 	        		        	
	                } else {
	                	//we don't do anything, just a message
	                	showInfo("Stop request is being processed...");
	                	$("#storm_status").text("Stop requested...");
	                	$("#show_stopstorm_btn").hide();
	                	CloseStopStormDialog(); 	        		        	
		        	}
		        } else {
					showAlert("Response was empty.  Stop Storm may not have been executed.");   
					CloseStopStormDialog();             		
				} 	
	        },
	        error: function (response) {
	            showAlert(response.responseText);
	        }
	    });
	}
		
	//shouldn't get here unless there are errors but unlock the page
	hidePleaseWait();
}
