# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from frappe.utils import nowdate
from accounting.accounting.doctype.accounts.test_accounts import create_account, delete_account

class TestSalesInvoice(unittest.TestCase):

    def setUp(self):
        create_account("ACC-100","_Test Debtors", "Asset", "Assets")
        create_account("ACC-100","_Test Creditors", "Liability", "Liabilities")

    def tearDown(self):
        delete_account("_Test Debtors")
        delete_account("_Test Creditors")
    
    def test_sales_invoice_creation(self):
        si = make_sales_invoice(1, True, True)

        gl_entries = frappe.db.sql(""" select * from `tabGL Entry` where voucher_no=%s and voucher_type='Sales Invoice' """, si.name, as_dict=1)
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
        
        si.cancel()
        si.delete()

    def test_with_negative_quantity(self):
        si = make_sales_invoice(-1, False, False)
        self.assertRaises(frappe.exceptions.ValidationError, si.insert)
        si.items[0].update({
            "qty": 1
        })
        si.insert()
        si_entry = frappe.db.sql(""" select * from `tabSales Invoice` where name=%s """, si.name, as_dict=1)
        self.assertTrue(si_entry)
        si.delete()

def make_sales_invoice(qty, save=True, submit=False ):
    si = frappe.new_doc("Sales Invoice")
    si.party = "Jannat Patel"
    si.posting_date = nowdate()
    si.payment_due_date = nowdate()
    si.debit_to = "_Test Debtors"
    si.income_account = "_Test Creditors"
    si.set("items",[
        {
            "item": "Headphones",
            "qty": qty
        }
    ])

    if save or submit:
        si.insert()
        if submit:
            si.submit()
    

    return si

