/*
There are some script that applies to instances of Steps on a Task.

Here is all the code relevant to Steps and their dynamic nature.
*/

//This link can appears anywhere it is needed.
//it clears a field and enables it for data entry.
$(document).ready(function () {
    $(".fn_field_clear_btn").live("click", function () {
        var field_id_to_clear = $(this).attr("clear_id");

        //clear it
        $("#" + field_id_to_clear).val("");

        //in case it's disabled, enable it
        $("#" + field_id_to_clear).removeAttr('disabled');

        //push an change event to it.
        $("#" + field_id_to_clear).change();
    });
    
    //the parameter edit dialog button for Run Task command
    $(".fn_runtask_edit_parameters_btn").live("click", function () {
        //trying globals!!!  Maybe we'll do this using AmplifyJS one day.
        rt_task_id = $(this).attr("task_id");
        rt_step_id = $(this).attr("step_id");
                
        ShowRunTaskParameterEdit();
    });

	//init dialogs
    $("#fn_runtask_parameter_dialog").dialog({
        autoOpen: false,
        modal: true,
        height: 650,
        width: 500,
        open: function (event, ui) { $(".ui-dialog-titlebar-close", ui).hide(); },
        buttons: {
            "Save": function () {
                SaveRunTaskParameters();
                ClosePlanEditDialog();
            },
            "Cancel": function () {
                CloseRunTaskParameterEdit();
            }
        }
    });

});

//the SUBTASK command
//this will get the parameters in read only format for each subtask command.
$(document).ready(function () {
    $("#steps .subtask_view_parameters_btn").live("click",
    function () {
        var task_id = $(this).attr("id").replace(/stvp_/, "");
        var target = $(this).parent().find(".subtask_view_parameters");
        $.ajax({
            async: false,
            type: "POST",
            url: "taskMethods/wmGetParameters",
            data: '{"sType":"task","sID":"' + task_id + '","bEditable":"false","bSnipValues":"true"}',
            contentType: "application/json; charset=utf-8",
            dataType: "html",
            success: function (response) {
                target.html(response);

                //have to rebind the tooltips here
                bindParameterToolTips();
            },
            error: function (response) {
                showAlert(response.responseText);
            }
        });
    });
});

//end SUBTASK command

//the CODEBLOCK command
//the onclick event of the 'codeblock' elements
$(document).ready(function () {
    $("#steps .codeblock_goto_btn").live("click", function () {
        cb = $(this).attr("codeblock");
        $("#hidCodeblockName").val(cb);
        doGetSteps();
    });
});

//end CODEBLOCK command

//the SUBTASK and RUN TASK commands
//the view link
$(document).ready(function () {
    $("#steps .task_print_btn").live("click", function () {
        var url = "taskPrint.aspx?task_id=" + $(this).attr("task_id");
        openWindow(url, "taskPrint", "location=no,status=no,scrollbars=yes,resizable=yes,width=800,height=700");
    });
    //the edit link
    $("#steps .task_open_btn").live("click", function () {
        location.href = "taskEdit?task_id=" + $(this).attr("task_id");
    });
});
// end SUBTASK and RUN TASK commands

