# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from accounting.accounting.general_ledger import make_gl_entries, make_reverse_gl_entries
from frappe.utils import nowdate

class SalesInvoice(Document):
    def validate(self):
        self.set_item_rate_and_amount()
        self.set_total_quantity_and_amount()
        self.check_quantity()

    def set_item_rate_and_amount(self):
        for item in self.get("items"):
            item.rate = frappe.db.get_value("Item", item.item, "standard_rate")
            item.qty = flt(item.qty, item.precision("qty"))
            item.amount = item.rate * item.qty
            
    def set_total_quantity_and_amount(self):
        self.total_qty, self.total_amount = 0, 0
        for item in self.get("items"):
            self.total_qty = flt(self.total_qty) + flt(item.qty, item.precision("qty"))
            self.total_amount = flt(self.total_amount) + flt(item.amount, item.precision("amount"))

    def check_quantity(self):
        for item in self.get("items"):
            if item.qty and item.qty <= 0:
                frappe.throw("One or more quantity is required for each product")

    def on_submit(self):
        self.balance_change()
        self.make_gl_entry()

    def on_cancel(self):
        self.ignore_linked_doctypes = ('GL Entry')
        make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)

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

    doclist = get_mapped_doc("Sales Invoice", source_name , {
        "Sales Invoice": {
            "doctype": "Payment Entry",
            "field_map": {
                "total_amount": "amount_paid",
                "debit_to": "account_paid_from",
                "income_account": "account_paid_to"
            },
            "validation": {
                "docstatus": ["=", 1]
            }
        }
    }, target_doc)

    return doclist

@frappe.whitelist(allow_guest=True)
def add_to_cart(item_name, user, save=True, submit=False):
    user = set_user(user)
    si = get_user_cart(user)
    if si:
        return update_sales_invoice(item_name, 1, si, save, submit)
    else:
        return make_sales_invoice(item_name, 1, user, save, submit)

@frappe.whitelist(allow_guest=True)
def make_sales_invoice(item_name, qty, user, save=True, submit=False):
    si = frappe.new_doc("Sales Invoice")
    si.party = user
    si.posting_date = nowdate()
    si.payment_due_date = nowdate()
    si.debit_to = "Debtors"
    si.income_account = "Creditors"
    si.set("items",[
        {
            "item": item_name,
            "qty": qty
        }
    ])

    if save or submit:
        si.insert()
        if submit:
            si.submit()
    
    return si

@frappe.whitelist(allow_guest=True)
def update_sales_invoice(item_name, qty, si, save=True, submit=False):
    si = frappe.get_doc("Sales Invoice", si)
    items = si.items
    if item_name:
        item_found = False
        for item in items:
            if item.item == item_name:
                item_found = True
                item.update({
                    "qty": flt(qty, item.precision("qty"))
                })
                break
        if not item_found:
            si.append("items", {
                "item": item_name,
                "qty": qty
            })
    if save or submit:
        si.save()
        if submit:
            si.submit()
    return si

def set_user(user):
    if user:
        email = frappe.db.get_value("User", user, "email")
        customer = frappe.db.sql(""" select party_name from`tabParty` where party_email=%s and party_type="Customer" """, email, as_dict=1)
        if not customer:
            party = frappe.new_doc("Party")
            party.party_name = user
            party.party_type = "Customer"
            party.party_email = email
            party.insert()
        elif customer:
            user = customer[0].party_name
    return user

def get_user_cart(user, get_full_details=False):
    si = frappe.db.sql(""" select name from `tabSales Invoice` where party=%s and docstatus=0 """, user, as_dict=1)
    if not si:
        return None
    else:
        return frappe.get_doc("Sales Invoice", si[0].name) if get_full_details else si[0].name

@frappe.whitelist(allow_guest=True)
def display_user_cart(user, get_full_details):
    set_user(user)
    return get_user_cart(user, get_full_details)