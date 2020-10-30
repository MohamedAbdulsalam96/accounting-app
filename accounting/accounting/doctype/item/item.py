# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator

class Item(WebsiteGenerator):
	website = frappe._dict(
		page_title_field="item_name",
		condition_field="show_in_website",
		template="templates/generators/item/item.html",
		no_cache=1
	)

