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


# This extension populates a variable with all of the common system information
# that should be available on most flavors of Linux.
# Commands are issued over an SSH connection, and the results
# are an XML variable.

proc linux_info { command } {
	set proc_name linux_info

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
		os_flavor "uname"
		architecture "uname -m"
		df "df"
		uptime "uptime | awk '{ gsub(/,/, \"\"); print $3 }'"
		date "date"
		hostname "hostname"
		ifconfig "ifconfig"
		process_count "ps ax | wc -l"
		cpus "grep -c 'processor' /proc/cpuinfo"
		cpu_model "awk -F':' '/^model name/ { print $2 }' /proc/cpuinfo"
		cpu_vendor "awk -F':' '/^vendor_id/ { print $2 }' /proc/cpuinfo"
		cpu_speed "awk -F':' '/^cpu MHz/ { print $2 }' /proc/cpuinfo"
		cpu_cache "awk -F':' '/^cache size/ { print $2 }' /proc/cpuinfo"
		meminfo "cat /proc/meminfo"
		free "free -m"
		load_average "uptime | awk -F'load average:' '{ print $2 }'"
		num_net_interfaces "netstat -i | grep -Ev \"^Iface|^Kernel|^lo\" | wc -l"
		kernel_modules "lsmod | grep -vE \"^Module\" | wc -l"
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