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

    //make the codeblock add button
    $("#codeblock_add_btn").button({ icons: { primary: "ui-icon-plus"} });

    //the onclick event of the 'add' link for codeblocks
    $("#codeblock_add_btn").live("click", function () {
        ShowCodeblockEdit('');
    });
    // also if the user hits the enter key in the new codeblock textbox
    //    $("#new_codeblock_name").live("keypress", function(e) {
    //        //alert('keypress');
    //        if (e.which == 13) {
    //            doCodeblockAdd();
    //            return false;
    //        }
    //    });


    //the onclick event of the 'copy' link of each codeblock
    $("#div_codeblocks .codeblock_copy_btn").live("click", function () {
        $("#update_success_msg").text("Copying...").show();

        var cb = $(this).attr("codeblock_name");

        $.ajax({
            async: false,
            type: "POST",
            url: "taskMethods.asmx/wmCopyCodeblockStepsToClipboard",
            data: '{"sTaskID":"' + g_task_id + '","sCodeblockName":"' + cb + '"}',
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (msg) {
                doGetClips();
                $("#update_success_msg").text("Copy Successful").fadeOut(2000);
            },
            error: function (response) {
                $("#update_success_msg").fadeOut(2000);
                showAlert(response.responseText);
            }
        });

    });

    //the onclick event of the 'delete' link of each codeblock
    $("#div_codeblocks .codeblock_delete_btn").live("click", function () {
        $("#codeblock_to_delete").val($(this).attr("remove_id"));
        $("#codeblock_delete_confirm_dialog").dialog('open');
    });

    //the onclick event of the 'codeblock' elements
    $("#div_codeblocks .codeblock_title").live("click", function () {
        cb = $(this).attr("name");

        $("#ctl00_phDetail_hidCodeblockName").val(cb);
        getSteps();
    });
    //the onclick event of the 'codeblock rename icon'
    $("#div_codeblocks .codeblock_rename").live("click", function () {
        cb = $(this).attr("codeblock_name");
        ShowCodeblockEdit(cb);
    });

    //init the codeblock add dialog
    $("#codeblock_edit_dialog").dialog({
        autoOpen: false,
        modal: true,
        width: 300
    });

    //init the codeblock delete confirm dialog
    $("#codeblock_delete_confirm_dialog").dialog({
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
                $(this).dialog('close');
                doCodeblockDelete();
            },
            Cancel: function () {
                $(this).dialog('close');
            }
        }
    });

    //hover effect
    $("#div_codeblocks .codeblock").live("hover", function () {
        $("#te_help_box_detail").html("Click a Codeblock to edit its steps.");
    }, function () {
        $("#te_help_box_detail").html("");
    });

});



function ShowCodeblockEdit(codeblock_name) {
    $("#codeblock_edit_dialog_msg").text("");

    //if codeblock_name is empty, we are adding otherwise we are editing
    if (codeblock_name.length > 0) {
        //Enter a name for the Codeblock :
        if (codeblock_name == 'MAIN') {
            // main codeblocks can not be renamed.
            showInfo('The MAIN codeblock can not be renamed.');
            return false;
        };
        $("#new_codeblock_name").val(codeblock_name);
        $("#codeblock_edit_dialog").dialog("option", "buttons", {
            "Save": function () { doCodeblockUpdate(codeblock_name) },
            "Cancel": function () { $(this).dialog("close"); }
        });
    }
    else {
        //Enter a name for the new Codeblock:
        $("#new_codeblock_name").val('');
        $("#codeblock_edit_dialog").dialog("option", "buttons", {
            "Add": function () { doCodeblockAdd() },
            "Cancel": function () { $(this).dialog("close"); }
        });
    }

    $("#codeblock_edit_dialog").dialog('open');
}

