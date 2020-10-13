// Copyright (c) 2020, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Entry', {
	refresh: function (form) {
		form.add_custom_button(__("General Ledger"), function () {
			//perform desired action such as routing to new form or fetching etc.
			frappe.set_route("query-report", "General Ledger");
		});
	} 
});
