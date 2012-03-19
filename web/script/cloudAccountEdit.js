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

    $("[tag='selectable']").live("click", function () {
        LoadEditDialog($(this).parent().attr("account_id"));
    });

    //dialogs

    $("#edit_dialog").dialog({
        autoOpen: false,
        modal: true,
        height: 500,
        width: 600,
        bgiframe: true,
        buttons: {
            "Save": function () {
                SaveItem(1);
            },
            Cancel: function () {
                $("#edit_dialog").dialog('close');
            }
        }
    });

    $("#edit_dialog_tabs").tabs();

    $("#keypair_dialog").dialog({
        autoOpen: false,
        modal: true,
        height: 400,
        width: 400,
        bgiframe: true,
        buttons: {
            "Save": function () {
                SaveKeyPair();
            },
            Cancel: function () {
                $("#keypair_dialog").dialog('close');
            }
        }
    });


	//the Provider ddl changes a few labels based on it's value
	$('#ddlProvider').change(function () {
		setLabels();
		GetProviderClouds();
	});

    $("#jumpto_cloud_btn").button({ icons: { primary: "ui-icon-pencil"}, text: false });
	$("#jumpto_cloud_btn").click(function () {
        var cld_id = $("#ddlTestCloud").val();
        var prv = $("#ddlProvider option:selected").text();

	    if (prv != "Amazon AWS") {
	    	var saved = SaveItem(0);
	    	if (saved) {
			    if (cld_id) {
					location.href="cloudEdit.aspx?cloud_id=" + cld_id;
				} else {
					location.href="cloudEdit.aspx";
				}
			}
		}
    });
    $("#add_cloud_btn").button({ icons: { primary: "ui-icon-plus"}, text: false });
	$("#add_cloud_btn").click(function () {
        var prv = $("#ddlProvider option:selected").text();
	    if (prv != "Amazon AWS") {
	    	var saved = SaveItem(0);
	    	if (saved) {
				location.href="cloudEdit.aspx?add=true&provider=" + prv;
			}
		}
    });


	//if there was an account_id querystring, we'll pop the edit dialog.
	var acct_id = getQuerystringVariable("account_id");
    if (acct_id) {
        LoadEditDialog(acct_id);
    }
	//if there was an add querystring, we'll pop the add dialog.
	var add = getQuerystringVariable("add");
    if (add == "true") {
		var prv = getQuerystringVariable("provider");
		ShowItemAdd();
	    if (prv) { $("#ddlProvider").val(prv); $("#ddlProvider").change(); }
    }


    //keypair add button
    $("#keypair_add_btn").button({ icons: { primary: "ui-icon-plus"} });
    $("#keypair_add_btn").click(function () {
        //wipe the fields
        $("#keypair_id").val("");
        $("#keypair_name").val("");
        $("#keypair_private_key").val("");
        $("#keypair_passphrase").val("");

        $("#keypair_dialog").dialog('open');
    });

    //keypair delete button
    $(".keypair_delete_btn").live("click", function () {
        if (confirm("Are you sure?")) {
            $("#update_success_msg").text("Deleting...").show().fadeOut(2000);

            var kpid = $(this).parents(".keypair").attr("id").replace(/kp_/, "");

            $.ajax({
                type: "POST",
                url: "cloudAccountEdit.aspx/DeleteKeyPair",
                data: '{"sKeypairID":"' + kpid + '"}',
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (msg) {
                    $("#kp_" + kpid).remove();
                    $("#update_success_msg").text("Delete Successful").fadeOut(2000);
                },
                error: function (response) {
                    showAlert(response.responseText);
                }
            });
        }
    });

    //edit a keypair
    $(".keypair_label").live("click", function () {
        //clear the optional fields
        $("#keypair_private_key").val("");
        $("#keypair_passphrase").val("");

        //fill them
        $("#keypair_id").val($(this).parents(".keypair").attr("id"));
        $("#keypair_name").val($(this).html());

        //show stars for the private key and passphrase if they were populated
        //the server sent back a flag denoting that
        var pk = "";

        if ($(this).parents(".keypair").attr("has_pk") == "true")
            pk += "**********\n";

        $("#keypair_private_key").val(pk);


        if ($(this).parents(".keypair").attr("has_pp") == "true")
            $("#keypair_passphrase").val("!2E4S6789O");


        $("#keypair_dialog").dialog('open');
    });


	//override the search click button as defined on managepagecommon.js, because this page is now ajax!
	$("#item_search_btn").die();
	//and rebind it
	$("#item_search_btn").live("click", function () {
        GetAccounts();
    });
    
    //the test connection buttton
    $("#test_connection_btn").button({ icons: { primary: "ui-icon-link"} });
	$("#test_connection_btn").live("click", function () {
        TestConnection();
    });

    $(".account_help_btn").tipTip({
        defaultPosition: "right",
        keepAlive: false,
        activation: "hover",
        maxWidth: "400px",
        fadeIn: 100
    });
});

