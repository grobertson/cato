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
    // clear the edit array
    $("#hidSelectedArray").val("");

    $("#edit_dialog").hide();
    $("#delete_dialog").hide();

    //define dialogs
    $('#edit_dialog').dialog('option', 'title', 'New Eco Template');
    $("#edit_dialog").dialog({
        autoOpen: false,
        modal: true,
        width: 550,
        buttons: {
            "Create": function () {
                Save();
            },
            Cancel: function () {
                $("[id*='lblNewMessage']").html("");
                $("#hidCurrentEditID").val("");

                $("#hidSelectedArray").val("");
                $("#lblItemsSelected").html("0");

                // nice, clear all checkboxes selected in a single line!
                $(':input', (".jtable")).attr('checked', false);

                $(this).dialog('close');
            }
        }
    });

    $("#copy_dialog").dialog({
        autoOpen: false,
        modal: true,
        width: 500,
        buttons: {
            "Copy": function () {
                CopyTemplate();
            },
            Cancel: function () {
                $(this).dialog('close');
            }
        }
    });

	//what happens when you click a row?
    $("[tag='selectable']").live("click", function () {
        showPleaseWait();
        location.href = 'ecoTemplateEdit.aspx?ecotemplate_id=' + $(this).parent().attr("ecotemplate_id");
    });

	//use storm?
    $("#use_storm_btn").click(function () {
		$(".stormfields").toggle();
    });
    
    //this onchange event will test the json text entry 
    //and display a little warning if it couldn't be parsed.
    $("#txtStormFile").change(function () {
		validateStormFileJSON();
    });
    
    //changing the Source dropdown refires the validation
    $("#ddlStormFileSource").change(function () {
    	//if it's File, show that section otherwise hide it.
    	if ($(this).val() == "File")
    		$(".stormfileimport").show();
    	else
	    	$(".stormfileimport").hide();
	    	
		validateStormFileJSON();
    });

});
function pageLoad() {
    ManagePageLoad();
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
		$("#json_parse_msg").empty().removeClass("ui-state-highlight").removeClass("ui-state-happy");			
		return;
	}
	
	try
	{
		json = $.parseJSON($("#txtStormFile").val());
		$("#json_parse_msg").empty();
		$("#json_parse_msg").text("Valid Storm File").addClass("ui-state-happy").removeClass("ui-state-highlight");
	}
	catch(err)
	{
		var msg = 'The provided Storm File text does not seem to be valid.';
			
		$("#json_parse_msg").text(msg).addClass("ui-state-highlight");
		$("#json_parse_msg").append(' <span class="pointer" onclick="alert(\'' + err.message + '\');">more details</span>');;
	}
}

function ShowItemAdd() {
    $("#hidMode").val("add");

    // clear all of the previous values
    clearEditDialog();

    $("#edit_dialog").dialog('open');
    $("#txtTemplateName").focus();
}

function DeleteItems() {
    var ArrayString = $("#hidSelectedArray").val();
    $.ajax({
        type: "POST",
        url: "uiMethods.asmx/wmDeleteEcotemplates",
        data: '{"sDeleteArray":"' + ArrayString + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (msg) {
            if (msg.d.length == 0) {

                $("#hidSelectedArray").val("");
                $("#delete_dialog").dialog('close');

                // clear the search field and fire a search click, should reload the grid
                $("[id*='txtSearch']").val("");
                $("[id*='btnSearch']").click();

                hidePleaseWait();
                showInfo('Delete Successful');

            } else {
                showAlert(msg.d);

                $("#delete_dialog").dialog('close');
                
                // reload the list, some may have been deleted.
                // clear the search field and fire a search click, should reload the grid
                $("[id*='txtSearch']").val("");
                $("[id*='btnSearch']").click();
            }
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });

}



function Save() {
    var bSave = true;
    var strValidationError = '';

    //some client side validation before we attempt to save the user
    if ($("#txtTemplateName").val() == "") {
        bSave = false;
        strValidationError += 'Name is required.';
    };

    if (bSave != true) {
        showAlert(strValidationError);
        return false;
    }

	var name = packJSON($("#txtTemplateName").val());
	var desc = packJSON($("#txtTemplateDesc").val());
	var sfs = packJSON($("#ddlStormFileSource").val());
	var sf = packJSON($("#txtStormFile").val());
	
    $.ajax({
        async: false,
        type: "POST",
        url: "uiMethods.asmx/wmCreateEcotemplate",
        data: '{"sName":"' + name + '","sDescription":"' + desc + '","sStormFileSource":"' + sfs + '","sStormFile":"' + sf + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (msg) {
            if (msg.d.length == 36) {
            	showPleaseWait();
                location.href = "ecoTemplateEdit.aspx?ecotemplate_id=" + msg.d;
            } else {
            	showInfo(msg.d, "", true);
            }
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
}


function ShowItemCopy() {
    // clear all of the previous values
    var ArrayString = $("#hidSelectedArray").val();
    if (ArrayString.length == 0) {
        showInfo('Select an Ecosystem Template to Copy.');
        return false;
    }
    if (ArrayString.indexOf(",") > -1) {
    	//make a comment and clear the selection.
        showInfo('Only one Ecosystem Template can be copied at a time.');
        ClearSelectedRows();
        return false;
    }
	
	$("#copy_dialog").dialog('open');
}
function CopyTemplate() {
	var sSelectedTemplateID = $("#hidSelectedArray").val();
    var sNewTemplateName = $("#txtCopyEcotemplateName").val();

    // make sure we have all of the valid fields
    if (sNewTemplateName == '') {
        showInfo('A new Name is required.');
        return false;
    }

    $.ajax({
        type: "POST",
        url: "uiMethods.asmx/wmCopyEcotemplate",
        data: '{"sEcoTemplateID":"' + sSelectedTemplateID + '","sNewName":"' + sNewTemplateName + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (msg) {
            if (msg.d.length == 36) {
                $("#copy_dialog").dialog('close');
                // clear the search field and fire a search click, should reload the grid
                $("#ctl00_phDetail_txtSearch").val("");
                $("#ctl00_phDetail_btnSearch").click();

                hidePleaseWait();
                showInfo('Copy Successful.');
            } else {
                showInfo(msg.d);
            	$("#txtCopyEcotemplateName").val("");
            }
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
}
