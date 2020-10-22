# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PurchaseInvoice(Document):
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
        self.perform_balance_change(self.get("credit_to"), "credit")
        self.perform_balance_change(self.get("expense_account"), "expense")
        
    def perform_balance_change(self, account, account_type):
        doc = frappe.get_doc("Accounts", account)
        if doc.opening_balance:
            if account_type == "credit":
                doc.opening_balance -= self.get("total_amount")
            elif account_type == "expense":
                doc.opening_balance += self.get("total_amount")
            doc.save()
            
    def make_gl_entry(self):
        from accounting.accounting.general_ledger import make_gl_entries
        gl_entry = [];
        gl_entry.append({
            "posting_date": self.get("posting_date"),
            "account": self.get("credit_to"),
            "party": self.get("party"),
            "voucher_no": self.get("name"),
            "voucher_type": "Purchase Invoice",
            "debit_amount": 0.00,
            "credit_amount": self.get("total_amount"),
            "balance": frappe.db.get_value("Accounts", self.get("credit_to"), "opening_balance"),
            "due_date": self.get("payment_due_date")
        })
        gl_entry.append({
            "posting_date": self.get("posting_date"),
            "account": self.get("expense_account"),
            "party": self.get("party"),
            "voucher_no": self.get("name"),
            "voucher_type": "Purchase Invoice",
            "debit_amount": self.get("total_amount"),
            "credit_amount": 0.00,
            "balance": frappe.db.get_value("Accounts", self.get("expense_account"), "opening_balance"),
            "due_date": self.get("payment_due_date")
        })

        if gl_entry:
            make_gl_entries(gl_entry)

@frappe.whitelist()
def make_payment_entry(source_name, target_doc=None):
    from frappe.model.mapper import get_mapped_doc

    doclist = get_mapped_doc("Purchase Invoice", source_name , {
        "Purchase Invoice": {
            "doctype": "Payment Entry",
            "field_map": {
				"amount_paid": "total_amount"
			},
            "validation": {
                "docstatus": ["=", 1]
            }
        }
    }, target_doc)

    return doclist
