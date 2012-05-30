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
g_newpw = "";

$(document).ready(function () {
    $('#txtLoginUser').focus();
    
    //if there's a 'msg' querystring, show it on a nice label
    var msg = getQuerystringVariable("msg");
    msg = urldecode(msg);
    if (msg) {
        $("#error_msg").text(msg);
        $(".loginerror").show();
    } else {
        $(".loginerror").hide();
        $("#error_msg").text("");
    }
    
	$("#username").keypress(function(e) {
		if(e.which == 13) {
			Login();
		}
	});

    $("#password_change_dialog").dialog({
        autoOpen: false,
        modal: true,
        bgiframe: false,
        buttons: {
            "OK": function () {
				Change();
            },
            Cancel: function () {
            	reset();
                $("#password_change_dialog").dialog("close");
            }
        }
    });

     
	$("#attempt_login_btn").button({ icons: { primary: "ui-icon-locked"} });
	$("#attempt_login_btn").click(function() { Login();	});
	$(".loginfield").keypress(function(e) {
		if(e.which == 13) { Login(); }
	});
 	
	$(".changefield").keypress(function(e) {
		if(e.which == 13) { Change(); }
	});


 	$("#forgot_password_btn").click(function() {
 		alert("Not yet implemented.");
 	});

	// get the welcome message
	$('#ltAnnouncement').load('/announcement');

});

function Login() {
	if ($("#username").val() == "" || $("#password").val() == "")
		return false;

    $.ajax({
        type: "POST",
        url: "/uiMethods/wmAttemptLogin",
        data: '{"username":"' + $("#username").val() + '", "password":"' + packJSON($("#password").val()) + '", "change_password":"' + g_newpw + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (response) {
			if (response.error) {
				$("#error_msg").html(response.error);
				reset();
			}
			if (response.info) {
				$("#error_msg").html(response.info);
				reset();
			}
			if (response.result) {
			    if (response.result == "change") {
			    	$("#password_change_dialog").dialog("open");
				}
			    if (response.result == "success") {
			    	// TODO check for expiration warnings and let the user know.
			    	location.href="/home";
				}
			}
        },
        error: function (response) {
            $("#error_msg").html(response.responseText);
        }
    });
}
function Change() {
	// do not submit if the passwords don't match
	pw1 = $("#password_change_dialog #new_password").val();
	pw2 = $("#password_change_dialog #new_password_confirm").val();
	
	if (pw1 != pw2) {
		alert("Passwords must match.");
		return false;	
	}
	
	g_newpw = packJSON(pw1);
	Login();
}

function reset() {
	$(":input").val("");
	$("#username").focus();
}