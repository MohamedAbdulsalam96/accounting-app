frappe.ready(() => {
    frappe.call({
        method: "accounting.www.all-products.index.get_website_products",
        callback: function (data) {
            data.message.forEach(item => {
                $(".product-list").prepend(display_product_list_items(item))
            })
        }
    })
});

var display_product_list_items = function (item) {
    return (`<li class="m-5">
    	        <a class="text-decoration-none text-reset" href=${item.route}>
    	            <div class="mb-5 row">
                    <div class="col-md-4">
                        <div class="border text-center rounded mb-5">
                            <img class="item-slideshow-image mt-2s" src=${item.image} style="max-height: 150px" alt=${item.item_name}>
                        </div>
                    </div>
                    <div class="col-md-8">
                        <h1>${item.item_name}</h1>
                        <p class="text-truncate">
                            ${item.item_description}
                        </p>
                        <h3>$ ${item.standard_rate}/${item.uom}</h3>
                    </div>
                </div>
    	        </a>
            </li>`)
}