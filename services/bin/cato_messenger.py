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
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.mime.text import MIMEText
#from email.Utils import formatdate

base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))
lib_path = os.path.join(base_path, "services", "lib")
sys.path.append(lib_path)
from catocryptpy import catocryptpy

from catocommon import catocommon

class Messenger(catocommon.CatoService):
    
    ### to do: add attachment logic into Messenger

    messenger_mode = ""

    def get_settings(self):

        previous_mode = self.messenger_mode

        sql = """select mode_off_on, loop_delay_sec, retry_max_attempts, smtp_server_addr, 
                smtp_server_user, smtp_server_password, smtp_server_port, from_email, from_name
            from messenger_settings where id = 1"""

        row = self.db.select_row(sql, ())
        #self.output(row)
        if row:
            self.messenger_mode = row[0]
            self.loop = row[1]
            self.min_depth = row[2]
            self.max_days = row[3]
            self.retry_attempts = row[2]
            self.smtp_server = row[3]
            self.smtp_user = row[4]
            password = row[5]

            if password:
                self.smtp_pass = catocryptpy.decrypt_string(password, self.config["key"])
            else:
                self.smtp_pass = ""

            self.smtp_port = row[6]
            self.smtp_from_email = row[7]
            self.smtp_from_name = row[8]

            if self.smtp_from_name == "":
                self.smtp_from = """\"%s\"<%s>""" % (self.smtp_from_name, self.smtp_from_email)
            else:
                self.smtp_from = self.smtp_from_email
            
            #output "Smtp from address is $::SMTP_FROM"
        else:
            self.output("select from messenger_settings did not work, using previous values")

        sql = "select admin_email from messenger_settings where id = 1"
        row = self.db.select_row(sql, ())
        self.admin_email = row[0]
        
        if previous_mode != "" and previous_mode != self.messenger_mode:
            self.output("*** Control Change: Mode is now %s" % 
                (self.messenger_mode))

    def update_msg_status(self, msg_id, status, err_msg):

        if status == 1:
            sql = """update message set status = 1, date_time_completed = now(), 
                    num_retries = ifnull(num_retries,0) + 1, error_message = %s where msg_id = %s"""
            self.db.exec_db(sql, (err_msg, msg_id))
        else:
            sql = """update message set status = %s, date_time_completed = now(), num_retries = 0, 
                    error_message = '' where msg_id = %s"""
            self.db.exec_db(sql, (status, msg_id))


    def check_for_emails(self):
        
        sql = """select msg_id, status, msg_to, msg_subject, msg_body, msg_cc, msg_bcc 
                from message where status in (0,1) and ifnull(num_retries,0) <= %s 
                order by msg_id asc"""
        rows = self.db.select_all(sql, (self.retry_attempts))
        if rows:
            self.output("Processing %d messages...", (len(rows)))
            try: 
                server = smtplib.SMTP_SSL(self.smtp_server, int(self.smtp_port))
                server.login(self.smtp_user, self.smtp_pass)
            except Exception, e:
                for row in rows:
                    msg_id = row[0]
                    err_msg = str(e)
                    self.update_msg_status(msg_id, 1, err_msg)

            for row in rows:
                msg_id = row[0]
                status = row[1]
                msg_to = row[2]
                msg_subject = row[3]
                msg_body = row[4]
                msg_cc = row[5]
                msg_bcc = row[6]

                msg = MIMEMultipart('alternative')
                msg["To"] = msg_to
                msg["From"] = self.smtp_from
                msg["Subject"] = msg_subject
                #msg["Date"] = formatdate(localtime=True)
                part1 = MIMEText(msg_body, 'plain')
                part2 = MIMEText(msg_body, 'html')
                msg.attach(part1)
                msg.attach(part2)
                try:
                    server.sendmail(self.smtp_from, msg_to, msg.as_string())
                except Exception, e:
                    err_msg = str(e)
                    self.update_msg_status(msg_id, 1, err_msg)
                else:
                    self.update_msg_status(msg_id, 2, "")
                del(msg)

            server.quit()


    def main_process(self):
        """main process loop, parent class will call this"""
        self.check_for_emails()


if __name__ == "__main__":

    messenger = Messenger("cato_messenger")
    messenger.startup()
    messenger.service_loop()

