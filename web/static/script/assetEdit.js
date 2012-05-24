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
    // clear the edit array
    $("#hidSelectedArray").val("");

    $("#edit_dialog").hide();
    $("#delete_dialog").hide();

    //specific field validation and masking
    $("#txtAssetName").keypress(function(e) { return restrictEntryToSafeHTML(e, this); });
    $("#txtAddress").keypress(function(e) { return restrictEntryToSafeHTML(e, this); });
    $("#txtDbName").keypress(function(e) { return restrictEntryToSafeHTML(e, this); });
    $("#txtCredUsername").keypress(function(e) { return restrictEntryToUsername(e, this); });
    $("#txtCredName").keypress(function(e) { return restrictEntryToSafeHTML(e, this); });
    $("#txtCredDescription").keypress(function(e) { return restrictEntryToSafeHTML(e, this); });
    $("#txtCredDomain").keypress(function(e) { return restrictEntryToHostname(e, this); });

    $("#item_upload_btn").live("click", function() {
        ShowAssetUpload();
    });

    //dialogs
    $("#edit_dialog").dialog({
        autoOpen: false,
        modal: true,
        width: 700,
        bgiframe: true,
        buttons: {
            "Save": function() {
                SaveAsset();
            },
            Cancel: function() {
                CloseDialog();
            }
        }
    });

    // remove the header and x, to prevent the user from clicking on them
    $("#edit_dialog").dialog().parents(".ui-dialog").find(".ui-dialog-titlebar").remove();

    //the hook for the 'show log' link
    $("#show_log_link").button({ icons: { primary: "ui-icon-document"} });
    $("#show_log_link").click(function() {
        var sAssetID = $("#hidCurrentEditID").val();
		ShowLogViewDialog(2, sAssetID, true);
    });

    $("#rbShared").live("change", function() {
        $(".SharedCredFields").show();
    });
    $("#rbLocal").live("change", function() {
        $(".SharedCredFields").hide();
    });
    
    //what happens when you click a asset row
    $(".selectablecrd").live("click", function() {
        $("#hidCredentialID").val($(this).parent().attr("credential_id"));
        $('#tblCredentialSelector td').removeClass('row_over'); //unselect them all
        $(this).parent().find('td').addClass("row_over"); //select this one
    });

    // end live version
    //------------------------------------------------------------------

    // setup the AddTabs
    $("#AddAssetTabs").tabs();
    $("#CredentialSelectorTabs").hide();
    $("#CredentialsSubMenu").hide();
    $("#EditCredential").hide();


    $("#btnCredSelect").click(function() {
        $("input[name=rbShared]:checked").val("0")
        $("#hidCredentialType").val("selected");
        $('#hidCredentialID').val('');
        $('#CredentialSelectorTabs').show();
        $('#AddCredential').hide();
        $('#CredentialDetails').hide();
        $('#SharedLocalDiv').hide();
        $('#EditCredential').hide();
        LoadCredentialSelector();
        $('#btnCredAdd').show();
        return false;
    });

    $("#btnCredAdd").click(function() {
        $("input[name=rbShared]:checked").val("1")
        $("#hidCredentialType").val("new");
        $("#hidCredentialID").val("");
        $("#CredentialSelectorTabs").hide();
        $("#CredentialDetails").html("");
        $("#txtCredName").val("");
        $("#txtCredUsername").val("");
        $("#txtCredDomain").val("");
        $("#txtCredPassword").val("");
        $("#txtCredPasswordConfirm").val("");
        $("#EditCredential").show();
        $("#SharedLocalDiv").show();
        $("#txtCredUsername").focus();
        return false;
    });

	GetItems();
    ManagePageLoad();
});