//the IF command
$(document).ready(function () {
    $("#steps .fn_if_remove_btn").live("click", function () {
        var step_id = $(this).attr("step_id");
        var idx = $(this).attr("number");

        doRemoveIfSection(step_id, idx)
    });

    $("#steps .fn_if_removeelse_btn").live("click", function () {
        var step_id = $(this).attr("step_id");
        doRemoveIfSection(step_id, -1)
    });

    $("#steps .fn_if_add_btn").live("click", function () {
        var step_id = $(this).attr("step_id");
        var idx = $(this).attr("next_index");

        doAddIfSection(step_id, idx);
    });

    $("#steps .fn_if_addelse_btn").live("click", function () {
        var step_id = $(this).attr("step_id");
        doAddIfSection(step_id, -1);
    });
    $("#steps .compare_templates").live("change", function () {
        // add whatever was selected into the textarea
        var textarea_id = $(this).attr("textarea_id");
        var tVal = $("#" + textarea_id).val();
        $("#" + textarea_id).val(tVal + this.value);

        // clear the selection
        this.selectedIndex = 0;
    });
});
function doAddIfSection(step_id, idx) {
    $("#task_steps").block({ message: null });
    $("#update_success_msg").text("Updating...").show();

    $.ajax({
        async: false,
        type: "POST",
        url: "taskMethods/wmFnIfAddSection",
        data: '{"sStepID":"' + step_id + '","iIndex":"' + idx + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (retval) {
            //go get the step
            getStep(step_id, step_id, true);
            $("#task_steps").unblock();
            $("#update_success_msg").text("Update Successful").fadeOut(2000);

            //hardcoded index for the last "else" section
            if (idx == -1)
                doDropZoneEnable($("#if_" + step_id + "_else .step_nested_drop_target"));
            else
                doDropZoneEnable($("#if_" + step_id + "_else_" + idx + " .step_nested_drop_target"));

        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
}
function doRemoveIfSection(step_id, idx) {
    if (confirm("Are you sure?")) {
        $("#task_steps").block({ message: null });
        $("#update_success_msg").text("Updating...").show();

        $.ajax({
            async: false,
            type: "POST",
            url: "taskMethods/wmFnIfRemoveSection",
            data: '{"sStepID":"' + step_id + '","iIndex":"' + idx + '"}',
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (retval) {
                getStep(step_id, step_id, true);
                $("#task_steps").unblock();
                $("#update_success_msg").text("Update Successful").fadeOut(2000);
            },
            error: function (response) {
                showAlert(response.responseText);
            }
        });
    }

}
//end IF command


//FUNCTIONS for adding/deleting key/value pairs on a step.
$(document).ready(function () {
    $("#steps .fn_pair_remove_btn").live("click", function () {
        if (confirm("Are you sure?")) {
            var step_id = $(this).attr("step_id");
            var idx = $(this).attr("index");

            $("#task_steps").block({ message: null });
            $("#update_success_msg").text("Updating...").show();

            $.ajax({
                async: false,
                type: "POST",
                url: "taskMethods/wmFnRemovePair",
                data: '{"sStepID":"' + step_id + '","iIndex":"' + idx + '"}',
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (retval) {
                    getStep(step_id, step_id, true);
                    $("#task_steps").unblock();
                    $("#update_success_msg").text("Update Successful").fadeOut(2000);
                },
                error: function (response) {
                    showAlert(response.responseText);
                }
            });
        }
    });

    $("#steps .fn_pair_add_btn").live("click", function () {
        var step_id = $(this).attr("step_id");

        $("#task_steps").block({ message: null });
        $("#update_success_msg").text("Updating...").show();

        $.ajax({
            async: false,
            type: "POST",
            url: "taskMethods/wmFnAddPair",
            data: '{"sStepID":"' + step_id + '"}',
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (retval) {
                //go get the step
                getStep(step_id, step_id, true);
                $("#task_steps").unblock();
                $("#update_success_msg").text("Update Successful").fadeOut(2000);

            },
            error: function (response) {
                showAlert(response.responseText);
            }
        });
    });

    //BUT! Key/Value pairs can appear on lots of different command types
    //and on each type there is a specific list of relevant lookup values
    //So, switch on the function and popup a picker
    //the onclick event of 'connection picker' buttons on selected fields
    $("#steps .key_picker_btn").live("click", function (e) {
        //hide any open pickers
        $("div[id$='_picker']").hide();
        var field = $("#" + $(this).attr("link_to"));
        var func = $(this).attr("function");

        var item_html = "N/A";

        //first, populate the picker
        //(in a minute build this based on the 'function' attr of the picker icon
        switch (func) {
            case "http":
                break;
            case "run_task":
                break;
        }

        $("#key_picker_keys").html(item_html);

        //set the hover effect
        $("#key_picker_keys .value_picker_value").hover(
            function () {
                $(this).toggleClass("value_picker_value_hover");
            },
            function () {
                $(this).toggleClass("value_picker_value_hover");
            }
        );

        //click event
        $("#key_picker_keys .value_picker_value").click(function () {
            field.val($(this).text());
            field.change();

            $("#key_picker").slideUp();
        });

        $("#key_picker").css({ top: e.clientY, left: e.clientX });
        $("#key_picker").slideDown();
    });
    $("#key_picker_close_btn").live("click", function (e) {
        //hide any open pickers
        $("div[id$='_picker']").hide();
    });

});

//end adding/deleting key/value pairs on a step.

//FUNCTIONS for adding/deleting variables on the set_variable AND clear_variable commands.
$(document).ready(function () {
    $("#steps .fn_var_remove_btn").live("click", function () {
        if (confirm("Are you sure?")) {
            var step_id = $(this).attr("step_id");
            var remove_path = $(this).attr("remove_path");

            $("#task_steps").block({ message: null });
            $("#update_success_msg").text("Updating...").show();

            $.ajax({
                async: false,
                type: "POST",
                url: "taskMethods/wmFnVarRemoveVar",
                data: '{"sStepID":"' + step_id + '","sRemovePath":"' + remove_path + '"}',
                contentType: "application/json; charset=utf-8",
                dataType: "text",
                success: function (response) {
                    getStep(step_id, step_id, true);
                    $("#task_steps").unblock();
                    $("#update_success_msg").text("Update Successful").fadeOut(2000);
                },
                error: function (response) {
                    showAlert(response.responseText);
                }
            });
        }
    });

    $("#steps .fn_setvar_add_btn").live("click", function () {
        var step_id = $(this).attr("step_id");
        var add_to = $(this).attr("add_to_node");

        $("#task_steps").block({ message: null });
        $("#update_success_msg").text("Updating...").show();

        $.ajax({
            async: false,
            type: "POST",
            url: "taskMethods/wmFnSetvarAddVar",
            data: '{"sStepID":"' + step_id + '", "sAddTo":"' + add_to + '"}',
            contentType: "application/json; charset=utf-8",
            dataType: "text",
            success: function (response) {
                //go get the step
                getStep(step_id, step_id, true);
                $("#task_steps").unblock();
                $("#update_success_msg").text("Update Successful").fadeOut(2000);

            },
            error: function (response) {
                showAlert(response.responseText);
            }
        });
    });

    $("#steps .fn_clearvar_add_btn").live("click", function () {
        var step_id = $(this).attr("step_id");
        var add_to = $(this).attr("add_to_node");

        $("#task_steps").block({ message: null });
        $("#update_success_msg").text("Updating...").show();

        $.ajax({
            async: false,
            type: "POST",
            url: "taskMethods/wmFnClearvarAddVar",
            data: '{"sStepID":"' + step_id + '", "sAddTo":"' + add_to + '"}',
            contentType: "application/json; charset=utf-8",
            dataType: "text",
            success: function (response) {
                //go get the step
                getStep(step_id, step_id, true);
                $("#task_steps").unblock();
                $("#update_success_msg").text("Update Successful").fadeOut(2000);

            },
            error: function (response) {
                showAlert(response.responseText);
            }
        });
    });

});

//end adding/deleting variables on set_variable AND clear_variable.

//FUNCTIONS for adding variables on the exists commands.
$(document).ready(function () {
    $("#steps .fn_exists_add_btn").live("click", function () {
        var step_id = $(this).attr("step_id");
        var add_to = $(this).attr("add_to_node");

        $("#task_steps").block({ message: null });
        $("#update_success_msg").text("Updating...").show();

        $.ajax({
            async: false,
            type: "POST",
            url: "taskMethods/wmFnExistsAddVar",
            data: '{"sStepID":"' + step_id + '", "sAddTo":"' + add_to + '"}',
            contentType: "application/json; charset=utf-8",
            dataType: "text",
            success: function (response) {
                //go get the step
                getStep(step_id, step_id, true);
                $("#task_steps").unblock();
                $("#update_success_msg").text("Update Successful").fadeOut(2000);

            },
            error: function (response) {
                showAlert(response.responseText);
            }
        });
    });

});

//end adding/deleting variables on set_variable AND clear_variable.

//FUNCTIONS for adding and removing handles from the Wait For Task command
$(document).ready(function () {
    $("#steps .fn_wft_add_btn").live("click", function () {
        var step_id = $(this).attr("step_id");

        $("#task_steps").block({ message: null });
        $("#update_success_msg").text("Updating...").show();

        $.ajax({
            async: false,
            type: "POST",
            url: "taskMethods/wmFnWaitForTasksAddHandle",
            data: '{"sStepID":"' + step_id + '"}',
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (retval) {
                //go get the step
                getStep(step_id, step_id, true);
                $("#task_steps").unblock();
                $("#update_success_msg").text("Update Successful").fadeOut(2000);

            },
            error: function (response) {
                showAlert(response.responseText);
            }
        });
    });

    $("#steps .fn_handle_remove_btn").live("click", function () {
        if (confirm("Are you sure?")) {
            var step_id = $(this).attr("step_id");
            var idx = $(this).attr("index");

            $("#task_steps").block({ message: null });
            $("#update_success_msg").text("Updating...").show();

            $.ajax({
                async: false,
                type: "POST",
                url: "taskMethods/wmFnWaitForTasksRemoveHandle",
                data: '{"sStepID":"' + step_id + '","iIndex":"' + idx + '"}',
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (retval) {
                    getStep(step_id, step_id, true);
                    $("#task_steps").unblock();
                    $("#update_success_msg").text("Update Successful").fadeOut(2000);
                },
                error: function (response) {
                    showAlert(response.responseText);
                }
            });
        }
    });
});

//End Wait For Task functions


//FUNCTIONS for adding and removing xml "node arrays" from any step that might have one.
$(document).ready(function () {
    $("#steps .fn_nodearray_add_btn").live("click", function () {
        var step_id = $(this).attr("step_id");
        var xpath = $(this).attr("xpath");

        $("#task_steps").block({ message: null });
        $("#update_success_msg").text("Updating...").show();

        $.ajax({
            async: false,
            type: "POST",
            url: "taskMethods/wmFnNodeArrayAdd",
            data: '{"sStepID":"' + step_id + '","sGroupNode":"' + xpath + '"}',
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (retval) {
                //go get the step
                getStep(step_id, step_id, true);
                $("#task_steps").unblock();
                $("#update_success_msg").text("Update Successful").fadeOut(2000);

            },
            error: function (response) {
                showAlert(response.responseText);
            }
        });
    });

    $("#steps .fn_nodearray_remove_btn").live("click", function () {
        if (confirm("Are you sure?")) {
            var step_id = $(this).attr("step_id");
            var xpath_to_delete = $(this).attr("xpath_to_delete");

            $("#task_steps").block({ message: null });
            $("#update_success_msg").text("Updating...").show();

            $.ajax({
                async: false,
                type: "POST",
                url: "taskMethods/wmFnNodeArrayRemove",
                data: '{"sStepID":"' + step_id + '","sXPathToDelete":"' + xpath_to_delete + '"}',
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (retval) {
                    getStep(step_id, step_id, true);
                    $("#task_steps").unblock();
                    $("#update_success_msg").text("Update Successful").fadeOut(2000);
                },
                error: function (response) {
                    showAlert(response.responseText);
                }
            });
        }
    });
});

//End XML Node Array functions

//FUNCTIONS for dealing with the very specific parameters for a Run Task command
function ShowRunTaskParameterEdit() {
    var task_parameter_xml = "";

	if (rt_task_id != "") {
	    $.ajax({
	        async: false,
	        type: "POST",
	        url: "taskMethods/wmGetParameterXML",
	        data: '{"sType":"runtask","sID":"' + rt_step_id + '","sFilterByEcosystemID":"' + rt_task_id + '"}',
	        contentType: "application/json; charset=utf-8",
	        dataType: "xml",
	        success: function (response) {
	            if (response != "")
	                task_parameter_xml = response;
	        },
	        error: function (response) {
	            showAlert(response.responseText);
	        }
	    });
	
	    var output = DrawParameterEditForm(task_parameter_xml);
	    $("#fn_runtask_parameter_dialog_params").html(output);
	
	    //don't forget to bind the tooltips!
	    bindParameterToolTips();
	
		//and for this case we bind the right click event of the value fields
		//so... for the new parameters feature on the Run Task command... bind the right click for the runtime var picker too
	    //enable right click on all edit fields
	    $("#fn_runtask_parameter_dialog .task_launch_parameter_value_input").rightClick(function(e) {
	        showVarPicker(e);
	    });
		//this focus hack is required too
	    $("#fn_runtask_parameter_dialog .task_launch_parameter_value_input").focus(function() {
	        fieldWithFocus = $(this).attr("id");
	    });

	
	    $("#fn_runtask_parameter_dialog").dialog("open");
	} else {
		showInfo("Unable to resolve the ID of the Task referenced by this command.");
	}
}
function CloseRunTaskParameterEdit() {
    $("#fn_runtask_parameter_dialog").dialog("close");
}
function SaveRunTaskParameters() {
    $("#update_success_msg").text("Saving Defaults...");

    //build the XML from the dialog
    var parameter_xml = packJSON(buildXMLToSubmit());
    //alert(parameter_xml);

    $.ajax({
        async: false,
        type: "POST",
        url: "taskMethods/wmSaveDefaultParameterXML",
        data: '{"sType":"runtask","sID":"' + rt_step_id + '","sTaskID":"' + rt_task_id + '","sXML":"' + parameter_xml + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "text",
        success: function (response) {
            $("#update_success_msg").text("Save Successful").fadeOut(2000);
            CloseRunTaskParameterEdit();
        },
        error: function (response) {
            $("#update_success_msg").fadeOut(2000);
            showAlert(response.responseText);
        }
    });

    $("#action_parameter_dialog").dialog("close");

}

//End Run Task Parameters
