//Copyright 2012 Cloud Sidekick
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
    //make the parameter add button
    $("#parameter_add_btn").button({ icons: { primary: "ui-icon-plus"} });

    //any page that includes this script will get the following dialog inner code
    //but the page requires a placeholder div... called "param_edit_dialog"
    var d = '<div id="param_edit_dialog_detail"></div>' +
        '<input type="hidden" id="param_edit_param_id" />'
    $("#param_edit_dialog").html(d);


    //here's the delete confirmation dialog
    var d = '<p>' +
                '<span class="ui-icon ui-icon-info" style="float: left; margin: 0 7px 50px 0;"></span>' +
                '<span>Are you sure?</span>' +
                '</p>'
    $("#param_delete_confirm_dialog").html(d);


    $("#param_delete_confirm_dialog").dialog({
        autoOpen: false,
        draggable: false,
        resizable: false,
        bgiframe: true,
        modal: true,
        overlay: {
            backgroundColor: '#000',
            opacity: 0.5
        },
        buttons: {
            'Delete': function () {
                doDeleteParam();
                $(this).dialog("close");
            },
            Cancel: function () {
                $(this).dialog("close");
            }
        }
    });

    $("#param_edit_dialog").dialog({
        autoOpen: false,
        modal: true,
        width: 600
    });

    //parameter edit buttons
    $("#parameter_add_btn").click(function () {
        ShowParameterEdit("");
    });
    $("#parameters .parameter_name").live("click", function () {
        ShowParameterEdit($(this).attr("id"));
    });
    $("#parameters .parameter_remove_btn").live("click", function () {
        $("#hidParamDelete").val($(this).attr("remove_id"));
        $("#param_delete_confirm_dialog").dialog("open");
    });

    //bind the tooltips for parameter descriptions
    bindParameterToolTips();


    $("#param_edit_value_add_btn").live("click", function () {
        //something unique on the page until it is posted.
        var id = "pv" + new Date().getTime();
        var html = "<div id=\"" + id + "\">" +
            "<textarea class=\"param_edit_value\" rows=\"1\"></textarea>" +
            " <span class=\"ui-icon ui-icon-close forceinline param_edit_value_remove_btn pointer\" remove_id=\"" + id + "\"></span>" +
            "</div>";

        $("#param_edit_values").append(html);
        $("#" + id + " textarea:first").focus();
    });
    $("#param_edit_values .param_edit_value_remove_btn").live("click", function () {
        $("#" + $(this).attr("remove_id")).remove();
    });

    $("#param_edit_present_as").live("change", function () {
        if ($(this).val() == "value") {
            $(".param_edit_value_remove_btn").addClass("hidden");
            $("#param_edit_value_add_btn").addClass("hidden");
        } else {
            $(".param_edit_value_remove_btn").removeClass("hidden");
            $("#param_edit_value_add_btn").removeClass("hidden");
        }
    });

    //any change to a value at all sets the dirty flag
    $(".param_edit_value").live('change', function () {
        $(this).attr("dirty","true");
    });

});

