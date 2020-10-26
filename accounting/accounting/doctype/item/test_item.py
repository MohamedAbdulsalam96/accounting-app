# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

def create_items(item_name, item_code, uom, standard_rate):
    item = frappe.new_doc("Item")
    item.item_code = item_code
    item.item_name = item_name
    item.uom = uom
    item.standard_rate = standard_rate
    item.insert()

def delete_existing_doc(item_name):
    if frappe.db.exists("Item", frappe.db.get_value("Item", {"item_name":item_name})):
        frappe.delete_doc("Item", frappe.db.get_value("Item", {"item_name": item_name}))

class TestItem(unittest.TestCase):

    def setUp(self):
        frappe.set_user("Administrator")
        create_items("_Test Item 1","IT-101","KG",100)
        create_items("_Test Item 3","IT-102","KG",100)

    def tearDown(self):
        frappe.set_user("Administrator")
        delete_existing_doc("_Test Item 1")
        delete_existing_doc("_Test Item 3")

    def test_allowed_public(self):
        doc = frappe.get_doc("Item", frappe.db.get_value("Item",
            {"item_name":"_Test Item 1"}))
        self.assertTrue(frappe.has_permission("Item", doc=doc))

    def test_not_allowed_private(self):
        frappe.set_user("test1@example.com")
        doc = frappe.get_doc("Item", frappe.db.get_value("Item",
            {"item_name":"_Test Item 3"}))
        self.assertFalse(frappe.has_permission("Item", doc=doc))




