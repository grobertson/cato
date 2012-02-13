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

set PROCESS_NAME cato_scheduler
set ::CATO_HOME [file dirname [file dirname [file dirname [file normalize $argv0]]]]
source $::CATO_HOME/services/bin/common.tcl
read_config

proc check_schedules {} {
	set proc_name check_schedules
	set sql "select ap.schedule_id, min(ap.plan_id) as plan_id, ap.task_id, 
		ap.action_id, ap.ecosystem_id, ap.parameter_xml, ap.debug_level, min(ap.run_on_dt), ap.account_id
		from action_plan  ap
		where run_on_dt < now() group by schedule_id"

	set rows [::mysql::sel $::CONN $sql -list]
	foreach row $rows {
		run_schedule_instance $row
	}
}

proc split_clean {it} {
        set proc_name split_clean
        set the_list ""
        foreach x [split $it ,] {
                if {$x ne ""} {
                        set the_list [concat $the_list $x]
                }
        }
        return $the_list
}

proc stp_z {it} {
	set proc_name stp_z
	if {$it eq "00"} {
		return 0
	} else {
		return [string trimleft $it 0]
	}
}

proc get_month_dates {days_of_month months start_dt} {

        set dates ""

        set start [clock scan [clock format $start_dt -format {%Y-%m-%d}]]
        set now_day [clock format $start -format "%d"]
        set month_day $start
        set date_ctr 1
        for {set day 0} {$day < 365} {incr day} {
                set this_month [expr [stp_z [clock format $month_day -format "%m"]] - 1]
                set this_day [expr [stp_z [clock format $month_day -format "%d"]] - 1]
                if {[lsearch $months $this_month] > -1 && [lsearch $days_of_month $this_day] > -1} {
                        lappend dates $month_day
                        if {$date_ctr == $::MAX_DAYS} {
                                break
                        }
                        incr date_ctr
                }
                set month_day [clock add $month_day 1 day]
        }
        return $dates
}

proc get_weekday_dates {days_of_week months start_dt} {
        set dates ""
        foreach day $days_of_week {
                set dates [concat $dates [get_dates_for_weekday $day 52 $months $start_dt]]
        }
        return [lsort $dates]
}

proc get_dates_for_weekday {weekday num_weeks months start_dt} {
        set dates ""
        set start [clock scan [clock format $start_dt -format {%Y-%m-%d}]]
        set now_day [clock format $start -format "%u"]
        if {$now_day == 7} {
                set now_day 0
        }
	if {$weekday > $now_day} {
		set days [expr $weekday - $now_day]
	} elseif {$now_day > $weekday} {
		set days [expr 6 - $weekday]
	} else {
		set days 0
	}

        set weekday [clock add $start $days day]

        for {set week 0} {$week < $num_weeks} {incr week} {
                #set now_date [clock format $now -format "%Y-%m-%d"]

                set this_month [expr [stp_z [clock format $weekday -format "%m"]] -1]
                if {[lsearch $months $this_month]} {
                        lappend dates $weekday
                }
                set weekday [clock add $weekday 1 week]
        }
        return $dates
}

proc get_times {dates hours minutes start_dt num_to_find} {
        set date_times ""
        #set hours [split_clean $hours]
        #set minutes [split_clean $minutes]
        set found_times 0
        foreach date $dates {
                foreach h $hours {
                        foreach min $minutes {
                                set date_time [expr ($h*3600 + $min*60) + $date]
                                if {$date_time < $start_dt} {
                                        continue
                                }
                                lappend date_times $date_time
                                incr found_times
                                if {$found_times == $num_to_find} {
                                        return $date_times
                                }
                        }
                }
        }
        return $date_times
}


