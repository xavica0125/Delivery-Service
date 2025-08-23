function restoreTableState() {
    const searchBar = document.getElementById("search-bar");

    searchBar.addEventListener('focus', () => { // Caches ordersTable state before a search query is made 
        if(searchBar.value.length === 0)
        {
            localStorage.clear();

            const deliveryTableHTML = document.getElementById("ordersTable").outerHTML;

            localStorage.setItem("ordersTable", deliveryTableHTML);
        }



    });

    searchBar.addEventListener("htmx:beforeRequest", function(e) { // Checks if search bar is empty before sending HTMX request and then retrieves cached ordersTable to repopulate DOM if search bar is indeed empty

        if(searchBar.value.length === 0 && localStorage.getItem("ordersTable") != null) {
            e.preventDefault();

            const ordersTable = document.getElementById("ordersTable");

            ordersTable.innerHTML = localStorage.getItem("ordersTable");
        }
    
    });
}

restoreTableState(); 