frappe.ready(() => {
    if (frappe.session.user == "Guest") {
        window.location.href = "/login";
    }
    frappe.call({
        method: "accounting.accounting.doctype.sales_invoice.sales_invoice.display_user_cart",
        args: {
            user: frappe.session.user,
            get_full_details: true
        },
        callback: (data) => {
            si = data.message
            if (!si) {
                display_empty_cart_msg()
                return
            }
            si.items.forEach(item => {
                $(".cart-products-list").append(display_item_in_cart(item))
            });
            update_total_quantity_and_amount(si)
            place_order(si.name)
            modify_qty(si.name)
        }
    })
});

var update_total_quantity_and_amount = function (si) {
    $(".total_qty").text(`Total Quantity : ${si.total_qty}`)
    $(".total_amount").text(`Total Amount : ${si.total_amount}`)
}

var place_order = function (si) {
    $(".place-order").click(e => {
        $(e.currentTarget).prop('disabled', true);
        frappe.call({
            method: "accounting.accounting.doctype.sales_invoice.sales_invoice.update_sales_invoice",
            args: {
                item_name: null,
                qty: 0,
                si: si,
                submit: true
            },
            callback: (data) => {
                $(".place-order").addClass("d-none");
                display_sales_invoice_info(si)
            }
        })
    })
}

var modify_qty = function (si) {
    $(".qty-btn").click(e => {
        btn = $(e.currentTarget)
        input = btn.closest('.number-spinner').find('input')
        oldVal = input.val()
        newVal = 0
        if (btn.attr("data-dir") == "up") {
            newVal = parseInt(oldVal) + 1
        }
        else {
            newVal = parseInt(oldVal) - 1
        }
        input.val(newVal)
        set_quantity_in_si(input.attr("data-item-name"), newVal, si)
    })
}

var set_quantity_in_si = function (item_name, qty, si) {
    frappe.call({
        method: "accounting.accounting.doctype.sales_invoice.sales_invoice.update_sales_invoice",
        args: {
            item_name: item_name,
            qty: qty,
            si: si,
            save: true
        },
        callback: (data) => {
            update_total_quantity_and_amount(data.message)
        }
    })
}

var display_item_in_cart = function (item) {
    return (`<li class="list-group-item">
		        <div class="d-flex flex-row justify-content-between">
                    <h5>${item.item} </h5>
                    <div class="d-flex flex-row align-items-center border rounded number-spinner">
                        <button class="qty-btn btn" data-dir="down">-</button>
                        <input class="cart-qty text-center border-0" style="max-width:60px"
                            type="number" value="${item.qty}" data-item-name="${item.item}">
                        <button class="qty-btn btn" data-dir="up">+</button>
                    </div>
                </div>
            </li>`)
}

var display_sales_invoice_info = function (si) {
    $(".cart-products").append(`<div class="border m-5 p-5">
                                    <h3>Sales Invoice : ${si}</h3> 
                                    <div>Estimate Delivery in 3-5 days.</div>
                                    <h3>Thank You for shopping with us :)</h3>
                                </div>`)
}

var display_empty_cart_msg = function () {
    $(".no-products-msg").removeClass("d-none");
    $(".cart-products").removeClass("d-flex").addClass("d-none");
}