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


# This extension populates a variable with the results of the 
# open source "Ohai" tool.

# Ohai returns JSON - can we use that or do we need to convert to XML?

proc ohai_info { command } {
	set proc_name ohai_info

	package require json

	get_xml_root $command
	set conn_name [$::ROOT selectNodes string(conn_name)]
	set cmd_timeout [$::ROOT selectNodes string(timeout)]
	set pos_resp [fix [$::ROOT selectNodes string(positive_response)]]
	set neg_resp [fix [$::ROOT selectNodes string(negative_response)]]
	set result_var [fix [$::ROOT selectNodes string(result_variable)]]
	del_xml_root

	#set doc [dom createDocument sysinfo]
	#set root [$doc documentElement]	

	set new_cmd [new_command $conn_name "ohai" $cmd_timeout $pos_resp $neg_resp]
	set result [execute_command $new_cmd]
	#set node [$doc createElement $name]
	#$node appendChild [$doc createTextNode "$result"]
	#$root appendChild $node

	set js [::json::json2dict $result]
	#puts $js
	#puts [dict get $js network default_gateway]
	
	set_variable $result_var $js
}