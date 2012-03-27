#!/usr/bin/env python

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

import os
import sys
import time

base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))
lib_path = os.path.join(base_path, "services", "lib")
sys.path.append(lib_path)

from catocommon import catocommon

class Poller(catocommon.CatoService):

    poller_mode = ""

    def start_submitted_tasks(self, get_num):

        task_list = []
        sql = """select ti.task_instance, ti.asset_id, 
            ti.schedule_instance 
            from tv_task_instance ti
            join task t on t.task_id = ti.task_id
            where ti.task_status = 'Submitted'
            and ti.ce_node = %s
            order by task_instance asc limit %s"""
        #self.output(sql % (self.instance_id, get_num))
        rows = self.db.select_all(sql, (self.instance_id, get_num))
        if rows:
            for row in rows:
                task_instance = row[0]
                self.output("Considering Task Instance: %d" % (task_instance))
                asset_id = row[1]
                schedule_instance = row[2]

                if task_instance > 0:
                    error_flag = 0
                    self.output("Starting process ...")

                    cmd_line = "nohup %s/services/bin/cato_task_engine.tcl %d >& %s/ce/%d.log &" % (self.home, task_instance, self.logfiles_path, task_instance)

                    pid = os.system(cmd_line)
                    self.output("The process id for task instance %d is %s" % (task_instance, pid))
                    if pid > "":
                        sql = """update task_instance set task_status = 'Staged',
                            pid = %d where task_instance = %s"""
                        self.db.exec_db(sql, (pid, task_instance))
                    else:
                        sql = """update task_instance set task_status = 'Staged'
                            where task_instance = %s"""
                        self.db.exec_db(sql, (task_instance))
                        time.sleep(0.01)
                        
    def update_to_error(self, the_pid):
    
        self.output("Setting tasks with PID %d and Processing status to Error..." % (the_pid))                  

        sql = """update task_instance set task_status = 'Error',
            completed_dt = now() 
            where pid = %d and task_status = 'Processing'"""
        self.db.exec_db(sql, (the_pid))

    def update_cancelled(self, task_instance):

        sql = """update task_instance set task_status = 'Cancelled', 
            completed_dt = now() where task_instance = %d"""
        self.db.exec_db(sql, (task_instance))

    def kill_ce_pid(self, pid):

        self.output("Killing process %d", (pid))
        os.kill(int(pid), signal.SIGHUP)

    def check_processing(self):

        db_pids = []
        os_pids = []
        sql = """select distinct pid from tv_task_instance 
            where ce_node = %d and task_status = 'Processing' 
            and pid is not null"""
        rows = self.db.select_all(sql, (self.instance_id))
        if rows:
            for row in rows:
                db_pids.append(row[0])

        cmd_line = """ps U%s -opid | grep "%s/services/bin/cato_task_engine.tcl" | grep -v grep""" % (self.user, self.home)

        os_pids = os.system(cmd_line)
        print cmd_line
        print os_pids
        print db_pids
        not_running_pids = list(set(db_pids)-set(os_pids))
        for pid in not_running_pids:
            self.update_to_error(pid)

    def update_load(self):
        
        loads = os.getloadavg()
        sql = """update application_registry set load_value = %s 
            where id = %s"""
        self.db.exec_db(sql, (loads[0], self.instance_id))

    def get_settings(self):

        previous_mode = self.poller_mode

        sql = """select mode_off_on, loop_delay_sec, max_processes 
            from poller_settings where id = 1"""

        row = self.db.select_row(sql, ())
        self.output(row)
        if row:
            self.poller_mode = row[0]
            self.loop = row[1]
            self.max_processes = row[2]
        else:
            self.output("Select from poller_settings did not work, using previous values")
        
        sql = """select admin_email from messenger_settings where id = 1""" 
        self.admin_email = self.db.select_col(sql, ())

        if previous_mode != "" and previous_mode != self.poller_mode:
            self.output("*** Control Change: Mode is now %s" % 
                (self.poller_mode))

    def get_aborting(self): 

        sql = """select task_instance, pid from tv_task_instance 
            where ce_node = %d and task_status = 'Aborting' 
            order by task_instance asc"""

        rows = self.db.select_all(sql, (self.instance_id))
        if rows:
            for row in rows:
                self.output("Cancelling task_instance %d, pid %d" %
                    (row[0], row[1]))

                if row[1]:
                    self.kill_ce_pid(row[1])
                self.update_cancelled(row[0])

    def main_process(self):
        """main process loop, parent class will call this"""

        self.update_load()
        #self.get_aborting()
        #self.check_processing()

        ### TO DO - need to get process count from linux
        process_count = 0
        get_processes = self.max_processes - process_count

        self.start_submitted_tasks(get_processes)

if __name__ == "__main__":

    poller = Poller("cato_poller")
    print dir(poller)
    poller.startup()
    poller.service_loop()

