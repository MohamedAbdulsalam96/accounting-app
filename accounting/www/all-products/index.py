# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals

import frappe

@frappe.whitelist(allow_guest=True)
def get_website_products():
    return frappe.db.get_list("Item",
		{"show_in_website": ["=", True]},
        ["*"],
        ignore_permissions=True )