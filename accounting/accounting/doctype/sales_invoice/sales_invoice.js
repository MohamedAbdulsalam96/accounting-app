// Copyright (c) 2020, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice', {
	refresh: function (form) {
		form.add_custom_button(__("General Ledger"), function () {
			//perform desired action such as routing to new form or fetching etc.
			frappe.set_route("query-report", "General Ledger");
		});
	},
	setup: function(form){
		form.set_query("income_account", function(){
			return {
				filters: {
					"account_type": "Income",
					"is_group": 0
				}
			}
		})
		form.set_query("debit_to", function(){
			return {
				filters: {
					"parent_accounts": "Account Receivable",
					"is_group": 0
				}
			}
		})
	}
});

frappe.ui.form.on('Sales Invoice Item', {
	item: function (form, cdt, cdn) {
		var document = frappe.get_doc(cdt, cdn);
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Item",
				name: document.item
			},
			callback: function (data) {
				frappe.model.set_value(cdt, cdn, "rate", data.message.standard_rate);
				frappe.model.set_value(cdt, cdn, "qty", 1);
				frappe.model.set_value(cdt, cdn, "amount", data.message.standard_rate * 1);
				set_total_quantity_and_amount(form);
			}
		})
	},
	qty: function (form, cdt, cdn) {
		var document = frappe.get_doc(cdt, cdn);
		frappe.model.set_value(cdt, cdn, "amount", document.rate * document.qty);
		set_total_quantity_and_amount(form)	
	}
})

var set_total_quantity_and_amount = function (form) {
	var total_quantity = 0.0, total_amount = 0.0;
	var items = form.doc.items || [];
	for (var i in items) {
		total_quantity += flt(items[i].qty, precision("qty", items[i]));
		total_amount += flt(items[i].amount, precision("amount", items[i]));
	}
	frappe.model.set_value(form.doctype, form.docname, "total_qty", total_quantity);
	frappe.model.set_value(form.doctype, form.docname, "total_amount", total_amount);
}