function doCodeblockUpdate(old_name) {
    showPleaseWait();

    var sNewCodeblockName = $("#new_codeblock_name").val();

    // before doing the postback, make sure the user entered something in the new name, and that its different than the old name.
    if (sNewCodeblockName == '') {
        return false;
    };

    $.ajax({
        async: false,
        type: "POST",
        url: "taskMethods.asmx/wmRenameCodeblock",
        data: '{"sTaskID":"' + g_task_id + '","sOldCodeblockName":"' + old_name + '","sNewCodeblockName":"' + sNewCodeblockName + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (msg) {
            if (msg.d.length == 0) {
                $("#codeblock_edit_dialog").dialog("close");

                //if we are looking at the codeblock we are changing... gotta reset the hidden field
                if ($("#ctl00_phDetail_hidCodeblockName").val() == old_name) {
                    $("#codeblock_steps_title").text(sNewCodeblockName);
                    $("#ctl00_phDetail_hidCodeblockName").val(sNewCodeblockName);
                }


                //refresh the codeblock list
                $("#ctl00_phDetail_btnCBRefresh").click();

                //reload the steps
                setTimeout('getSteps()', 500);

                setTimeout('hidePleaseWait()', 1000);
            } else {
                showInfo(msg.d);
                hidePleaseWait();
            }
        },
        error: function (response) {
            $("#update_success_msg").fadeOut(2000);
            showAlert(response.responseText);
            hidePleaseWait();
        }
    });

    // since we are reloading the codeblock list, remove the delete button again for the MAIN codeblock
    $("#codeblock_delete_btn_MAIN").remove();
    $("#codeblock_rename_btn_MAIN").remove();

}

function doCodeblockAdd() {
    codeblock_name = $("#new_codeblock_name").val();

    if (codeblock_name != "") {
        $.blockUI({ message: null });
        $("#update_success_msg").text("Updating...").show();

	    $.ajax({
	        async: false,
	        type: "POST",
	        url: "taskMethods.asmx/wmAddCodeblock",
	        data: '{"sTaskID":"' + g_task_id + '","sNewCodeblockName":"' + codeblock_name + '"}',
	        contentType: "application/json; charset=utf-8",
	        dataType: "json",
	        success: function (response) {
		        //set the hidden field and label
		        $("#ctl00_phDetail_hidCodeblockName").val(codeblock_name);
		        $("#codeblock_steps_title").text(codeblock_name);
		
				//TODO: add it to the codeblock list?
				//probably by just regetting all the codeblocks so the links and stuff will work?
				//yes! so they will also be sorted correctly
				//getCodeblocks();
				
		        //clear the 'add' box
		        $("#new_codeblock_name").val("");
		
		        //and clear the step sortable
		        $("#steps").empty();
		
		        $.unblockUI();
		        $("#codeblock_edit_dialog").dialog('close');
		        $("#update_success_msg").text("Update Successful").fadeOut(2000);
	        },
	        error: function (response) {
	            $("#update_success_msg").fadeOut(2000);
	            showAlert(response.responseText);
	            hidePleaseWait();
	        }
	    });
	
    } else {
        //this would be better if you couldn't click the Add button if it was blank
        $("#codeblock_edit_dialog_msg").text("Codeblock Name is required.");
        $("#new_codeblock_name").focus();
    }
}

function doCodeblockDelete() {
    var codeblock_name = $("#codeblock_to_delete").val();

        //don't need to block, the dialog blocks.
    $("#update_success_msg").text("Updating...").show();

    $.ajax({
        async: false,
        type: "POST",
        url: "taskMethods.asmx/wmDeleteCodeblock",
        data: '{"sTaskID":"' + g_task_id + '","sCodeblockID":"' + codeblock_name + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (response) {
        	//remove it from the list of codeblocks
		    $("#codeblocks #cb_" + codeblock_name).remove();

			//clear the dialog value
		    $("#codeblock_to_delete").val("");
		
		    //when we delete a codeblock we reset the step list to MAIN.
		    $("#ctl00_phDetail_hidCodeblockName").val("MAIN");
			getSteps();
		
		    $("#update_success_msg").text("Update Successful").fadeOut(2000);
        },
        error: function (response) {
            $("#update_success_msg").fadeOut(2000);
            showAlert(response.responseText);
            hidePleaseWait();
        }
    });
}

