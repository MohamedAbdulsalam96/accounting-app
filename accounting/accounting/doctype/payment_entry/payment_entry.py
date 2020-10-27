# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from accounting.accounting.general_ledger import make_gl_entries, make_reverse_gl_entries

class PaymentEntry(Document):

    def on_submit(self):
        self.balance_change()
        self.make_gl_entry()

    def on_cancel(self):
        self.ignore_linked_doctypes = ('GL Entry')
        make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)
    
    def balance_change(self):
        self.perform_balance_change(self.get("account_paid_from"), "from")
        self.perform_balance_change(self.get("account_paid_to"), "to")
        
    def perform_balance_change(self, account, account_type):
        doc = frappe.get_doc("Accounts", account)
        if doc.opening_balance:
            if account_type == "from":
                doc.opening_balance -= self.get("amount_paid")
            elif account_type == "to":
                doc.opening_balance += self.get("amount_paid")
            doc.save()

    def make_gl_entry(self):
        gl_entry = [];
        gl_entry.append({
            "posting_date": self.get("posting_date"),
            "account": self.get("account_paid_from"),
            "party": self.get("party"),
            "voucher_no": self.get("name"),
            "voucher_type": "Payment Entry",
            "debit_amount": 0.00,
            "credit_amount": self.get("amount_paid"),
            "balance": frappe.db.get_value("Accounts", self.get("account_paid_from"), "opening_balance"),
            "due_date": self.get("payment_due_date")
        })
        gl_entry.append({
            "posting_date": self.get("posting_date"),
            "account": self.get("account_paid_to"),
            "party": self.get("party"),
            "voucher_no": self.get("name"),
            "voucher_type": "Payment Entry",
            "debit_amount": self.get("amount_paid"),
            "credit_amount": 0.00,
            "balance": frappe.db.get_value("Accounts", self.get("account_paid_to"), "opening_balance"),
            "due_date": self.get("payment_due_date")
        })

        if gl_entry:
            make_gl_entries(gl_entry)