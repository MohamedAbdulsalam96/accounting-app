# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

class TestAccounts(unittest.TestCase):
    
    def test_account_creation(self):
        if not frappe.db.exists("Accounts", "Test Asset Account"):
            acc = frappe.new_doc("Accounts")
            acc.parent_accounts = "Assets"
            acc.account_number ="ACC-190"
            acc.account_name ="Test Asset Account"
            acc.account_type = "Asset"
            acc.insert()
        
        account_number, account_name = frappe.db.get_value("Accounts", "Test Asset Account", ["account_number","account_name"])
        print(account_name, account_number)
        self.assertEqual(account_name, "Test Asset Account")
        self.assertEqual(account_number, "ACC-190")
        frappe.delete_doc("Accounts", "Test Asset Account")