proc expand_this_schedule {sched_row} {
	set proc_name expand_this_schedule
	set id [lindex $sched_row 0]
	set now [lindex $sched_row 1]
	set months [lindex $sched_row 2]
	set days_or_weeks [lindex $sched_row 3]
	set days [lindex $sched_row 4]
	set hours [split_clean [lindex $sched_row 5]]
	set minutes [split_clean [lindex $sched_row 6]]
	set start_dt [lindex $sched_row 7]
	set task_id [lindex $sched_row 8]
	set action_id [lindex $sched_row 9]
	set ecosystem_id [lindex $sched_row 10]
	set parameter_xml [lindex $sched_row 11]
	set debug_level [lindex $sched_row 12]
	set start_instances [lindex $sched_row 13]
	set account_id [lindex $sched_row 14]
	if {$start_dt == 0 || $start_dt == ""} {
		set start_dt $now
	} else {
		set start_dt [expr $start_dt + 1]
	}
	set days [split_clean [string map $::DAY_MAP $days]]
	set months [split_clean $months]

	set the_dates ""
	if {$days_or_weeks == 1} {
		set dates [get_weekday_dates $days $months $start_dt]
	} else {
		set dates [get_month_dates $days $months $start_dt]
	}
	if {[llength $dates] > 0} {
		set dates [get_times $dates $hours $minutes $start_dt $start_instances]
	}

	set dates [lsort -unique $dates]
	foreach date $dates {
		set date [clock format $date -format "%Y-%m-%d %H:%M:%S"]
		set sql "insert into action_plan (task_id,run_on_dt,action_id,ecosystem_id,parameter_xml,debug_level,source,schedule_id, account_id)
			values ('$task_id', '$date', '$action_id', '$ecosystem_id', '$parameter_xml', '$debug_level', 'schedule', '$id', '$account_id')"
		::mysql::exec $::CONN $sql
	}	
}
proc run_schedule_instance {instance_row} {
	set proc_name run_schedule_instance

	#set sql "update schedule_instance set status = 'Processing' where schedule_instance = '$instance'"
	#::mysql::exec $::CONN $sql
	set schedule_id [lindex $instance_row 0]
	set plan_id [lindex $instance_row 1]
	set task_id [lindex $instance_row 2]
	set action_id [lindex $instance_row 3]
	set ecosystem_id [lindex $instance_row 4]
	set parameter_xml [lindex $instance_row 5]
	set debug_level [lindex $instance_row 6]
	set run_on_dt [lindex $instance_row 7]
	set account_id [lindex $instance_row 8]

	set sql "call addTaskInstance ('$task_id',NULL,'$schedule_id','$debug_level','$plan_id','$parameter_xml','$ecosystem_id','$account_id')"
#output $sql
	set ti [::mysql::sel $::CONN $sql -list]
	output "Started task instance $ti for schedule id $schedule_id and plan id $plan_id"
	set sql "insert into action_plan_history (plan_id, task_id, run_on_dt, action_id, ecosystem_id, parameter_xml, debug_level, source, schedule_id, task_instance, account_id)
		values ('$plan_id', '$task_id', '$run_on_dt', '$action_id', '$ecosystem_id', '$parameter_xml', '$debug_level', 'schedule', '$schedule_id', '$ti', '$account_id')"
	::mysql::exec $::CONN $sql
	set sql "delete from action_plan where plan_id = '$plan_id'"
	::mysql::exec $::CONN $sql

}
proc clear_scheduled_action_plans {} {
	### delete action_plan rows upon scheduler startup to remove any backlog
	set sql "delete from action_plan where source = 'schedule'"
	::mysql::exec $::CONN $sql
}
proc expand_schedules {} {
	set proc_name expand_schedules
	set sql "select distinct(a.schedule_id), unix_timestamp() as now, a.months, a.days_or_weeks, a.days, 
		a.hours, a.minutes, max(unix_timestamp(ap.run_on_dt)), a.task_id, a.action_id, a.ecosystem_id,
		a.parameter_xml, a.debug_level, $::MIN_DEPTH - count(ap.schedule_id) as num_to_start, a.account_id
		from action_schedule a
		left outer join action_plan ap on ap.schedule_id = a.schedule_id
		group by a.schedule_id
		having count(*) < $::MIN_DEPTH"

        set rows [::mysql::sel $::CONN $sql -list]
	foreach row $rows {
		#output "remaining $remaining_instances, min depth $::MIN_DEPTH"
		expand_this_schedule $row
	}

}
proc balance_task_instances {} {

	set sql "select id from tv_application_registry where app_name = 'cato_poller' and master = 1 order by load_value asc limit 1"
	::mysql::sel $::CONN $sql
	set row [::mysql::fetch $::CONN]
	set id [lindex $row 0]
	if {"$id" ne ""} {	
		set sql "update task_instance set ce_node = $id where task_status = 'Submitted' and ce_node is NULL"
		::mysql::exec $::CONN $sql
	}
}
proc manage_poller_nodes {} {

	# get the poller loop value in seconds
	set sql "select loop_delay_sec from poller_settings"
	::mysql::sel $::CONN $sql
	set row [::mysql::fetch $::CONN]
	set poller_delay [lindex $row 0]

	#turn poller off if the heartbeat is longer than twice the poller loop
	set sql "update application_registry set master = 0 
		where time_to_sec(timediff(now(),heartbeat)) > ($poller_delay * 2)
		and master = 1 and app_name = 'cato_poller'"
	::mysql::exec $::CONN $sql

	#turn it back on if the heartbeat is current
	set sql "update application_registry set master = 1 
		where time_to_sec(timediff(now(),heartbeat)) <= ($poller_delay * 2)
		and master = 0 and app_name = 'cato_poller'"
	::mysql::exec $::CONN $sql

	#check for submitted tasks that are assigned a non-master ce node, meaning they are orphaned
	set sql "update task_instance set ce_node = NULL, task_status = 'Submitted' where task_status in ('Staged','Submitted') and ce_node is not null
		 and ce_node not in (select id from tv_application_registry where app_name = 'cato_poller' and master = 1)"
	::mysql::exec $::CONN $sql

}
proc get_settings {} {
	
	set ::PREVIOUS_MODE ""
	
	if {[info exists ::MODE]} {
		set ::PREVIOUS_MODE $::MODE
	}

	set sql "select mode_off_on, loop_delay_sec, schedule_min_depth, schedule_max_days from scheduler_settings where id = 1"
	::mysql::sel $::CONN $sql
	set row [::mysql::fetch $::CONN]
	set ::MODE [lindex $row 0]
	set ::LOOP [lindex $row 1]
	set ::MIN_DEPTH [lindex $row 2]
	set ::MAX_DAYS [lindex $row 3]
	if {$::MIN_DEPTH <= 0} {
		set ::MIN_DEPTH 1
	}
	if {$::MAX_DAYS > 360} {
		set ::MAX_DAYS 360
	}
        set sql "select admin_email from messenger_settings where id = 1"
	::mysql::sel $::CONN $sql
	set row [lindex [::mysql::fetch $::CONN] 0]
	set ::ADMIN_EMAIL [lindex $row 0]
	
	#did the run mode change? not the first time of course previous_mode will be ""
	if {"$::PREVIOUS_MODE" != "" && "$::PREVIOUS_MODE" != "$::MODE"} {
		output "*** Control Change: Mode is now $::MODE"
	}

}
proc initialize_process {} {
	clear_scheduled_action_plans
	set ::DAY_MAP {00, 0, 01, 1, 02, 2, 03, 3, 04, 4, 05, 5, 06, 6, 07, 7, 08, 8, 09, 9,}

}
proc main_process {} {

	expand_schedules
	check_schedules
	balance_task_instances
	manage_poller_nodes
}
main
exit 0
