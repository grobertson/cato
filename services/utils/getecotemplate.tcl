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

package require base64
package require sha256  1.0.2
package require tdom
package require http
#package require tls
#::http::register https 443 ::tls::socket

# This script will get a task using a task_id as input.

set ::API_URL [lindex [split [lindex $::argv 0]] 0]
set ::ECOTEMPLATE_ID [lindex [split [lindex $::argv 1]] 0]
set ::INCLUDE_TASKS [lindex [split [lindex $::argv 2]] 0]
set ::KEY [lindex [split [lindex $::argv 3]] 0]
set ::PASSWORD [lindex [split [lindex $::argv 4]] 0]
set ::SILENT [lindex [split [lindex $::argv 5]] 0]
set ::RESULT ""

proc output {args} {
	if {"$::SILENT" != "-silent"} {
		set output_string [lindex $args 0]
		#puts "\n[clock format [clock seconds] -format "%Y-%m-%d %H:%M:%S"] :: $output_string"
		puts "$output_string"
		flush stdout
	}
}

# this proc does an HTTP POST to the specified URL, and sends the encoded task xml as form data
proc http_get {url} {
	# if you wanted to do a GET instead it would look like this, get is a lot pickier about what's in the querystring... specifically newlines.
	# catch {set token [::http::geturl $url -timeout [expr 10 * 1000]]} error_code
	
	#but this is big data and it has newlines... so we're using POST
	set query ""
	catch {set token [::http::geturl $url -timeout [expr 60 * 1000]]} error_code
	
	if {[string match "::http::*" $error_code] == 0} {
		set output_buffer "<error>$error_code</error>"
		#output "\n\nHTTP Error:\n$error_code" 1
	} else {
		if {"[::http::status $token]" != "ok" || [::http::ncode $token] != 200} {
			set output_buffer "<error>HTTP Error: [::http::status $token] [::http::code $token] [::http::data $token]</error>"
			error $output_buffer 2011
		
		} else {
			set output_buffer [::http::data $token]
			#output $output_buffer 1
		}
		
	}
	if {[info exists token] == 1} {
		::http::cleanup $token 
	}

	set ::RESULT $output_buffer
}

#############
# MAIN CODE #
#############

output "Cato GetEcotemplate Utility\n"

# do not continue unless we have all the required arguments
if {"$::API_URL" == "" || "$::ECOTEMPLATE_ID" == "" || "$::INCLUDE_TASKS" == "" || "$::KEY" == "" || "$::PASSWORD" == ""} {
	output "Usage:\n getecotemplate.tcl <url> <ecotemplate_id> <yes/no> <key> <password>\n\nExample:\n getecotemplate.tcl localhost 550e8400-e29b-41d4-a716-446655440000 yes 545b60a5-17e7-4fe0-b28f-7c4722c76544 foo"
	exit
}

# a little useful information
output "Using the API at: $::API_URL"
output "ID: $::ECOTEMPLATE_ID"
output "INCLUDE TASKS? $::INCLUDE_TASKS"
output "API Key: $::KEY"

# timestamp must be this exact format, in UTC time, and with the dashes URL encoded
# 2011-12-20T13%3A58%3A14
set timestamp [string map {: %3A} [clock format [clock seconds] -format "%Y-%m-%dT%H:%M:%S" -gmt true]]
#output "Timestamp: $timestamp"

set string_to_sign "action=GetEcotemplate&key=$::KEY&timestamp=$timestamp"
#output "String to sign: $string_to_sign"

set signature [::sha2::hmac $::PASSWORD $string_to_sign]
#output "Signature: $signature"

# build the URL we will connect to
set url "http://$::API_URL/pages/api.ashx?id=$::ECOTEMPLATE_ID&include_tasks=$::INCLUDE_TASKS&$string_to_sign&signature=$signature"

output "\n\nConnecting using: $url"

# and do the connection
http_get $url

# process the results
output $::RESULT

# and we're done
exit


