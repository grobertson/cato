$(document).ready(function () {
    //any page that includes this script will get the following dialog inner code
    //but the page requires a placeholder div... called "storm_run_dialog"
    var d = 'Filter: <input type="text" id="log_view_dialog_search" />' +
    	'<span id="lblMaxRows"># of Results <input id="log_view_dialog_records" /></span>' +
    	'<span id="log_search_btn">Search</span>' +
		'<table class="jtable" cellspacing="1" cellpadding="1" width="100%" style="font-size: 0.8em;">' +
		'<thead><tr>' +
        '<th width="125px">Date</th>' +
        '<th width="100px">User</th>' +
        '<th>Log</th>' +
        '</tr></thead>' +
		'<tbody id="log_view_dialog_results">' +
        '</tbody>';

    $("#log_view_dialog").prepend(d);

    //init the dialogs
    $("#log_view_dialog").dialog({
        autoOpen: false,
        modal: true,
        height: 650,
        width: 900,
        open: function (event, ui) { $(".ui-dialog-titlebar-close", ui).hide(); },
        buttons: {
            "Close": function () {
                CloseLogViewDialog();
            }
        }
    });

    $("#log_search_btn").button({ icons: { primary: "ui-icon-search"} });
    $("#log_search_btn").click(function () {
        GetLog();
    });

});


function ShowLogViewDialog(type, id, prefill) {
	g_log_object_id = id;
	g_log_object_type = type;
    $("#log_view_dialog").dialog('open');
    
    if (prefill) {
    	GetLog();
    }
}

function CloseLogViewDialog() {
    $("#log_view_dialog").dialog('close');
    $("#log_view_dialog_results").empty();
    $('#log_view_dialog :input').each(function () {
        var type = this.type;
        var tag = this.tagName.toLowerCase(); // normalize case
        if (type == 'text' || type == 'password' || tag == 'textarea')
            this.value = "";
        else if (type == 'checkbox' || type == 'radio')
            this.checked = false;
        else if (tag == 'select')
            this.selectedIndex = 0;
    });

    return false;
}

function GetLog() {
	$("#log_view_dialog_results").empty();
	
	search = $("#log_view_dialog_search").val();
	// will come from the pickers.
	from = "";
	to = "";
	records = $("#log_view_dialog_records").val();
    
    $.ajax({
        async: true,
        type: "POST",
        url: "uiMethods/wmGetLog",
        data: '{"sObjectID":"' + g_log_object_id + '", "sObjectType":"' + g_log_object_type + '", "sSearch":"' + search + '", "sFrom":"' + from + '", "sTo":"' + to + '", "sRecords":"' + records + '"}',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (response) {
        	if (response.error) {
        		showAlert(response.error);
        	} else if (response.log) {
	            //spin the json and build a table
	            $.each(response.log, function() {
                	$("#log_view_dialog_results").append("<tr><td>" + this[0] + "</td><td>" + this[1] + "</td><td>" + this[2] + "</td></tr>");
            	});
            	initJtable(true, false);
        	} else {
        		showInfo(response);
        	}
        },
        error: function (response) {
            showAlert(response.responseText);
        }
    });
}