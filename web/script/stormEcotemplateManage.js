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

$(document).ready(function () {
	//use storm?
    $("#use_storm_btn").click(function () {
		$(".stormfields").toggle();
		$("#edit_dialog").dialog('option','position','center');
    });
    
    //this onchange event will test the json text entry 
    //and display a little warning if it couldn't be parsed.
    $("#txtStormFile").change(function () {
		validateStormFileJSON();
    });
    
    //tabs in the editor
    $("#txtStormFile").tabby();
    
    //changing the Source dropdown refires the validation
    $("#ddlStormFileSource").change(function () {
    	//if it's File, show that section otherwise hide it.
    	if ($(this).val() == "File")
    		$(".stormfileimport").show();
    	else
	    	$(".stormfileimport").hide();
	    	
		if ($(this).val() == "URL") {
			$("#url_to_text_btn").show();
		} else {
			$("#url_to_text_btn").hide();
		}

		validateStormFileJSON();
    });

	//wire up the json "validate" button and other niceties.
	$("#validate").button({ icons: { primary: "ui-icon-check"} });
	$("#validate").click(function () {
		var reformat = ($('#chk_reformat').attr('checked') == "checked" ? true : false);
	    jsl.interactions.validate($("#txtStormFile"), $("#json_parse_msg"), reformat, false);
	    return false;
	});

	$("#storm_edit_dialog_text").keyup(function () {
	    $(this).removeClass('greenBorder').removeClass('redBorder');
	});

    $("#url_to_text_btn").button({ icons: { primary: "ui-icon-shuffle"} });
    $("#url_to_text_btn").click(function () {
		GetStormFileFromURL();
    });
});

function GetStormFileFromURL() {
	var url = $("#txtStormFile").val();
	
	if (url.length == 0)
		return;
		
    $.ajax({
        async: false,
        type: "POST",
        url: "uiMethods.asmx/wmGetStormFileFromURL",
        data: '{"sURL":"' + packJSON(url) + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (msg) {
			if (msg.d.length > 0) {
		       	try
				{
					$("#ddlStormFileSource").val("Text");
					$("#txtStormFile").val(unpackJSON(msg.d));
					$("#url_to_text_btn").hide();
					validateStormFileJSON();
				}
				catch(err)
				{
					showAlert(err.message);
				}
        	} else {
        		showAlert("Nothing returned.  URL may be invalid.");
        	}
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
}

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
                $("#txtStormFile").val(txt);
                $(".stormfileimport").hide();
                $("#ddlStormFileSource").val("Text");
                validateStormFileJSON();
            } else {
                showInfo(msg.d);
            }
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
}

function validateStormFileJSON() {
	if ($("#ddlStormFileSource").val() != "Text") {
		$("#json_parse_msg").empty().removeClass("ui-state-error").removeClass("ui-state-happy");			
		$("#txtStormFile").empty().removeClass("redBorder").removeClass("greenBorder");
		$("#validate").hide();	
		return;
	} else {
		$("#validate").show();
	}
	
	//call the validate function
	var reformat = ($('#chk_reformat').attr('checked') == "checked" ? true : false);
    jsl.interactions.validate($("#txtStormFile"), $("#json_parse_msg"), reformat, false);
}
