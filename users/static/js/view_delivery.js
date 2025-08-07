function getDeliveryDetails() {
    let orders_table = document.getElementById("ordersTable");

    orders_table.addEventListener("click", function(e) {
        const clickedRow = e.target.closest("tr");
        if(clickedRow && clickedRow.id != "replaceMe")
        {
            window.location.href = `/delivery_details/?control_number=${clickedRow.dataset.controlNumber}`;
        }
    })
}

getDeliveryDetails();