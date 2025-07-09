let listItemCounter = 0;

function referenceNumberAdded() {
    let addReferenceNumberButton = document.getElementById("add-reference-number-button");
    addReferenceNumberButton.addEventListener("click", function() {
        const referenceNumber = document.getElementById("reference-number-input");
        addNumberToList(referenceNumber);
    });
    
}

function addNumberToList(referenceNumber) {
    let referenceNumberList = document.getElementById("reference-number-list");
    let referenceNumbersDiv = document.getElementById("reference-numbers-div");
    
    const listItem = `<li class="list-group-item"><div class="d-flex justify-content-between">${referenceNumber.value} <button type="button" class="btn btn-danger custom-delete-button" id=${listItemCounter += 1}><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash3-fill" viewBox="0 0 16 16"> <path d="M11 1.5v1h3.5a.5.5 0 0 1 0 1h-.538l-.853 10.66A2 2 0 0 1 11.115 16h-6.23a2 2 0 0 1-1.994-1.84L2.038 3.5H1.5a.5.5 0 0 1 0-1H5v-1A1.5 1.5 0 0 1 6.5 0h3A1.5 1.5 0 0 1 11 1.5m-5 0v1h4v-1a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5M4.5 5.029l.5 8.5a.5.5 0 1 0 .998-.06l-.5-8.5a.5.5 0 1 0-.998.06m6.53-.528a.5.5 0 0 0-.528.47l-.5 8.5a.5.5 0 0 0 .998.058l.5-8.5a.5.5 0 0 0-.47-.528M8 4.5a.5.5 0 0 0-.5.5v8.5a.5.5 0 0 0 1 0V5a.5.5 0 0 0-.5-.5"/></svg></button></div></li>`;

    referenceNumberList.insertAdjacentHTML('beforeend', listItem);
    document.getElementById(listItemCounter).addEventListener("click", function(e) {
        let parentElement = this.parentElement.parentElement;
        parentElement.remove();

        if(referenceNumberList.childElementCount === 0)
        {
            referenceNumbersDiv.setAttribute("hidden", "");
            listItemCounter = 0;
        }
    });

    if(referenceNumberList.childElementCount > 0)
    {
        referenceNumbersDiv.removeAttribute("hidden");
    }

    referenceNumber.value = "";
}

function formSubmittal() {
    let submitButton = document.getElementById("submit-button");
    submitButton.addEventListener("click", function() {
        const listItemValues = JSON.stringify(extractRefNumberValues());
        const deliveryForm = document.getElementById("create-delivery-form");
        let formData = new FormData(deliveryForm);
        formData.append("jsonRefValues", listItemValues);
        htmx.ajax('POST', '/create_delivery/', {
            target : "#order-information",
            values : formData
        });
    });


    
}

function extractRefNumberValues() {
    const listItems = document.querySelectorAll("#reference-number-list li");
    let listItemValues = [];

    listItems.forEach(item => {
        listItemValues.push(item.firstElementChild.innerText);
    });

    return listItemValues;
}


setTimeout(function() {
  referenceNumberAdded();
  formSubmittal();
}, 2000);