//Copyright 2011 Cloud Sidekick
// 
//Licensed under the Apache License, Version 2.0 (the "License");
//you may not use this file except in compliance with the License.
//You may obtain a copy of the License at
// 
//    http://www.apache.org/licenses/LICENSE-2.0
// 
//Unless required by applicable law or agreed to in writing, software
//distributed under the License is distributed on an "AS IS" BASIS,
//WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//See the License for the specific language governing permissions and
//limitations under the License.
//

//This is all the functions to support Storm on the ecoTemplateEdit page.
$(document).ready(function () {
    //Storm buttons
    $("#url_to_text_btn").button({ icons: { primary: "ui-icon-shuffle"} });
    $("#url_to_text_btn").click(function () {
		var storm = GetStorm(false);
	    if (storm != null) {
			$("#storm_edit_dialog_type").val("Text");
			$("#storm_edit_dialog_text").val(unpackJSON(storm.Text));
			$("#url_to_text_btn").hide();
    	}
    });

    $("#run_storm_btn").button({ icons: { primary: "ui-icon-play"} });
    $("#run_storm_btn").click(function () {
    	//check if the function to display the dialog exists
    	//otherwise show a message
        if (typeof(ShowRunStormDialog) != 'undefined') {
            ShowRunStormDialog(g_id);
        } else {
		    $("#run_storm_btn").hide();
    	}
    });

	//Storm File edit button and dialog
    $("#edit_storm_btn").button({ icons: { primary: "ui-icon-pencil"} });
    $("#edit_storm_btn").click(function () {
    	//check if the function to display the dialog exists
    	//otherwise show a message
        if (typeof(ShowEditStormDialog) != 'undefined') {
            ShowEditStormDialog();
        } else {
		    $("#edit_storm_btn").hide();
    	}
    });
    $("#storm_edit_dialog").dialog({
        autoOpen: false,
        modal: true,
        width: 800,
        height: 600,
        buttons: [
        	{
        		id: "storm_edit_dialog_ok_btn",
				text: "OK",
				click: function () {
                	SaveStormFile();
            	}
        	},
            {
            	text: "Cancel",
            	click: function () {
                	$(this).dialog('close');
            	}
        	}
        ]
    });

    //this onchange event will test the json text entry 
    //and display a little warning if it couldn't be parsed.
    $("#storm_edit_dialog_text").change(function () {
		validateStormFileJSON();
    });
    
    //changing the Source dropdown refires the validation
    $("#storm_edit_dialog_type").change(function () {
		validateStormFileJSON();
    });
});

function ShowStorm() {
	//gets the details of Storm and sets it up on the page    
    var storm = GetStorm(true);
    if (storm != null) {
        $("#storm_file_source").html(storm.FileType);
        $("#storm_file_url").html(unpackJSON(storm.URL));
        $("#storm_file_desc").html(unpackJSON(storm.Description));
        $("#storm_file_text").html(unpackJSON(storm.Text));
    
        //turn on the buttons
        $("#run_storm_btn").show();
        $("#edit_storm_btn").show();
	}
}

function GetStorm(format_for_html) {
    //gets the storm details for an Ecosystem, but several different functions consume the results
    var storm = null;
    
    $.ajax({
        async: false,
        type: "POST",
        url: "uiMethods.asmx/wmGetEcotemplateStorm",
        data: '{"sEcoTemplateID":"' + g_id + '","bFormatForHTML":"' + format_for_html + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (response) {
        	try
			{
				storm = jQuery.parseJSON(response.d);
				if (!storm) {
		            showAlert(response.d);
		        }
			}
			catch(err)
			{
				showAlert(err.message);
			}
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
    
    return storm;
}

function ShowEditStormDialog() {
	//get the details of the Storm and populate the edit dialog.
	var storm = GetStorm(false);
    if (storm != null) {
		$("#storm_edit_dialog_type").val(storm.FileType);
		
		//if it's a URL, we want to edit the URL, not the data.
		if (storm.FileType == "URL") {
			$("#storm_edit_dialog_text").val(unpackJSON(storm.URL));
			
			//show the url_to_text button
			$("#url_to_text_btn").show();
		} else {
			$("#storm_edit_dialog_text").val(unpackJSON(storm.Text));

			//hide the url_to_text button
			$("#url_to_text_btn").hide();
			
			validateStormFileJSON();
		}
		
	    $("#storm_edit_dialog").dialog('open');
	} else {
		showAlert("Unable to edit Storm.  Could not get Storm File.");
	}
}

function SaveStormFile() {
	var sfs = packJSON($("#storm_edit_dialog_type").val());
	var sf = packJSON($("#storm_edit_dialog_text").val());
	
    $.ajax({
        async: false,
        type: "POST",
        url: "uiMethods.asmx/wmUpdateEcotemplateStorm",
        data: '{"sEcoTemplateID":"' + g_id + '", "sStormFileSource":"' + sfs + '", "sStormFile":"' + sf + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (retval) {
            ShowStorm();
         	$("#storm_edit_dialog").dialog('close');
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });

}

function validateStormFileJSON() {
	if ($("#storm_edit_dialog_type").val() != "Text") {
		$("#json_parse_msg").empty().removeClass("ui-state-highlight").removeClass("ui-state-happy");			
		$("#storm_edit_dialog_ok_btn").button("enable");		
		return;
	}
	
	try
	{
		json = $.parseJSON($("#storm_edit_dialog_text").val());
		$("#json_parse_msg").empty();
		$("#json_parse_msg").text("Valid Storm File").addClass("ui-state-happy").removeClass("ui-state-highlight");
		$("#storm_edit_dialog_ok_btn").button("enable");		
	}
	catch(err)
	{
		var errmsg = err.message.replace(/'/g,"\\'");
		var msg = 'The provided Storm File text does not seem to be valid.';
			
		$("#json_parse_msg").text(msg).addClass("ui-state-highlight");
		$("#storm_edit_dialog_ok_btn").button("disable");		

		if (errmsg.length > 0)
			$("#json_parse_msg").append(' <span class="pointer" onclick="$(this).append(\'<div>' + errmsg + '</div>\');">Click here for details.</span>');
	}
}