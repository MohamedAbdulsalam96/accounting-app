# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

class TestAccounts(unittest.TestCase):
    
    def test_account_creation(self):
        if not frappe.db.exists("Accounts", "Test Asset Account"):
            create_account("ACC-190","Test Asset Account","Asset", "Assets")
        
        account_number, account_name = frappe.db.get_value("Accounts", "Test Asset Account", ["account_number","account_name"])
        self.assertEqual(account_name, "Test Asset Account")
        self.assertEqual(account_number, "ACC-190")
        delete_account("Test Asset Account")

def create_account(account_number, account_name, account_type, parent_accounts):
    acc = frappe.new_doc("Accounts")
    acc.parent_accounts = parent_accounts
    acc.account_number = account_number
    acc.account_name = account_name
    acc.account_type = account_type
    acc.insert()
    
def delete_account(name):
    frappe.delete_doc("Accounts", name)
