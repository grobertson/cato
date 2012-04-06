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

import pymysql

class Db(object):

	def __init__(self):
		self.conn = ""
		self.error = ""

	def connect_db(self, server="", port=3306, database="", user="", password=""):
		"""Establishes a connection as a class property."""

		try:
			self.conn = pymysql.connect(host=server, port=int(port), 
				user=user, passwd=password, db=database)
		except Exception, e:
			raise Exception(e)
	
	def ping_db(self):
		self.conn.ping(True)
	
	def select_all(self, sql, params=()):
		"""Gets a row set for a provided query."""
		if sql == "":
			print "select_all: SQL cannot be empty."
			return None
		
		try:
			c = self.conn.cursor()
			c.execute(sql, params)
			result = c.fetchall()
			c.close()
		except Exception, e:
			raise Exception(e)

		if result:
			return result
		else:
			return False


	def select_row(self, sql, params=()):
		"""Gets a single row for a provided query.  If there are multiple rows, the first is returned."""
		if sql == "":
			print "select_row: SQL cannot be empty."
			return None
		
		try:
			c = self.conn.cursor()
			c.execute(sql, params)
			result = c.fetchone()
			c.close()
		except Exception, e:
			raise Exception(e)

		if result:
			return result
		else:
			return False

	def select_col(self, sql, params=()):
		"""Gets a single value from the database.  If the query returns more than one column, the first is used."""
		if sql == "":
			print "select_column: SQL cannot be empty."
			return None
		
		try:
			c = self.conn.cursor()
			c.execute(sql, params)
			result = c.fetchone()
			c.close()
		except Exception, e:
			raise Exception(e)

		if result:
			return result[0]
		else:
			return False

	def exec_db(self, sql, params=()):
		"""Used for updates, inserts and deletes"""
		if sql == "":
			print "update: SQL cannot be empty."
			return None
		
		try:
			c = self.conn.cursor()
			c.execute(sql, params)
			self.conn.commit()
			c.close()
		except Exception, e:
			raise Exception(e)

		return True

	def close(self):
		"""Closes the database connection."""
		self.conn.close()

# Now something interesting...
# these functions all just call the ones above...
# with one difference - none of these throw exceptions.
# instead, they set the 'error' property of the class.
# GUI calls and other crash-proof services are made to expect messages, and display them nicely,
# and not be filled with lots of wasteful try:except blocks.

	def try_select_col(self, sql, params=()):
		try:
			return self.select_col(sql, params)
		except Exception, e:
			self.error = e.__str__()
			return False

	def try_exec_db(self, sql, params=()):
		try:
			self.exec_db(sql, params)
		except Exception, e:
			self.error = e.__str__()
			return False

		return True

