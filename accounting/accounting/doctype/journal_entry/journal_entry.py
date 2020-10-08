# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class JournalEntry(Document):
    def validate(self):
        self.validate_total_debit_and_credit()


    def validate_total_debit_and_credit(self):
        self.set_total_debit_credit()
        if self.difference:
            frappe.throw(_("Total Debit must be equal to Total Credit. The difference is {0}").format(self.difference))
        
    def set_total_debit_credit(self):
        self.total_debit, self.total_credit, self.difference = 0, 0, 0
        for account in self.get("accounting_entries"):
            if account.debit and account.credit:
                frappe.throw(_("You cannot credit and debit same account at the same time"))
        
            self.total_debit = flt(self.total_debit) + flt(account.debit, account.precision("debit"))
            self.total_credit = flt(self.total_credit) + flt(account.credit, account.precision("credit"))
        self.difference = flt(self.total_debit, self.precision("total_debit")) - flt(self.total_credit, self.precision("total_credit"))