function GetItems() {
    $.ajax({
        type: "POST",
        async: false,
        url: "uiMethods/wmGetAssetsTable",
        data: '{"sSearch":"' + $("#txtSearch").val() + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "html",
        success: function (response) {
            $("#assets").html(response);
            //gotta restripe the table
            initJtable(true, true);
		    $("#assets .selectable").click(function () {
		        LoadEditDialog(0, $(this).parent().attr("asset_id"));
		    });
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
}

function ShowItemAdd() {
    $("#hidMode").val("add");
    // clear all of the previous values
    $(':input', ("#tblEdit")).each(function() {
        var type = this.type;
        var tag = this.tagName.toLowerCase(); // normalize case
        if (type == 'text' || type == 'password' || tag == 'textarea')
            this.value = "";
        else if (type == 'checkbox' || type == 'radio')
            this.checked = false;
        else if (tag == 'select')
            this.selectedIndex = -1;
    });

    $('#edit_dialog').data('title.dialog', 'Add New Asset');

    // hide the log link on a new asset creation
    $('#show_log_link').hide();

    // bugzilla 1243 make Active the default on add
    $("#ddlAssetStatus").val("Active");

    //bugzilla 1203 when ading a new asset set the credentials tab to add new credential by default.
    //if the user adds no information nothing will get saved but new local credential is default.
    $("#btnCredAdd").click();

    $('#CredentialDetails').html('');
    $("#edit_dialog").dialog('open');
    $("#txtAssetName").focus();


}
function CloseDialog() {
    $('#AddAssetTabs').tabs('select', 0);

    CancelCredentialAdd();

    $("#edit_dialog").dialog('close');
    InitializeAdd();

    return false;
}
function InitializeAdd() {
    // called from button click, or the small x in the dialog
    $('#AddAssetTabs').tabs('select', 0);
    $("#hidCurrentEditID").val("");

    $("#CredentialsSubMenu").hide();
    // and credential add
    $("#txtCredUsername").val("");
    $("#txtCredPassword").val("");
    $("#txtCredPasswordConfirm").val("");
    $("#txtCredName").val("");
    $("#txtCredDescription").val("");
    $("#txtCredDomain").val("");
    $("#txtPrivilegedPassword").val("");
    $("#txtPrivilegedConfirm").val("");
    $("#objects_tags").empty();

    ClearSelectedRows();

}

function DeleteItems() {
    var ArrayString = $("#hidSelectedArray").val();
    $.ajax({
        type: "POST",
        url: "assetEdit.aspx/DeleteAssets",
        data: '{"sDeleteArray":"' + ArrayString + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(msg) {
            //update the list in the dialog
            var myArray = new Array();
            var myArray = msg.d.split(',');
            $("#hidSelectedArray").val("");
            $("#delete_dialog").dialog('close');

            $("#ctl00_phDetail_btnSearch").click();

            if (msg.d.length == 0) {
                showInfo('Delete Successful');
            } else {
                showAlert(msg.d);
            }
        },
        error: function(response) {
            showAlert(response.responseText);
        }
    });

}

function SaveAsset() {

    var bSave = true;
    var strValidationError = '';
    //some client side validation before we attempt to save
    var sAssetID = $("#hidCurrentEditID").val();
    var sAssetName = $("#txtAssetName").val();
    if (sAssetName == '') {
        bSave = false;
        strValidationError += 'Asset Name required.';
    };

    var ddlAssetStatus = "";
    if ($("#ddlAssetStatus").val() != null) {
        ddlAssetStatus = $("#ddlAssetStatus").val();
    }
    if (ddlAssetStatus == "") {
        bSave = false;
        strValidationError += 'Select a status for the Asset.';
    }


    var sDbName = $("#txtDbName").val();
    var sPort = $('#txtPort').val();

    // new credentials
    var sCredUsername = $("#txtCredUsername").val();
    var sCredPasword = $("#txtCredPassword").val();
    var sCredPasswordConfirm = $("#txtCredPasswordConfirm").val();
    var sPrivilegedPassword = $("#txtPrivilegedPassword").val();
    var sPrivilegedPasswordConfirm = $("#txtPrivilegedConfirm").val();
    var rbShared = $('input[name=rbShared]:checked').val();
    var sCredentialName = $("#txtCredName").val();
    var sCredentialDescr = $("#txtCredDescription").val();
    var sDomain = $("#txtCredDomain").val();
    var sCredentialType = $("#hidCredentialType").val()
    var sCredentialID = $("#hidCredentialID").val();


    if (sCredentialType == 'selected') {
        if (sCredentialID == '') {
            bSave = false;
            strValidationError += 'Select a credential, or create a new credential.';
        }
    } else {
        // if the type is new, and the user didnt add a username, just ignore it
        //if (sCredentialType == 'existing') {
            if (rbShared == '0') {
                // this is a shared credential, name and description are required
                if (sCredentialDescr == '' || sCredentialName == '') {
                    bSave = false;
                    strValidationError += 'Name and Description are required on Shared Credentials.<br />';
                }
            }
            if (sCredPasword != sCredPasswordConfirm) {
                bSave = false;
                strValidationError += 'Credential Passwords do not match.<br />';
            }
            // check the privileged password if one is filled in they should match
            if (sPrivilegedPassword != sPrivilegedPasswordConfirm) {
                bSave = false;
                strValidationError += 'Credential Passwords do not match.<br />';
            }
        //}

    }
    if (bSave != true) {
        showInfo(strValidationError);
        return false;
    }

    //put the tags in a string for submission
    var sTags = "";
    $("#objects_tags .tag").each(function(intIndex) {
        if (sTags == "")
            sTags += $(this).attr("id").replace(/ot_/, "");
        else
            sTags += "," + $(this).attr("id").replace(/ot_/, "");
    });


    var stuff = new Array();
    stuff[0] = sAssetID;
    stuff[1] = sAssetName;
    stuff[2] = $("#txtDbName").val();
    stuff[3] = sPort;
    stuff[5] = $("#txtAddress").val();
    stuff[6] = $("#hidMode").val();
    stuff[7] = sCredentialID;
    stuff[8] = sCredUsername;
    stuff[9] = sCredPasword;
    stuff[10] = rbShared;
    stuff[11] = sCredentialName;
    stuff[12] = sCredentialDescr;
    stuff[13] = sDomain;
    stuff[14] = $("#hidCredentialType").val();
    stuff[15] = ddlAssetStatus;
    stuff[16] = sPrivilegedPassword;
    stuff[17] = sTags;
    stuff[18] = $("#txtConnString").val();

    if (stuff.length > 0) {
        PageMethods.SaveAsset(stuff, OnUpdateSuccess, OnUpdateFailure);
    } else {
        showAlert('incorrect list of update attributes:' + stuff.length.toString());
    }
}

// Callback function invoked on successful completion of the MS AJAX page method.
function OnUpdateSuccess(result, userContext, methodName) {
    if (methodName == "SaveAsset") {
        if (result.length == 0) {
            showInfo('Asset Saved.');

            if ($("#hidMode").val() == 'edit') {
                // remove this item from the array
                var sEditID = $("#hidCurrentEditID").val();
                var myArray = new Array();
                var sArrHolder = $("#hidSelectedArray").val();
                myArray = sArrHolder.split(',');

                //how many in the array before you clicked Save?
                var wereInArray = myArray.length;

                if (jQuery.inArray(sEditID, myArray) > -1) {
                    $("#chk_" + sEditID).attr("checked", false);
                    myArray.remove(sEditID);
                }

                $("#lblItemsSelected").html(myArray.length);
                $("#hidSelectedArray").val(myArray.toString());

                if (wereInArray == 1) {
                    // this was the last or only user edited so close
                    $("#hidCurrentEditID").val("");
                    $("#hidEditCount").val("");

                    CloseDialog();

                    //leave any search string the user had entered, so just click the search button
                    $("#ctl00_phDetail_btnSearch").click();
                } else {
                    // load the next item to edit
                    $("#hidCurrentEditID").val(myArray[0]);
                    FillEditForm(myArray[0]);
                }
            } else {
                CloseDialog();

                //leave any search string the user had entered, so just click the search button
                $("#ctl00_phDetail_btnSearch").click();
            }
        } else {
            showAlert(result);
        }

    }

}

// Callback function invoked on failure of the MS AJAX page method.
function OnUpdateFailure(error, userContext, methodName) {
    //alert('failure');
    if (error !== null) {
        showAlert(error.get_message());
    }
}
function ShowCredentialAdd() {
    $('#Credentials').hide();
    $('#btnCreateCredentials').hide();
    $('#btnCancelCredentials').show();
    $('#EditCredential').show();
}
function CancelCredentialAdd() {
    //alert('cancel credentials');
    $('#Credentials').show();
    $('#btnCreateCredentials').show();
    $('#btnCancelCredentials').hide();
    $('#EditCredential').hide();
}

function LoadEditDialog(editCount, editAssetID) {
    //alert('clear everything out');


    // show the log link on an existing asset
    $('#show_log_link').show();
    $('#show_tasks_link').show();

    // clear credentials
    $('#txtCredUsername').val();
    $('#txtCredDomain').val();
    $('#txtCredPassword').val();
    $('#txtCredPasswordConfirm').val();

    $("#hidMode").val("edit");
    $("#edit_dialog").data("title.dialog", "Modify Asset");
    $("#edit_dialog").dialog('open');

    $("#hidEditCount").val(editCount);
    $("#hidCurrentEditID").val(editAssetID);

    FillEditForm(editAssetID);
    GetObjectsTags(editAssetID);
}

function ShowItemModify() {

    var ArrayString = $("#hidSelectedArray").val();
    if (ArrayString.length == 0) {
        showInfo('Select one or more Assets to modify.');
        return false;
    }
    var curArray = ArrayString.split(',');

    //load up the first or only asset to modify
    var sFirstID = curArray[0];

    // load the asset for editing
    LoadEditDialog(curArray.length, sFirstID);

}
function LoadCredentialSelector() {
    $("#CredentialSelectorShared").html("Loading...");
    // set the return t the default 'local' credentials
    $.ajax({
        type: "POST",
        url: "assetEdit.aspx/GetCredentialSelector",
        data: '{}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(msg) {
            //update the list in the dialog
            //alert(msg.d);
            if (msg.d.length == 0) {
                showAlert('Could not load selector.' + response.responseText);
            } else {
                $("#CredentialSelectorShared").html(msg.d);
                //$('#tblCredentialSelector td').addClass('row');
            }
        },
        error: function(response) {
            showAlert('error ' + response.responseText);
        }
    });
    $('#CredentialSelectorTabs').show();


}
function FillEditForm(sAssetID) {
    $.ajax({
        type: "POST",
        url: "uiMethods/wmGetAsset",
        data: '{"sAssetID":"' + sAssetID + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(asset) {
            // show the assets current values
            $("#txtAssetName").val(asset.Name);
            $("#ddlAssetStatus").val(asset.Status);
            $("#txtPort").val(asset.Port)
            $("#txtDbName").val(asset.DbName);
            var sAddress = asset.Address.replace("||", "\\\\");
            sAddress = sAddress.replace(/\|/g, "\\");
            $("#txtAddress").val(sAddress);
            $("#txtConnString").val(asset.ConnString);
            
            $("#hidCredentialID").val(asset.CredentialID);
            var sCredentialID = asset.CredentialID;
            $("#hidCredentialID").val(sCredentialID);
            $('#CredentialSelectorTabs').hide();
            var CredentialUser = asset.UserName;

            $('#btnCredAdd').hide();

            if (sCredentialID == '') {
                // no existing credential, just show the add dialog
                $("#hidCredentialType").val("new");
                $("#CredentialDetails").html("");
                $('#SharedLocalDiv').show();
                $('#EditCredential').show();
                $('.SharedCredFields').hide();

            } else {
                // display the credentials if they exist, if not display only the add button
                if (asset.UserName != '') {
                    var CredentialShared = asset.SharedOrLocal;
                    if (CredentialShared == 'Local') {
                        $("#CredentialDetails").html("");
                        $("#hidCredentialType").val("existing");
                        $("input[name=rbShared]:checked").val("1");
                        $('#txtCredUsername').val(asset.UserName);
                        $('#txtCredDomain').val(asset.Domain);
                        //$('#txtCredPassword').val(asset.Password);
                        //$('#txtCredPasswordConfirm').val(asset.Password);
                        //$('#txtPrivilegedPassword').val(asset.PriviledgedPassword);
                        //$('#txtPrivilegedConfirm').val(asset.PriviledgedPassword);
                        $('.SharedCredFields').hide();
                        $('#SharedLocalDiv').hide();
                        $('#EditCredential').show();
                    } else {
                        // display the existing shared credential
                        $("#CredentialDetails").html(CredentialShared + ' - ' + asset.UserName + '<br />Domain - ' + asset.Domain + '<br />Name - ' + asset.SharedCredName + '<br />Description - ' + asset.SharedCredDesc);
                        $('#CredentialRemove').show();
                        $('#CredentialDetails').show();
                        $('#imgCredClear').show();
                        $('#btnCredAdd').show();
                    }
                } else {
                    $('#imgCredClear').hide();
                    $("#CredentialDetails").html("");
                    $('#CredentialRemove').hide();
                    $('#CredentialDetails').hide();
                }
            }

            $("#CredentialSelectorLocal").empty();

            // at load default to the first tab
            $('#AddAssetTabs').tabs('select', 0);

        },
        error: function(response) {
            showAlert(response.responseText);
        }
    });
}

function ShowAssetUpload() {
    var url = "assetUpload.aspx";
    openWindow(url, "assetUpload", "location=no,status=no,scrollbars=yes,resizable=yes,width=850,height=700");
}
