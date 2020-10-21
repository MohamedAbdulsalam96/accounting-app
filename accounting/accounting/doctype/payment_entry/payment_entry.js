// Copyright (c) 2020, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Entry', {
	refresh: function (form) {
		set_party_type(form, "Customer")
		form.add_custom_button(__("General Ledger"), function () {
			frappe.route_options = {
				"voucher_no": form.doc.name,
				"from_date": form.doc.posting_date,
				"to_date": form.doc.posting_date
			};
			frappe.set_route("query-report", "General Ledger");
		});
	},
	payment_type: function (form) {
		if (form.doc.payment_type == "Receive") {
			set_party_type(form, "Customer")
		}
		else {
			set_party_type(form, "Supplier")
		}
	}
});

var set_party_type = function (form, party_type) {
	form.set_query("party", function () {
		return {
			filters: {
				"party_type": party_type
			}
		}
	})
}
