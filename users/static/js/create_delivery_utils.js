function referenceNumberAdded() {
    let addReferenceNumberButton = document.getElementById("add-reference-number-button");
    addReferenceNumberButton.addEventListener("click", function() {
        let referenceNumber = document.getElementById("id_customer_order_reference");
        console.log(referenceNumber);
        addNumberToList(referenceNumber);
    });
    
}

function addNumberToList(referenceNumber) {
    let referenceNumberList = document.getElementById("reference-number-list");
    const listItem = document.createElement("li");
    const listItemContent = document.createTextNode(referenceNumber.value);
    listItem.appendChild(listItemContent);

    referenceNumberList.appendChild(listItem);
    
    referenceNumber.value = "";
}


setTimeout(function() {
  referenceNumberAdded();
}, 5000);