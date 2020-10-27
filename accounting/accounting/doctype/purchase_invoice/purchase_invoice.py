# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from accounting.accounting.general_ledger import make_gl_entries, make_reverse_gl_entries

class PurchaseInvoice(Document):
    def validate(self):
        self.set_item_rate_and_amount()
        self.set_total_quantity_and_amount()
        self.check_quantity()

    def set_item_rate_and_amount(self):
        for item in self.get("items"):
            item.rate = frappe.db.get_value("Item", item.item, "standard_rate")
            item.amount = item.rate * item.qty
            
    def set_total_quantity_and_amount(self):
        self.total_qty, self.total_amount = 0, 0
        for item in self.get("items"):
            self.total_qty = flt(self.total_qty) + flt(item.qty, item.precision("qty"))
            self.total_amount = flt(self.total_amount) + flt(item.amount, item.precision("amount"))

    def check_quantity(self):
        for item in self.get("items"):
            if item.qty <= 0:
                frappe.throw("One or more quantity is required for each product")

    def on_submit(self):
        self.balance_change()
        self.make_gl_entry()

    def on_cancel(self):
        self.ignore_linked_doctypes = ('GL Entry')
        make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)

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
				"total_amount": "amount_paid",
                "expense_account": "account_paid_from",
                "credit_to": "account_paid_to"
			},
            "validation": {
                "docstatus": ["=", 1]
            }
        }
    }, target_doc)

    return doclist
