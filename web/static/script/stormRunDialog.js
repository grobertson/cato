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
    //but the page requires a placeholder div... called "storm_run_dialog"
    var d = '<div id="storm_run_dialog_parameters" class="floatleft task_launch_column ui-widget-content ui-tabs ui-corner-all">' +
                '   <div id="storm_run_params_content">' +
                '       <div class="task_launch_params_title ui-widget-header ui-corner-all">' +
                '       Parameters' +
                '       </div>' +
                '       <div id="storm_run_dialog_params"></div>' +
                '   </div>' +
                '</div>' +
                '<div id="storm_run_dialog_ecosystem" class="floatright task_launch_column ui-widget-content ui-tabs ui-corner-all">' +
            	'   <div class="task_launch_params_title ui-widget-header ui-corner-all">' +
                '       Ecosystem' +
                '   </div>' +
                '	Name:<br />' +
                '	<input type="text" id="storm_run_dialog_ecosystem_name" style="width: 95%;" validate_as="identifier" />' +
                '	<br />Description:<br />' +
                '	<textarea id="storm_run_dialog_ecosystem_desc"></textarea>' +
                '	<br /><br />Cloud: ' +
                '	<select id="storm_run_dialog_clouds"></select>' +
                '	<br /><br />Compatibility: ' +
                '	<input id="storm_run_dialog_compatibility" type="checkbox" /><label for="storm_run_dialog_compatibility">Strict AWS?</label>' +
                '   <hr />' +
                '   <span id="run_btn" class="floatright">Run</span>' +
                '</div>' +
                '<input type="hidden" id="storm_run_dialog_ecotemplate_id" />';

    $("#storm_run_dialog").prepend(d);

    //dialog was drawn dynamically, have to do some bindings
    $("#run_btn").button({ icons: { primary: "ui-icon-play"} });
    $("#run_btn").live("click", function () {
		if (checkParamConstraints() == true)
	    	RunStorm();
    });

    //init the dialogs
    $("#storm_run_dialog").dialog({
        autoOpen: false,
        modal: true,
        height: 650,
        width: 900,
        open: function (event, ui) { $(".ui-dialog-titlebar-close", ui).hide(); },
        buttons: {
            "Close": function () {
                CloseRunStormDialog();
            }
        }
    });

});

//check parameters before running
//NOTE: this is different than the checkRequiredParameters on a task or action launch.  
// in those cases we're checking our "required" flag... here we're more specific.
// in the future we'll make the task params more specific too.
function checkParamConstraints() {
	//look over the parameters and do their constraint checking
	
	var msg = "";
	
	if ($(".task_launch_parameter_value_input").length > 0) {
		var warn = false;
		$(".task_launch_parameter_value_input").each(function(){
			msg += checkFieldConstraints($(this));
		});
	
		if (msg.length > 0) {
			return false;
		} else {
			return true;
		}
	} else
		return true; //there are no parameters
}

