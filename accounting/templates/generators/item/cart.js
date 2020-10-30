frappe.provide("accounting.cart");
frappe.ready(() => {
    $('.add-to-cart').click((e) => {
        $(e.currentTarget).prop('disabled', true);
        var qty = $('.cart-qty').val();
        var item_name = $(e.currentTarget).data('item-name');
        if (qty <= 0) {
            frappe.msgprint({
                title: __("Validation Error"),
                message: __("Please add one or more quantity for product.")
            })
            $('.add-to-cart').prop('disabled', false)
            return;
        }
        var si = localStorage.getItem("Sales Invoice")
        if (si && si != "undefined") {
            si = JSON.parse(si)
            if (si.docstatus == 1) {
                sales_invoice_call("make_sales_invoice", item_name, qty)
                return
            }
            sales_invoice_call("update_sales_invoice", item_name, qty, si.name)
            return;
        }
        sales_invoice_call("make_sales_invoice", item_name, qty)
    })
})

var sales_invoice_call = function (method, item_name, qty, si) {
    frappe.call({
        method: "accounting.accounting.doctype.sales_invoice.sales_invoice." + method,
        args: {
            item_name: item_name,
            qty: qty > 0 ? qty : 0,
            debit_to: "Debtors",
            income_account: "Creditors",
            save: true,
            si: si
        },
        callback: (data) => {
            $('.add-to-cart').prop('disabled', false)
            localStorage.setItem("Sales Invoice", JSON.stringify(data.message))
            frappe.msgprint({
                title: "Cart Confirmation",
                message: `Item added to Cart!!! <a href="/cart">View Cart and Checkout</a>`
            })
            $('.cart-qty').val(null)
        }
    })
}