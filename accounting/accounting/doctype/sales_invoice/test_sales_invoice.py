# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from frappe.utils import nowdate
from accounting.accounting.doctype.accounts.test_accounts import create_account, delete_account
from accounting.accounting.doctype.journal_entry.test_journal_entry import get_gl_entries, delete_gl_entries
from accounting.accounting.doctype.sales_invoice.sales_invoice import make_sales_invoice

class TestSalesInvoice(unittest.TestCase):

    def setUp(self):
        create_account("ACC-100","_Test Debtors", "Asset", "Assets")
        create_account("ACC-100","_Test Creditors", "Liability", "Liabilities")

    def tearDown(self):
        delete_account("_Test Debtors")
        delete_account("_Test Creditors")
    
    def test_sales_invoice_creation(self):
        si = make_sales_invoice("Headphones", 1, "_Test Debtors", "_Test Creditors",  True, True)

        gl_entries = get_gl_entries(si.name, "Sales Invoice")
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

        delete_gl_entries(gl_entries)
        
        si.cancel()
        si.delete()

    def test_with_negative_quantity(self):
        si = make_sales_invoice("Headphones", -1, "_Test Debtors", "_Test Creditors", False, False)
        self.assertRaises(frappe.exceptions.ValidationError, si.insert)
        si.items[0].update({
            "qty": 1
        })
        si.insert()
        si_entry = frappe.db.sql(""" select * from `tabSales Invoice` where name=%s """, si.name, as_dict=1)
        self.assertTrue(si_entry)
        si.delete()

    def test_reverse_ledger_entry(self):
        si = make_sales_invoice("Headphones", 1, "_Test Debtors", "_Test Creditors", True, True)

        gl_entries = get_gl_entries(si.name, "Sales Invoice")
        original_gl_entries_count = len(gl_entries)

        si.cancel();
        gl_entries = get_gl_entries(si.name, "Sales Invoice")

        self.assertTrue(len(gl_entries)/2 == original_gl_entries_count)

        for gl in gl_entries:
            self.assertTrue(gl.is_cancelled)
        
        delete_gl_entries(gl_entries)
        si.delete()


