# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SalesInvoice(Document):
    def validate(self):
        self.check_quantity()

    def check_quantity(self):
        for item in self.get("items"):
            if item.qty <= 0:
                frappe.throw("One or more quantity is required for each product")

    def on_submit(self):
        self.balance_change()
        self.make_gl_entry()

    def balance_change(self):
        self.perform_balance_change(self.get("debit_to"), "debit")
        self.perform_balance_change(self.get("income_account"), "income")
        
    def perform_balance_change(self, account, account_type):
        doc = frappe.get_doc("Accounts", account)
        if doc.opening_balance:
            if account_type == "debit":
                doc.opening_balance += self.get("total_amount")
            elif account_type == "income":
                doc.opening_balance -= self.get("total_amount")
            doc.save()

    def make_gl_entry(self):
        from accounting.accounting.general_ledger import make_gl_entries
        gl_entry = [];
        gl_entry.append({
            "posting_date": self.get("posting_date"),
            "account": self.get("debit_to"),
            "party": self.get("party"),
            "voucher_no": self.get("name"),
            "voucher_type": "Sales Invoice",
            "debit_amount": self.get("total_amount"),
            "credit_amount": 0.00,
            "balance": frappe.db.get_value("Accounts", self.get("debit_to"), "opening_balance"),
            "due_date": self.get("payment_due_date")
        })
        gl_entry.append({
            "posting_date": self.get("posting_date"),
            "account": self.get("income_account"),
            "party": self.get("party"),
            "voucher_no": self.get("name"),
            "voucher_type": "Sales Invoice",
            "debit_amount": 0.00,
            "credit_amount": self.get("total_amount"),
            "balance": frappe.db.get_value("Accounts", self.get("income_account"), "opening_balance"),
            "due_date": self.get("payment_due_date")
        })

        if gl_entry:
            make_gl_entries(gl_entry)

@frappe.whitelist()
def make_payment_entry(source_name, target_doc=None):
    from frappe.model.mapper import get_mapped_doc

    print("heaven",source_name, target_doc)
    doclist = get_mapped_doc("Payment Entry", "", {
        "Payment Entry": {
            "doctype": "Payment Entry",
            "validation": {
                "docstatus": ["=", 1]
            }
        }
    }, target_doc)

    return doclist
