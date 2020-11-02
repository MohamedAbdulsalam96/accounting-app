frappe.provide("accounting.cart");
frappe.ready(() => {
    $('.add-to-cart').click((e) => {
        if (frappe.session.user === "Guest") {
            window.location.href = "/login";
        }
        else {
            $(e.currentTarget).prop('disabled', true);
            var item_name = $(e.currentTarget).data('item-name');
            add_to_cart(item_name);
        }
    })
})

var add_to_cart = function (item_name) {
    frappe.call({
        method: "accounting.accounting.doctype.sales_invoice.sales_invoice.add_to_cart",
        args: {
            item_name: item_name,
            save: true,
            user: frappe.session.user
        },
        callback: (data) => {
            $('.add-to-cart').prop('disabled', false)
            frappe.msgprint({
                title: "Cart Confirmation",
                message: `Item added to Cart!!! <a href="/cart">View Cart and Checkout</a>`
            })
        }
    })
}