function pageLoad() {
    ManagePageLoad();
}

function GetProviderClouds() {
	var provider = $("#ddlProvider").val();

    $.ajax({
        type: "POST",
        async: false,
        url: "uiMethods.asmx/wmGetProviderClouds",
        data: '{"sProvider":"' + provider + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (response) {
            var provider = jQuery.parseJSON(response.d);

            // all we want here is to loop the clouds
            $("#ddlTestCloud").empty();
            $.each(provider.Clouds, function(id, cloud){
            	$("#ddlTestCloud").append("<option value=\"" + id + "\">" + cloud.Name + "</option>");
			});
			
			//we can't allow testing the connection if there are no clouds
			if ($("#ddlTestCloud option").length == 0)
				$("#test_connection_btn").hide();
            else
				$("#test_connection_btn").show();
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
}

function TestConnection() {
	SaveItem(0);

    var account_id = $("#hidCurrentEditID").val();
    var cloud_id = $("#ddlTestCloud").val();

    if (cloud_id.length == 36 && account_id.length == 36)
    {    
		ClearTestResult();
		$("#conn_test_result").text("Testing...");
	    
	    $.ajax({
	        type: "POST",
	        async: false,
	        url: "awsMethods.asmx/wmTestCloudConnection",
	        data: '{"sAccountID":"' + account_id + '","sCloudID":"' + cloud_id + '"}',
	        contentType: "application/json; charset=utf-8",
	        dataType: "json",
	        success: function (response) {
				try
				{
		        	var oResultData = jQuery.parseJSON(response.d);
					if (oResultData != null)
					{
						if (oResultData.result == "success") {
							$("#conn_test_result").css("color","green");
							$("#conn_test_result").text("Connection Successful.");
						}
						if (oResultData.result == "fail") {
							$("#conn_test_result").css("color","red");
							$("#conn_test_result").text("Connection Failed.");
							$("#conn_test_error").text(unpackJSON(oResultData.error));
						}
					}
				}
				catch(err)
				{
					alert(err);
					ClearTestResult();
				}
	        },
	        error: function (response) {
	            showAlert(response.responseText);
	        }
	    });
	} else {
		ClearTestResult();
		$("#conn_test_result").css("color","red");
		$("#conn_test_result").text("Unable to test.  Please try again.");
	}
}

function GetAccounts() {
    $.ajax({
        type: "POST",
        async: false,
        url: "cloudAccountEdit.aspx/wmGetAccounts",
        data: '{"sSearch":"' + $("#ctl00_phDetail_txtSearch").val() + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (response) {
            $('#accounts').html(response.d);
            //gotta restripe the table
            initJtable(true, true);
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
}

function setLabels() {
	if ($("#ddlProvider").val() == "Amazon AWS" || $("#ddlProvider").val() == "Eucalyptus")
	{
		$("#login_label").text("Access Key");
		$(".password_label").text("Secret Key");
	} else {
		$("#login_label").text("Login ID");
		$(".password_label").text("Password");
	}
}

function LoadEditDialog(editID) {
    clearEditDialog();
    $("#hidMode").val("edit");

    $("#hidCurrentEditID").val(editID);

    FillEditForm(editID);
	setLabels();	
	
	//clear out any test results
	ClearTestResult();
	
    $('#edit_dialog_tabs').tabs('select', 0);
    $('#edit_dialog_tabs').tabs( "option", "disabled", [] );
    $("#edit_dialog").dialog("option", "title", "Modify Account");
    $("#edit_dialog").dialog('open');

}

function ClearTestResult() {
	$("#conn_test_result").css("color","green");
	$("#conn_test_result").empty();
	$("#conn_test_error").empty();
}

function FillEditForm(sEditID) {
    $.ajax({
        type: "POST",
        async: false,
        url: "uiMethods.asmx/wmGetCloudAccount",
        data: '{"sID":"' + sEditID + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (response) {
            //update the list in the dialog
            if (response.d.length == 0) {
                showAlert('error no response');
                // do we close the dialog, leave it open to allow adding more? what?
            } else {
                var account = jQuery.parseJSON(response.d);

                // show the assets current values
                $("#txtAccountName").val(account.Name);
                $("#txtAccountNumber").val(account.AccountNumber)
                $("#ddlProvider").val(account.Provider);
                $("#txtLoginID").val(account.LoginID);
                $("#txtLoginPassword").val(account.LoginPassword);
                $("#txtLoginPasswordConfirm").val(account.LoginPassword);

                if (account.IsDefault) $("#chkDefault").attr('checked', true);
                //if (account.AutoManage == "1") $("#chkAutoManageSecurity").attr('checked', true);
                
                //the account result will have a list of all the clouds on this account.
                $("#ddlTestCloud").empty();
                $.each(account.Clouds, function(id, cloud){
                	$("#ddlTestCloud").append("<option value=\"" + id + "\">" + cloud.Name + "</option>");
   				});	
			
				//we can't allow testing the connection if there are no clouds
				if ($("#ddlTestCloud option").length == 0)
					$("#test_connection_btn").hide();
	            else
					$("#test_connection_btn").show();
			}
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });

    //get the keypairs
    GetKeyPairs(sEditID);
}

function GetKeyPairs(sEditID) {
    $.ajax({
        type: "POST",
        async: false,
        url: "cloudAccountEdit.aspx/GetKeyPairs",
        data: '{"sID":"' + sEditID + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (response) {
            $('#keypairs').html(response.d);
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
}

function SaveItem(close_after_save) {
	//used for changing the global dropdown if needed
	var old_label = $('#ctl00_ddlCloudAccounts option:selected').text();
    
    var bSaved = false;
    var bSave = true;
    var strValidationError = '';

    //some client side validation before we attempt to save
    var sAccountID = $("#hidCurrentEditID").val();

    var sAccountName = $("#txtAccountName").val();
    if (sAccountName == '') {
        bSave = false;
        strValidationError += 'Account Name required.<br />';
    };

    if ($("#txtLoginPassword").val() != $("#txtLoginPasswordConfirm").val()) {
        bSave = false;
        strValidationError += 'Passwords do not match.';
    };

    if (bSave != true) {
        showInfo(strValidationError);
        return false;
    }

    var args = '{"sMode":"' + $("#hidMode").val() + '", \
    	"sAccountID":"' + sAccountID + '", \
        "sAccountName":"' + sAccountName + '", \
        "sAccountNumber":"' + $("#txtAccountNumber").val() + '", \
        "sProvider":"' + $("#ddlProvider").val() + '", \
        "sLoginID":"' + $("#txtLoginID").val() + '", \
        "sLoginPassword":"' + $("#txtLoginPassword").val() + '", \
        "sLoginPasswordConfirm":"' + $("#txtLoginPasswordConfirm").val() + '", \
        "sIsDefault":"' + ($("#chkDefault").attr("checked") ? "1" : "0") + '", \
        "sAutoManageSecurity":"' + ($("#chkAutoManageSecurity").attr("checked") ? "1" : "0") + '"}';


	$.ajax({
        type: "POST",
        async: false,
        url: "uiMethods.asmx/wmSaveAccount",
        data: args,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (response) {
        	try {
	            var account = jQuery.parseJSON(response.d);
		        if (account) {
					//if there are errors or info, we're closing the dialog.
					//just makes things cleaner regarding the "mode" (add or edit)
		        	if (account.info) {
		            	$("#edit_dialog").dialog('close');
	        			showInfo(account.info);
		        	} else if (account.error) {
		            	$("#edit_dialog").dialog('close');
		        		showAlert(account.error);
		        	} else {
						// clear the search field and fire a search click, should reload the grid
		                $("[id*='txtSearch']").val("");
						GetAccounts();
		
						var dropdown_label = account.Name + ' (' + account.Provider + ')';
						//if we are adding a new one, add it to the dropdown too
						if ($("#hidMode").val() == "add") {
				            $('#ctl00_ddlCloudAccounts').append($('<option>', { value : account.ID }).text(dropdown_label)); 
				          	//if this was the first one, get it in the session by nudging the change event.
				          	if ($("#ctl00_ddlCloudAccounts option").length == 1)
				          		$("#ctl00_ddlCloudAccounts").change();
		          		} else {
		          			//we've only changed it.  update the name in the drop down if it changed.
		          			if (old_label != dropdown_label)
		          				$('#ctl00_ddlCloudAccounts option[value="' + account.ID + '"]').text(dropdown_label);
		          		}
			            
			            if (close_after_save) {
			            	$("#edit_dialog").dialog('close');
		            	} else {
			            	//we aren't closing? fine, we're now in 'edit' mode.
			            	$("#hidMode").val("edit");
		            		$("#hidCurrentEditID").val(account.ID);
		            		$("#edit_dialog").dialog("option", "title", "Modify Account");	
		            	}
		            	bSaved = true;
	          		}
		        } else {
		            showAlert(response.d);
		        }
			} catch (ex) {
				showAlert(response.d);
			}
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
    
    return bSaved;
}

function ShowItemAdd() {
    clearEditDialog();
    $("#hidMode").val("add");

	setLabels();	
	GetProviderClouds();

	//clear out any test results
	ClearTestResult();

    $('#edit_dialog_tabs').tabs('select', 0);
    $('#edit_dialog_tabs').tabs( "option", "disabled", [1] );
    $('#edit_dialog').dialog('option', 'title', 'Create a New Account');
    $("#edit_dialog").dialog('open');
    $("#txtAccountName").focus();
}

function SaveKeyPair() {
    var kpid = $("#keypair_id").val().replace(/kp_/, "");
    var name = $("#keypair_name").val();
	//pack up the PK field, JSON doesn't like it
    var pk = packJSON($("#keypair_private_key").val());
    var pp = $("#keypair_passphrase").val();
    var account_id = $("#hidCurrentEditID").val();

    //some client side validation before we attempt to save
    if (name == '') {
        showInfo("KeyPair Name is required.");
        return false;
    };

    $("#update_success_msg").text("Saving...").show().fadeOut(2000);

    $.ajax({
        type: "POST",
        url: "cloudAccountEdit.aspx/SaveKeyPair",
        data: "{'sKeypairID' : '" + kpid + "','sAccountID' : '" + account_id + "','sName' : '" + name + "','sPK' : '" + pk + "','sPP' : '" + pp + "'}",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (msg) {
            if (msg.d == "") {
                if (kpid) {
                    //find the label and update it
                    $("#kp_" + kpid + " .keypair_label").html(name);
                } else {
                    //re-get the list
                    GetKeyPairs(account_id);
                }
                $("#update_success_msg").text("Save Successful").show().fadeOut(2000);
                $("#keypair_dialog").dialog('close');
            }
            else {
                showAlert(msg.d);
            }
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
}

function DeleteItems() {
    $("#update_success_msg").text("Deleting...").show().fadeOut(2000);

    var ArrayString = $("#hidSelectedArray").val();
    $.ajax({
        type: "POST",
        url: "uiMethods.asmx/wmDeleteAccounts",
        data: '{"sDeleteArray":"' + ArrayString + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (msg) {
        	var do_refresh = false;
        	
			//first, which one is selected?
			var current = $("#mySelect option:selected").val();

        	//remove the deleted ones from the cloud account dropdown
			myArray = $("#hidSelectedArray").val().split(',');
			$.each(myArray, function(name, value) {
				//whack it
				$('#ctl00_ddlCloudAccounts option[value="' + value + '"]').remove();
				//if we whacked what was selected, flag for change push
				if (value == current)
					do_refresh = true;
			});
            
            if (do_refresh)
            	$('#ctl00_ddlCloudAccounts').change();
            
            //update the list in the dialog
            if (msg.d.length == 0) {
                $("#hidSelectedArray").val("");
                $("#delete_dialog").dialog('close');

                // clear the search field and fire a search click, should reload the grid
                $("[id*='txtSearch']").val("");
				GetAccounts();

                $("#update_success_msg").text("Delete Successful").show().fadeOut(2000);
            } else {
                showAlert(msg.d);
            }
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
}
