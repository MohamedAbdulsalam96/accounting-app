# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from frappe.utils import nowdate
from accounting.accounting.doctype.accounts.test_accounts import create_account, delete_account

class TestPaymentEntry(unittest.TestCase):
    def setUp(self):
        create_account("ACC-100","_Test Debtors", "Asset", "Assets")
        create_account("ACC-100","_Test Creditors", "Liability", "Liabilities")

    def tearDown(self):
        delete_account("_Test Debtors")
        delete_account("_Test Creditors")
    
    def test_payment_entry_creation(self):
        pe = make_payment_entry(500, "Receive", True, True)

        gl_entries = frappe.db.sql(""" select * from `tabGL Entry` where voucher_no=%s and voucher_type='Payment Entry' """, pe.name, as_dict=1)
        self.assertTrue(gl_entries)

        expected_values = {
            "_Test Debtors": {
                "debit_amount" : 500,
                "credit_amount": 0
            },
            "_Test Creditors": {
                "debit_amount": 0,
                "credit_amount" : 500
            }
        }
        for field in ("debit_amount", "credit_amount"):
            for i, gle in enumerate(gl_entries):
                self.assertEqual(expected_values[gle.account][field], gle[field])

        for gl in gl_entries:
            frappe.delete_doc("GL Entry", gl.name)
        
        pe.cancel()
        pe.delete()

def make_payment_entry(amount, payment_type="Receive", save=True, submit=False ):
    pe = frappe.new_doc("Payment Entry")
    pe.posting_date = nowdate()
    pe.payment_due_date = nowdate()
    pe.payment_type = payment_type
    pe.party = "Jannat Patel"
    pe.account_paid_from = "_Test Creditors"
    pe.account_paid_to = "_Test Debtors"
    pe.amount_paid = amount

    if save or submit:
        pe.insert()

        if submit:
            pe.submit()

    return pe
