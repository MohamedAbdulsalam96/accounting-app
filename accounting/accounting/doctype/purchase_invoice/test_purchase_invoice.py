# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from frappe.utils import nowdate
from accounting.accounting.doctype.accounts.test_accounts import create_account, delete_account

class TestPurchaseInvoice(unittest.TestCase):
    def setUp(self):
        create_account("ACC-100","_Test Debtors", "Asset", "Assets")
        create_account("ACC-100","_Test Creditors", "Liability", "Liabilities")

    def tearDown(self):
        delete_account("_Test Debtors")
        delete_account("_Test Creditors")
    
    def test_purchase_invoice_creation(self):
        pi = make_purchase_invoice(1, True, True)

        gl_entries = frappe.db.sql(""" select * from `tabGL Entry` where voucher_no=%s and voucher_type='Purchase Invoice' """, pi.name, as_dict=1)
        self.assertTrue(gl_entries)

        expected_values = {
            "_Test Debtors": {
                "debit_amount" : 3000,
                "credit_amount": 0
            },
            "_Test Creditors": {
                "debit_amount": 0,
                "credit_amount" : 3000
            }
        }
        for field in ("debit_amount", "credit_amount"):
            for i, gle in enumerate(gl_entries):
                self.assertEqual(expected_values[gle.account][field], gle[field])

        for gl in gl_entries:
            frappe.delete_doc("GL Entry", gl.name)
        
        pi.cancel()
        pi.delete()

    def test_with_negative_quantity(self):
        pi = make_purchase_invoice(-1, False, False)
        self.assertRaises(frappe.exceptions.ValidationError, pi.insert)
        pi.items[0].update({
            "qty": 1
        })
        pi.insert()
        pi_entry = frappe.db.sql(""" select * from `tabPurchase Invoice` where name=%s """, pi.name, as_dict=1)
        self.assertTrue(pi_entry)
        pi.delete()

def make_purchase_invoice(qty, save, submit):
    pi = frappe.new_doc("Purchase Invoice")
    pi.posting_date = nowdate()
    pi.payment_due_date = nowdate()
    pi.party = "Jannat Patel"
    pi.credit_to = "_Test Creditors"
    pi.expense_account = "_Test Debtors"
    pi.set("items",[
        {
            "item": "Headphones",
            "qty": qty
        }
    ])

    if save or submit:
        pi.insert()

        if submit:
            pi.submit()

    return pi
