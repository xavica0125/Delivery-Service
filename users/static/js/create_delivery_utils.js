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
    if(referenceNumberList.childElementCount === 0)
    {
        let referenceNumbersDiv = document.getElementById("reference-numbers-div");
        referenceNumbersDiv.setAttribute("class", "mb-3");
        referenceNumbersDiv.removeAttribute("hidden");

    }
    referenceNumberList.innerHTML += `<li class="list-group-item">${referenceNumber.value}</li>`;
    
    referenceNumber.value = "";
}


setTimeout(function() {
  referenceNumberAdded();
}, 5000);