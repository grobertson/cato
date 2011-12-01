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
    $("#skip_registration_btn").click(function () {
        $("#update_success_msg").text("Updating...").show();

        $.ajax({
            type: "POST",
            async: false,
            url: "uiMethods.asmx/wmSetApplicationSetting",
            data: '{"sCategory":"general","sSetting":"register_cato","sValue":"skipped"}',
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (msg) {
                $("#update_success_msg").text("Update Successful").fadeOut(2000);
                
//here's where we'll figure out how to remove it from the page!
                if (msg.d.length > 0) {
                    showAlert(msg.d);
                }
            },
            error: function (response) {
                showAlert(response.responseText);
            }
        });
    });

});