//functions
function ShowParameterEdit(param_id) {
    //if param_id is empty, we are adding otherwise we are editing
    if (param_id.length > 0) {
        $("#param_edit_dialog").dialog("option", "buttons", {
            "Save": function () { doSaveParam() },
            "Cancel": function () { $(this).dialog("close"); }
        });
    }
    else {
        $("#param_edit_dialog").dialog("option", "buttons", {
            "Add": function () { doSaveParam() },
            "Cancel": function () { $(this).dialog("close"); }
        });
    }

    $("#param_edit_param_id").val(param_id);
    var id = "";
    var type = $("#hidParamType").val();
    if (type == "task")
        id = g_task_id;
    else if (type == "ecosystem")
        id = $("#hidEcosystemID").val();

    //go get the details for the parameter via ajax and populate the dialog
    $.ajax({
        async: false,
        type: "POST",
        url: "taskMethods/wmGetTaskParam",
        data: '{"sType":"' + type + '","sID":"' + id + '","sParamID":"' + param_id + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "html",
        success: function (response) {
            $("#param_edit_dialog_detail").html(response);
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });

    $("#param_edit_dialog").dialog("open");
}

function doSaveParam() {
    $("#update_success_msg").text("Updating...").fadeOut(2000);

    var id = "";
    var type = $("#hidParamType").val();
    if (type == "task")
        id = g_task_id;
    else if (type == "ecosystem")
        id = $("#hidEcosystemID").val();

    var param_id = $("#param_edit_param_id").val();
    var name = $("#param_edit_name").val();
    var desc = packJSON($("#param_edit_desc").val());

    if (name == "") {
        alert("Parameter name cannot be blank.");
        return false;
    }

    var minlength = $("#param_edit_minlength").val();
    var maxlength = $("#param_edit_maxlength").val();
    var minvalue = $("#param_edit_minvalue").val();
    var maxvalue = $("#param_edit_maxvalue").val();
    var constraint = packJSON($("#param_edit_constraint").val());
    var constraint_msg = packJSON($("#param_edit_constraint_msg").val());


    //is this parameter required?
    var is_required = ($("#param_edit_required").is(':checked') ? true : false);
    //should we prompt the user for it?
    var should_prompt = ($("#param_edit_prompt").is(':checked') ? true : false);
    //is this parameter encrypted?
    var encrypt = ($("#param_edit_encrypt").is(':checked') ? true : false);

    //presentation type for these values?
    var present_as = $("#param_edit_present_as").val();

    //put the values in an array
    var vals = "";
    $("#param_edit_values .param_edit_value").each(
        function (index) {
        	//for encrypted parameters...
        	//if a value is dirty, use the value...
        	//otherwise use the oev.

			var val = packJSON($(this).val());;            

        	if (encrypt) {
        		///the oev is already "packed"
        		if ($(this).attr("dirty")==null && $(this).attr("oev")!=null)
        			val = "oev:" + $(this).attr("oev");
        			
        		//if it's dirty, and the value is empty, clear the oev
        		if ($(this).attr("dirty")==true && val == "")
        		{
        			val = "oev:";
        			$(this).attr("oev", "");
    			}
        	}
        	
            if (vals == "")
                vals += val;
            else
                vals += "|" + val;

        }
    );

    $("#update_success_msg").text("Updating...").show();
    $.ajax({
        async: false,
        type: "POST",
        url: "taskMethods/wmUpdateTaskParam",
        data: '{"sType":"' + type + '","sID":"' + id +
            '","sParamID":"' + param_id + '","sName":"' + name + '","sDesc":"' + desc +
            '","sRequired":"' + is_required + '","sPrompt":"' + should_prompt + '","sEncrypt":"' + encrypt +
            '","sMinLength":"' + minlength + '","sMaxLength":"' + maxlength + 
            '","sMinValue":"' + minvalue + '","sMaxValue":"' + maxvalue + 
            '","sConstraint":"' + constraint + '","sConstraintMsg":"' + constraint_msg + 
            '","sPresentAs":"' + present_as + '","sValues":"' + vals + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (retval) {
            doGetParams(type, id);

            $("#param_edit_dialog").dialog("close");
            $("#update_success_msg").text("Update Successful").fadeOut(2000);
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
}

function doDeleteParam() {
    var param_id = $("#hidParamDelete").val();
    var id = "";
    var type = $("#hidParamType").val();
    if (type == "task")
        id = g_task_id;
    else if (type == "ecosystem")
        id = $("#hidEcosystemID").val();

    $("#update_success_msg").text("Updating...").show();
    $.ajax({
        async: false,
        type: "POST",
        url: "taskMethods/wmDeleteTaskParam",
        data: '{"sType":"' + type + '","sID":"' + id + '","sParamID":"' + param_id + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (response) {
            doGetParams(type, id);
            $("#update_success_msg").text("Update Successful").fadeOut(2000);
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
}
function doGetParams(type, id, editable, snip, readonly) {
    if (editable === undefined) editable = true;
    if (snip === undefined) snip = true;

    $.ajax({
        async: false,
        type: "POST",
        url: "taskMethods/wmGetParameters",
        data: '{"sType":"' + type + '","sID":"' + id + '","bEditable":"' + editable + '","bSnipValues":"' + snip + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "html",
        success: function (response) {
            $("#parameters").html(response);

            //have to rebind the tooltips here
            bindParameterToolTips();
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
}
function bindParameterToolTips() {
    $("#parameters .parameter_help_btn").tipTip({
        defaultPosition: "right",
        keepAlive: false,
        activation: "hover",
        maxWidth: "500px",
        fadeIn: 100
    });
}