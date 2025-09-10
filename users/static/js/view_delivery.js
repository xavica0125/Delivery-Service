function getDeliveryDetails() {
    let orders_table = document.getElementById("ordersTable");

    orders_table.addEventListener("click", function(e) {
        const clickedRow = e.target.closest("tr");
        if(clickedRow && clickedRow.id != "replaceMe" && clickedRow.id != "column-headers")
        {
            htmx.ajax('GET', '/delivery_details/', {
                "target" : "#ordersTable",
                "values" : {"control_number" : `${clickedRow.dataset.controlNumber}`}, 
            });
        }
    })
}

getDeliveryDetails();