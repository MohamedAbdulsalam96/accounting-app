# Copyright (c) 2013, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate
from accounting.accounting.report.balance_sheet.balance_sheet import filter_accounts, set_gl_entries_by_account

value_fields = ("opening_debit", "opening_credit", "debit_amount", "credit_amount", "closing_debit", "closing_credit")

def execute(filters=None):
	columns, data = [], []
	validate_filters(filters)
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def validate_filters(filters):
	fiscal_year = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ["start_date", "end_date"], as_dict=True)
	
	filters.from_date = getdate(fiscal_year.start_date)
	filters.to_date = getdate(fiscal_year.end_date)
	

def get_data(filters):
	accounts = frappe.db.sql("""select name, account_number, parent_accounts, account_name, account_type, lft, rgt
		from `tabAccounts` order by lft""", as_dict=True)

	if not accounts:
		return None
	
	accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)

	min_lft, max_rgt = frappe.db.sql("""select min(lft), max(rgt) from `tabAccounts`""")[0]

	gl_entries_by_account = {}

	opening_balances = get_opening_balances(filters)

	set_gl_entries_by_account(filters.from_date,filters.to_date, min_lft, max_rgt, gl_entries_by_account, ignore_closing_entries=False)

	total_row = calculate_values(accounts, gl_entries_by_account, opening_balances, filters)
	accumulate_values_into_parents(accounts, accounts_by_name)

	data = prepare_data(accounts, filters, total_row, parent_children_map)

	return data


def get_opening_balances(filters):
	query_filters = {
		"from_date": filters.from_date
	}

	gle = frappe.db.sql("""
		select
			account, sum(debit_amount) as opening_debit, sum(credit_amount) as opening_credit
		from `tabGL Entry`
		where
			(posting_date < %(from_date)s)
		group by account""", query_filters , as_dict=True)

	opening = frappe._dict()
	for d in gle:
		opening.setdefault(d.account, d)
	return opening


def calculate_values(accounts, gl_entries_by_account, opening_balances, filters):
	init = {
		"opening_debit": 0.0,
		"opening_credit": 0.0,
		"debit_amount": 0.0,
		"credit_amount": 0.0,
		"closing_debit": 0.0,
		"closing_credit": 0.0
	}

	total_row = {
		"account": "'" + _("Total") + "'",
		"account_name": "'" + _("Total") + "'",
		"warn_if_negative": True,
		"opening_debit": 0.0,
		"opening_credit": 0.0,
		"debit_amount": 0.0,
		"credit_amount": 0.0,
		"closing_debit": 0.0,
		"closing_credit": 0.0,
		"parent_accounts": None,
		"indent": 0
	}

	for d in accounts:
		d.update(init.copy())

		# add opening
		d["opening_debit"] = opening_balances.get(d.name, {}).get("opening_debit", 0)
		d["opening_credit"] = opening_balances.get(d.name, {}).get("opening_credit", 0)

		for entry in gl_entries_by_account.get(d.name, []):
			d["debit_amount"] += flt(entry.debit_amount)
			d["credit_amount"] += flt(entry.credit_amount)

		d["closing_debit"] = d["opening_debit"] + d["debit_amount"]
		d["closing_credit"] = d["opening_credit"] + d["credit_amount"]

		prepare_opening_closing(d)

		for field in value_fields:
			total_row[field] += d[field]

	return total_row

def prepare_opening_closing(row):
	dr_or_cr = "debit" if row["account_type"] in ["Asset", "Equity", "Expense"] else "credit"
	reverse_dr_or_cr = "credit" if dr_or_cr == "debit" else "debit"
	for col_type in ["opening", "closing"]:
		valid_col = col_type + "_" + dr_or_cr
		reverse_col = col_type + "_" + reverse_dr_or_cr
		row[valid_col] -= row[reverse_col]
		if row[valid_col] < 0:
			row[reverse_col] = abs(row[valid_col])
			row[valid_col] = 0.0
		else:
			row[reverse_col] = 0.0
		
def accumulate_values_into_parents(accounts, accounts_by_name):
	for d in reversed(accounts):
		if d.parent_account:
			for key in value_fields:
				accounts_by_name[d.parent_account][key] += d[key]

def prepare_data(accounts, filters, total_row, parent_children_map):
	data = []

	for d in accounts:
		# Prepare opening closing for group account
		if parent_children_map.get(d.account):
			prepare_opening_closing(d)

		has_value = False
		row = {
			"account": d.name,
			"parent_accounts": d.parent_accounts,
			"indent": d.indent,
			"from_date": filters.from_date,
			"to_date": filters.to_date,
			"account_name": ('{} - {}'.format(d.account_number, d.account_name)
				if d.account_number else d.account_name)
		}

		for key in value_fields:
			row[key] = flt(d.get(key, 0.0), 3)

			if abs(row[key]) >= 0.005:
				# ignore zero values
				has_value = True

		row["has_value"] = has_value
		data.append(row)

	data.extend([total_row])

	return data

def get_columns():
	return [
		{
			"fieldname": "account",
			"label": _("Account"),
			"fieldtype": "Link",
			"options": "Accounts",
			"width": 300
		},
		{
			"fieldname": "opening_debit",
			"label": _("Opening (Dr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "opening_credit",
			"label": _("Opening (Cr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "debit_amount",
			"label": _("Debit"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "credit_amount",
			"label": _("Credit"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "closing_debit",
			"label": _("Closing (Dr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "closing_credit",
			"label": _("Closing (Cr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		}
	]