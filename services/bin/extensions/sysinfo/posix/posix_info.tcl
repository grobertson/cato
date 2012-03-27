#!/usr/bin/env tclsh

# This extension populates a variable with the most basic system information
# that should be available on any POSIX compliant system.
# Commands are issued over an SSH connection, and the results
# are an XML variable.

proc posix_info { command } {
	set proc_name posix_info

	get_xml_root $command
	set conn_name [$::ROOT selectNodes string(conn_name)]
	set cmd_timeout [$::ROOT selectNodes string(timeout)]
	set pos_resp [fix [$::ROOT selectNodes string(positive_response)]]
	set neg_resp [fix [$::ROOT selectNodes string(negative_response)]]
	set result_var [fix [$::ROOT selectNodes string(result_variable)]]
	del_xml_root

	set doc [dom createDocument sysinfo]
	set root [$doc documentElement]	

	#all the commands we wanna execute
	array set info_items {
		uname "uname"
		df "df"
		uptime "uptime"
		date "date"
		hostname "hostname"
		ifconfig "ifconfig"
		process_count "ps ax | wc -l"
	}
	
	#now, for each bit of info we wanna grab...
	foreach {name cmd_text} [array get info_items] {
		set new_cmd [new_command $conn_name $cmd_text $cmd_timeout $pos_resp $neg_resp]
		set result [execute_command $new_cmd]
		set node [$doc createElement $name]
		$node appendChild [$doc createTextNode "$result"]
		$root appendChild $node
	}

	set_variable $result_var [$root asXML]
}