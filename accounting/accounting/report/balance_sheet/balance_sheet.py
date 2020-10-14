# Copyright (c) 2013, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from six import itervalues
import re
import functools
from frappe import _
from past.builtins import cmp
from frappe.utils import (flt, getdate, get_first_day, add_months, add_days, formatdate, cstr, cint)


def execute(filters=None):
    columns, data = [], []

    fiscal_year = get_fiscal_year_data(filters.fiscal_year)
    asset = get_data("Asset", fiscal_year)
    liability = get_data("Liability", fiscal_year)

    data = []
    data.extend(asset or [])
    data.extend(liability or [])

    columns = get_columns(filters.fiscal_year)
    return columns, data

def get_fiscal_year_data(fiscal_year):
    return frappe.db.sql(""" select start_date, end_date from `tabFiscal Year` where name=%s """, fiscal_year, as_dict=1)

def get_data(account_type, fiscal_year):
    accounts = get_accounts(account_type)
    if not accounts:
        return None
    accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)
    gl_entries_by_account = {}
    for root in frappe.db.sql("""select lft, rgt from tabAccounts
            where account_type=%s and ifnull(parent_accounts, '') = ''""", account_type, as_dict=1):

        set_gl_entries_by_account(fiscal_year[0].start_date, fiscal_year[0].end_date, root.lft, root.rgt, gl_entries_by_account, ignore_closing_entries=False)
    
    accumulate_values_into_parents(accounts, accounts_by_name, fiscal_year)
    out = prepare_data(accounts, fiscal_year)

    return out

def get_accounts(account_type):
    return frappe.db.sql("""
        select *
        from `tabAccounts`
        where account_type=%s order by lft""", (account_type), as_dict=True)

def filter_accounts(accounts, depth=10):
    accounts_by_name = {}
    parent_children_map = {}

    for account in accounts:
        accounts_by_name[account.account_name] = account
        parent_children_map.setdefault(account.parent_accounts or None, []).append(account)

    filtered_accounts = []
    def add_to_list(parent, level):
        if level < depth:
            children = parent_children_map.get(parent) or []
            sort_accounts(children, is_root=True if parent==None else False)

            for child in children:
                child.indent = level
                filtered_accounts.append(child)
                add_to_list(child.name, level + 1)

    add_to_list(None, 0)

    return filtered_accounts, accounts_by_name, parent_children_map

def sort_accounts(accounts, is_root=False, key="name"):
    """Sort root types as Asset, Liability, Equity, Income, Expense"""

    def compare_accounts(a, b):
        if re.split('\W+', a[key])[0].isdigit():
            # if chart of accounts is numbered, then sort by number
            return cmp(a[key], b[key])
        elif is_root:
            if a.report_type != b.report_type and a.report_type == "Balance Sheet":
                return -1
            if a.root_type != b.root_type and a.root_type == "Asset":
                return -1
            if a.root_type == "Liability" and b.root_type == "Equity":
                return -1
            if a.root_type == "Income" and b.root_type == "Expense":
                return -1
        else:
            # sort by key (number) or name
            return cmp(a[key], b[key])
        return 1

    accounts.sort(key = functools.cmp_to_key(compare_accounts))

def set_gl_entries_by_account(start_date, end_date, root_lft, root_rgt, gl_entries_by_account, ignore_closing_entries=False):
    accounts = frappe.db.sql_list("""select name from `tabAccounts` where lft >= %s and rgt <= %s""", (root_lft, root_rgt))
    conditions = "account in ({})".format(", ".join([frappe.db.escape(d) for d in accounts]))
    gl_filters = {
            "from_date": start_date,
            "to_date": end_date
        }

    gl_entries = frappe.db.sql("""select posting_date, account, debit_amount, credit_amount, balance from `tabGL Entry`
            where {conditions}
            and posting_date <= %(to_date)s
            order by account, posting_date""".format(conditions=conditions), gl_filters, as_dict=True)

    for entry in gl_entries:
            gl_entries_by_account.setdefault(entry.account, []).append(entry)

    return gl_entries_by_account

def accumulate_values_into_parents(accounts, accounts_by_name, fiscal_year):
    for d in reversed(accounts):
        if d.parent_accounts:
            print(d.parent_accounts, accounts_by_name[d.parent_accounts].get("opening_balance",0.0))
            accounts_by_name[d.parent_accounts]["opening_balance"] = accounts_by_name[d.parent_accounts].get("opening_balance",0.0) + d.get("opening_balance", 0.0)
            
def prepare_data(accounts, fiscal_year):
    data = []
    start_date = fiscal_year[0].start_date.strftime("%Y-%m-%d")
    end_date = fiscal_year[0].end_date.strftime("%Y-%m-%d")

    for d in accounts:
        row = frappe._dict({
            "account": _(d.name),
            "parent_accounts": _(d.parent_accounts) if d.parent_accounts else '',
            "indent": flt(d.indent),
            "start_date": start_date,
            "end_date": end_date,
            "account_type": d.account_type,
            "is_group": d.is_group,
            "opening_balance": d.get("opening_balance", 0.0),
            "account_name": ('%s - %s' %(_(d.account_number), _(d.account_name))
                if d.account_number else _(d.account_name))
        })
        data.append(row)
    return data

def get_columns(fiscal_year):
    columns = [
    {
        "fieldname": "account",
        "label": _("Accounts"),
        "fieldtype": "Link",
        "options": "Accounts",
        "width": 300
    },
    {
        "fieldname": "opening_balance",
        "label" : fiscal_year,
        "fieldtype": "Currency",
        "width": 100
    }]
    return columns