function getParamsFromJSON() {
    //we gotta get the parameters from the json and convert it to xml so we can display it using our standard parametersOnDialog routine.
    //conversion is server side, so we don't have to deal with browser nuances
    var storm_parameter_xml = "";
    var ecotemplate_id = $("#storm_run_dialog_ecotemplate_id").val();
    
    $.ajax({
        async: false,
        type: "POST",
        url: "ecoMethods/wmGetEcotemplateStormParameterXML",
        data: '{"sEcoTemplateID":"' + ecotemplate_id + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "xml",
        success: function (storm_parameter_xml) {
            if (storm_parameter_xml == "") {
            	//it's ok to have a file with no parameters.
				$("#storm_run_dialog_params").html('<div id="no_storm_msg" class="ui-state-highlight">' +
					'The Storm did not contain any parameters.  Check and validate the text, or verify the URL.<br /><br />' +
					'Parameters are not required - if the Storm valid you may proceed.</div>');         	
            } else {
                $("#no_storm_msg").remove();

			    var output = DrawParameterEditForm(storm_parameter_xml);
			    $("#storm_run_dialog_params").html(output);
			
			    //don't forget to bind the tooltips!
			    bindParameterToolTips();
            }
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
    
    return;
}

function getClouds() {
	var account_id = $("#header_cloud_accounts").val();
	var has_clouds = false;
	
	if (account_id) {
	    $.ajax({
	        type: "POST",
	        async: false,
	        url: "cloudMethods/wmGetCloudAccount",
	        data: '{"sID":"' + account_id + '"}',
	        contentType: "application/json; charset=utf-8",
	        dataType: "json",
	        success: function (account) {
	            //update the list in the dialog
	        	if (account.info) {
	    			showInfo(account.info);
	        	} else if (account.error) {
	        		showAlert(account.error);
	            } else {
		            // all we want here is to loop the provider clouds
		            $("#storm_run_dialog_clouds").empty();
		            $.each(account.Clouds, function(id, cloud){
		            	$("#storm_run_dialog_clouds").append("<option value=\"" + id + "\">" + cloud.Name + "</option>");
					});
					
					//we can't allow running the storm if there are no clouds
					if ($("#storm_run_dialog_clouds option").length == 0) {
						$("#run_btn").before('<div id="no_cloud_msg" class="ui-state-highlight">' +
							'Running Storm requires at least one Cloud, but no Clouds are defined.' +
							'<br /><br />Click <a href="cloudEdit.aspx">here</a> to define a Cloud.</div>');
					} else {
						has_clouds = true;
						$("#no_cloud_msg").remove();
		        	}
	        	}
	        },
	        error: function (response) {
	            showAlert(response.responseText);
	        }
	    });
	} else {
		$("#run_btn").before('<div id="no_cloud_msg" class="ui-state-highlight">' +
			'Running Storm requires a Cloud Account, but none are defined.' +
			'<br /><br />Click <a href="cloudAccountEdit.aspx">here</a> to define a Cloud Account.</div>');
	}
	
	return has_clouds;
}

function ShowRunStormDialog(ecotemplate_id) {
	if (!ecotemplate_id || ecotemplate_id.length != 36) {
		showAlert("Cannot show Run Storm dialog without a valid EcoTemplate ID.");
		return;
	}
	
	$("#storm_run_dialog_ecotemplate_id").val(ecotemplate_id);
	
	var proceed = false;
	
    proceed = getClouds();

	if (proceed) {
		getParamsFromJSON();
		$("#run_btn").show();
	} else {
		$("#run_btn").hide();
	}

    $.unblockUI();
    $("#storm_run_dialog").dialog('open');
}

function CloseRunStormDialog() {
    $("#storm_run_dialog").dialog('close');
    $("#storm_run_dialog_params").empty();

    //empty every input on the dialog
    $('#storm_run_dialog :input').each(function () {
        var type = this.type;
        var tag = this.tagName.toLowerCase(); // normalize case
        if (type == 'text' || type == 'password' || tag == 'textarea')
            this.value = "";
        else if (type == 'checkbox' || type == 'radio')
            this.checked = false;
        else if (tag == 'select')
            this.selectedIndex = 0;
    });


    return false;
}
function RunStorm() {

    showPleaseWait();
    $("#update_success_msg").text("Running Storm...");

    var ecotemplate_id = $("#storm_run_dialog_ecotemplate_id").val();
    
	//First things first... create an Ecosystem.
	var ecosystem_id = CreateEcosystem();
	if (ecosystem_id.length == 36) {
		//we have a guid!  yay.
		var ecosys_url = "ecosystemEdit?tab=details&ecosystem_id=" + ecosystem_id;
		
		var strict = ($('#storm_run_dialog_compatibility').attr('checked') == "checked" ? 1 : 0);
		
		//args are a json document too
		var args = '{"ecosystem_id":"' + ecosystem_id + '", "aws_strict" : "' + strict + '"}';
		
	    $.ajax({
	        async: false,
	        type: "POST",
	        url: "ecoMethods/wmCallStormAPI",
	        data: '{"sMethod":"runstorm", "sArgs":"' + packJSON(args) + '"}',
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
	                } else {
	                	//must be good... did we get an ecosystem_id back?
	                	var token = response.find("EcosystemId").text();

                		//we got an ecosystem id back - it should match what we sent.
	                	if (token == ecosystem_id) {
	                		location.href = ecosys_url;
	                	} else {
	                		showAlert("Reponse was not an error, but not an Ecosystem ID either.");                		
	                	}		        		        	
		        	}
		        } else {
					showAlert("Response was empty.  Ecosystem was created, but Storm may not have started.<br /><br /><a href='" + ecosys_url + "'>Click here</a> to go to the Ecosystem.");                		
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

function CreateEcosystem() {
    var ecotemplate_id = $("#storm_run_dialog_ecotemplate_id").val();
    var cloud_id = $("#storm_run_dialog_clouds").val();

    var bSave = true;

	var ecosystem_name = $("#storm_run_dialog_ecosystem_name").val();
    if (ecosystem_name == "") {
        bSave = false;
    	$("#storm_run_dialog_ecosystem_name").after("<div class=\"constraint_msg ui-state-highlight\">Ecosystem Name is required.</div>");
    } else {
    	$("#storm_run_dialog_ecosystem_name").next(".constraint_msg").remove();
	}


    //we will test it, but really we're not gonna use it rather we'll get it server side
    //this just traps if there isn't one.
    if ($("#header_cloud_accounts")[0].length == 0) {
        bSave = false;
    	$("#storm_run_dialog_clouds").after("<div class=\"constraint_msg ui-state-highlight\">Ecosystems by Storm require a Cloud Account.  Create a Cloud first.</div>");
    } else {
    	$("#storm_run_dialog_clouds").next(".constraint_msg").remove();
    };

    if (bSave != true) {
        return "";
    }

	var account_id = $("#header_cloud_accounts").val();
	var ecosystem_desc = packJSON($("#storm_run_dialog_ecosystem_desc").val());
    var parameter_xml = packJSON(buildXMLToSubmit());
	var ecosystem_id = "";
	
    $.ajax({
        async: false,
        type: "POST",
        url: "ecoMethods/wmCreateEcosystem",
        data: '{"sName":"' + packJSON(ecosystem_name) + '","sDescription":"' + ecosystem_desc + '","sEcotemplateID":"' + ecotemplate_id + '","sAccountID":"' + account_id + '","sParameterXML":"' + parameter_xml + '","sCloudID":"' + cloud_id + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (response) {
        	if (response.info) {
    			showInfo(response.info);
        	} else if (response.error) {
        		showAlert(response.error);
            } else if (response.id) {
                ecosystem_id = response.id;
            } else {
                showAlert(response);
                hidePleaseWait();
            }
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
    
    return ecosystem_id;
}
