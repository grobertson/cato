$(document).ready(function () {
    //NOTE: this is the main jQuery function that will execute
    //when the DOM is ready.  Things you want defined on 'page load' should 
    //go in here.

    //use this to define constants, set up jQuery objects, etc.

    $('#main-menu').load("uiMethods/wmGetMenu", function() {
	    $("ul.sf-menu").supersubs({
	        minWidth: 18,   // minimum width of sub-menus in em units 
	        maxWidth: 27,   // maximum width of sub-menus in em units 
	        extraWidth: .5     // extra width can ensure lines don't sometimes turn over 
	        // due to slight rounding differences and font-family 
	    }).superfish();  // call supersubs first, then superfish, so that subs are 
	    // not display:none when measuring. Call before initialising 
	    // containing tabs for same reason.
	});

    $('#header_cloud_accounts').load("uiMethods/wmGetCloudAccountsForHeader");

    //the cloud accounts dropdown updates the server session
    $("#header_cloud_accounts").change(function () {
        $("#update_success_msg").text("Updating...").show();

        var account_id = $(this).val();
        $.ajax({
            type: "POST",
            async: false,
            url: "uiMethods.asmx/wmSetActiveCloudAccount",
            data: '{"sAccountID":"' + account_id + '"}',
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (msg) {
                $("#update_success_msg").text("Update Successful").fadeOut(2000);

                //some pages have cloud content, but they are all different.
                //This expects a page to have the following function...
                //if it doesn't, nothing really happens after the ajax call.
                //if it does, it will do some sort of nice clean refresh logic.
                CloudAccountWasChanged();

                if (msg.length > 0) {
                    showInfo(msg);
                }
            },
            error: function (response) {
                showAlert(response.responseText);
            }
        });
    });
});


// Menu
$(function () {
    var tabContainers = $('div.tabs > div');
    tabContainers.hide().filter(':home').hide();
    $('div.tabs ul.tabNavigation a').click(function () {
        tabContainers.slideUp();
        tabContainers.filter(this.hash).slideDown();
        //$('div.tabs ul.tabNavigation a').removeClass('selected');
        //$(this).addClass('selected');
    }).filter(':first').click();
});
// End Menu


//the timer that keeps the heartbeat updated
window.setInterval(updateHeartbeat, 120000);

//and the jquery ajax it performs
function updateHeartbeat() {
    $.ajax({
        type: "GET",
        url: "uiMethods/wmUpdateHeartbeat",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (msg) {
            if (msg) {
                showAlert(msg);
            }
        },
        error: function (response) {
            //nothing to do here but throw you back to the login page.
            location.href = "/logout?msg=heartbeat failed"
        }
    });
}

function registerCato()
{
	//update the setting
	updateSetting("general","register_cato","registered");
	
	//open the form
	openWindow('http://community.cloudsidekick.com/register-cato?utm_source=cato_app&amp;utm_medium=menu&amp;utm_campaign=app', 'ask', 'location=no,status=no,scrollbars=yes,resizable=yes,width=800,height=700');
	
	//this might not be visible, but try to remove it anyway.
	$("#registercato").remove();
}