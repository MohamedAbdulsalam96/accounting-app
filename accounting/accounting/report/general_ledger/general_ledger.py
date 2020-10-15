# Copyright (c) 2013, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, _dict
from frappe.utils import getdate, cstr, flt, fmt_money

def execute(filters=None):
    columns, data = [], []
    validate_filters(filters)
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def validate_filters(filters):
    if not filters.get("from_date") and not filters.get("to_date"):
        frappe.throw(_("{0} and {1} are mandatory").format(frappe.bold(_("From Date")), frappe.bold(_("To Date"))))
    
    if filters.from_date > filters.to_date:
        frappe.throw(_("From Date must be before To Date"))
    
def get_columns(filters):
    columns = [
        {
            "label": _("GL Entry"),
            "fieldname": "gl_entry",
            "fieldtype": "Link",
            "options": "GL Entry",
            "hidden": 1
        },
        {
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 90
        },
        {
            "label": _("Accounts"),
            "fieldname": "account",
            "fieldtype": "Link",
            "options": "Accounts",
            "width": 180
        },
        {
            "label": _("Debit ({0})").format('INR'),
            "fieldname": "debit_amount",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("Credit ({0})").format('INR'),
            "fieldname": "credit_amount",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("Balance ({0})").format('INR'),
            "fieldname": "balance",
            "fieldtype": "Float",
            "width": 130
        },
        {
            "label": _("Voucher Type"),
            "fieldname": "voucher_type",
            "width": 120
        },
        {
            "label": _("Voucher No"),
            "fieldname": "voucher_no",
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
            "width": 180
        },
        {
            "label": _("Party"),
            "fieldname": "party",
            "width": 100
        }
    ]

    return columns

def get_data(filters):
    gl_entries = get_gl_entries(filters)
    data = get_data_with_opening_closing(filters, gl_entries)
    result = get_result_as_list(data, filters)
    return result

def get_gl_entries(filters):
    order_by_statement = "order by voucher_no"

    gl_entries = frappe.db.sql(
        """
        select name as gl_entry, posting_date, account, party, voucher_type, voucher_no, debit_amount, credit_amount
        from `tabGL Entry` {conditions} {order_by_statement}
        """.format(conditions=get_conditions(filters),order_by_statement=order_by_statement),
        filters, as_dict=1)

    return gl_entries

def get_conditions(filters):
    conditions = []
    if filters.get("account"):
        lft, rgt = frappe.db.get_value("Accounts", filters["account"], ["lft", "rgt"])
        conditions.append("""account in (select name from tabAccounts
            where lft>=%s and rgt<=%s and docstatus<2)""" % (lft, rgt))

    if filters.get("voucher_no"):
        conditions.append("voucher_no=%(voucher_no)s")

    if filters.get("party"):
        conditions.append("party = %(party)s")
    
    from frappe.desk.reportview import build_match_conditions
    match_conditions = build_match_conditions("GL Entry")

    if match_conditions:
        conditions.append(match_conditions)
    
    return "where {}".format(" and ".join(conditions)) if conditions else ""

def get_totals_dict():
    def _get_debit_credit_dict(label):
        return _dict(
            account="'{0}'".format(label),
            debit_amount=0.0,
            credit_amount=0.0
        )
    return _dict(
        opening = _get_debit_credit_dict(_('Opening')),
        total = _get_debit_credit_dict(_('Total')),
        closing = _get_debit_credit_dict(_('Closing (Opening + Total)')))

def get_data_with_opening_closing(filters, gl_entries):
    data = []

    gle_map = _dict(totals=get_totals_dict(), entries=[])
    totals, entries = get_accountwise_gle(filters, gl_entries, gle_map)
    data.append(totals.opening)
    data += entries
    data.append(totals.total)
    data.append(totals.closing)

    return data


def get_accountwise_gle(filters, gl_entries, gle_map):
    totals = get_totals_dict()
    entries = []

    def update_value_in_dict(data, key, gle):
        data[key].debit_amount += flt(gle.debit_amount)
        data[key].credit_amount += flt(gle.credit_amount)

    from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
    for gle in gl_entries:
        if gle.posting_date < from_date:
            update_value_in_dict(totals, 'opening', gle)
            update_value_in_dict(totals, 'closing', gle)

        elif gle.posting_date <= to_date:
            update_value_in_dict(totals, 'total', gle)
            update_value_in_dict(totals, 'closing', gle)

        entries.append(gle)

    return totals, entries

    
def get_result_as_list(data, filters):
    balance = 0

    for d in data:
        if not d.get('posting_date'):
            balance = 0

        balance = get_balance(d, balance, 'debit_amount', 'credit_amount')
        d['balance'] = balance

    return data

def get_balance(row, balance, debit_field, credit_field):
    balance += (row.get(debit_field, 0) -  row.get(credit_field, 0))

    return balance

