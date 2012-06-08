#!/usr/bin/env tclsh

#########################################################################
# Copyright 2011 Cloud Sidekick
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#########################################################################


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