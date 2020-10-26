// Copyright (c) 2020, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Journal Entry', {
	refresh: function (form) {
		form.add_custom_button(__("General Ledger"), function () {
			frappe.route_options = {
				"voucher_no": form.doc.name,
				"from_date": form.doc.posting_date,
				"to_date": form.doc.posting_date
			};
			frappe.set_route("query-report", "General Ledger");
		});
	}
});

frappe.ui.form.on("Journal Entry Account", {
	"debit": function (form) {
		set_debit_and_credit(form);
	},
	"credit": function (form) {
		set_debit_and_credit(form);
	}
})

var set_debit_and_credit = function (form) {
	var total_debit = 0.0, total_credit = 0.0;
	var accounts = form.doc.accounting_entries || [];
	for (var i in accounts) {
		total_debit += flt(accounts[i].debit, precision("debit", accounts[i]));
		total_credit += flt(accounts[i].credit, precision("credit", accounts[i]));
	}
	var difference = flt((total_debit - total_credit), precision("difference"))

	frappe.model.set_value(form.doctype, form.docname, "total_debit", total_debit);
	frappe.model.set_value(form.doctype, form.docname, "total_credit", total_credit);
	frappe.model.set_value(form.doctype, form.docname, "difference", difference);
}
