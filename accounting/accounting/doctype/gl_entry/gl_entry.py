# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class GLEntry(Document):
	
	def make_gl_entry():
		gl_entry = frappe.new_doc('GL Entry')
		gl_entry.insert()
