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
$(document).ready(function() {
    $("#new_version_btn").button({ icons: { primary: "ui-icon-extlink"} });
    $("#new_version_btn").click(function () {
		ShowVersionAdd();
    });

    $("#addVersion_dialog").dialog({
        autoOpen: false,
        modal: true,
        width: 400,
        buttons: {
            "New Version": function () {
                CreateNewVersion();
            },
            "Cancel": function () {
                $(this).dialog('close');
            }
        }
    });
});

function ShowVersionAdd() {
    $("#hidMode").val("add");
    $("#addVersion_dialog").dialog('open');
}

function CreateNewVersion() {
    $.blockUI({ message: "Creating new version..." });

    $.ajax({
        async: false,
        type: "POST",
        url: "taskMethods/wmCreateNewTaskVersion",
        data: '{"sTaskID":"' + g_task_id + '","sMinorMajor":"' + $("input[name='rbMinorMajor']:checked").val() + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "text",
        success: function(response) {
            if (response.length == 36) {
		    	//NOTE: this changes the g_task_id, and pushes a new URL into the address bar
		    	g_task_id = response
				history.replaceState({}, "", "taskEdit?task_id=" + g_task_id);
				//refresh the versions toolbox, which will add the new one...
				doGetVersions();
				
				//BUT WE must do this to set the "focus" of the page on the new version
				
		    	//get the details
		    	doGetDetails();
				//get the codeblocks
				doGetCodeblocks();
				//get the steps
				doGetSteps();
            }
            else {
                showAlert(response);
            }
        },
        error: function(response) {
            showAlert(response.responseText);
        }
    });

	$.unblockUI();
    $("#addVersion_dialog").dialog('close');

    return false;
}

function CloseVersionDialog() {
    $("#addVersion_dialog").dialog('close');

    return false;
}

function doGetVersions() {
    $.ajax({
        async: true,
        type: "POST",
        url: "taskMethods/wmGetTaskVersions",
        data: '{"sTaskID":"' + g_task_id + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "html",
        success: function (response) {
            $("#versions").html(response);
		    //VERSION TOOLBOX
		    $("#versions .version").disableSelection();
		    
		    //the onclick event of the 'version' elements
		    $("#versions .version").click(function () {
		    	//NOTE: this changes the g_task_id, and pushes a new URL into the address bar
		    	g_task_id = $(this).attr("task_id")
				history.replaceState({}, "", "taskEdit?task_id=" + g_task_id);
			    $("#versions .version").removeClass("version_selected")
			    $(this).addClass("version_selected");
		    	//get the details
		    	doGetDetails();
				//get the codeblocks
				doGetCodeblocks();
				//get the steps
				doGetSteps();
		    });
		    
		    //whatever the current version is... change it's class in the list
		    $("#v_" + g_task_id).addClass("version_selected");
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
}
