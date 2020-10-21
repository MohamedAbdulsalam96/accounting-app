# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

def create_items():
    print(frappe.flags.test_items_created)
    if frappe.flags.test_items_created:
        return

    frappe.set_user("Administrator")
    doc = frappe.get_doc({
        "doctype": "Item",
        "item_name": "_Test Item 1",
        "item_code": "IT-0101",
        "uom": "KG",
        "standard_rate": "100"
    }).insert()

    doc = frappe.get_doc({
        "doctype": "Item",
        "item_name": "_Test Item 3",
        "item_code": "IT-0103",
        "uom": "KG",
        "standard_rate": "100"
    }).insert()

    frappe.flags.test_items_created =  True

def delete_existing_doc(item_name):
    if frappe.db.exists("Item", frappe.db.get_value("Item", {"item_name":item_name})):
        frappe.delete_doc("Item", frappe.db.get_value("Item", {"item_name": item_name}))

class TestItem(unittest.TestCase):
    def setUp(self):
        #create_items()
        pass

    def tearDown(self):
        frappe.set_user("Administrator")

    def test_allowed_public(self):
        frappe.set_user("test1@example.com")
        doc = frappe.get_doc("Item", frappe.db.get_value("Item",
            {"item_name":"_Test Item 1"}))
        self.assertTrue(frappe.has_permission("Item", doc=doc))
        #delete_existing_doc("_Test Item 1")

    def test_not_allowed_private(self):
        frappe.set_user("test1@example.com")
        doc = frappe.get_doc("Item", frappe.db.get_value("Item",
            {"item_name":"_Test Item 3"}))
        self.assertFalse(frappe.has_permission("Item", doc=doc))
        #delete_existing_doc("_Test Item 3")




