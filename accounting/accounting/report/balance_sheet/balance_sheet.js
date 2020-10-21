// Copyright (c) 2016, Frappe and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.require("/assets/accounting/js/financial_statements.js", function () {
	frappe.query_reports["Balance Sheet"] = {
		"filters": [
			{
				"fieldname": "fiscal_year",
				"label": __("Fiscal Year"),
				"fieldtype": "Link",
				"options": "Fiscal Year",
				"reqd": 1,
				"width": "60px",
				"default": frappe.db.get_list("Fiscal Year").then((data) => {
					return data[0].name;
				})
			}
		],
		"formatter": accounting.financial_statements.formatter
	};
})
