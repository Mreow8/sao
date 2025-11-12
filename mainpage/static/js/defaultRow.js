document.addEventListener("DOMContentLoaded", function() {
    addDefaultRows(2, 'fundsTable', 'date', 'checkNumber', 'particulars', 'amount');
    addDefaultRows(2, 'disbursementsTable', 'disbursementDate', 'disbursementNumber', 'disbursementParticulars');
});

function addDefaultRows(numRows, tableId, dateName, checkNumberName, particularsName, amountName) {
    const table = document.getElementById(tableId);
    
    for (let i = 0; i < numRows; i++) {
        const row = table.insertRow(-1);

        const cell1 = row.insertCell(0);
        const dateInput = document.createElement("input");
        dateInput.type = "date";
        dateInput.name = dateName + (i + 1);
        cell1.appendChild(dateInput);

        const cell2 = row.insertCell(1);
        const checkNumberInput = document.createElement("input");
        checkNumberInput.type = "text";
        checkNumberInput.name = checkNumberName + (i + 1);
        cell2.appendChild(checkNumberInput);

        const cell3 = row.insertCell(2);
        const particularsInput = document.createElement("input");
        particularsInput.type = "text";
        particularsInput.name = particularsName + (i + 1);
        cell3.appendChild(particularsInput);

        if (amountName) {
            const cell4 = row.insertCell(3);
            const amountInput = document.createElement("input");
            amountInput.type = "number";
            amountInput.name = amountName + (i + 1);
            cell4.appendChild(amountInput);

            const cell5 = row.insertCell(4);
            const removeButton = document.createElement("button");
            removeButton.type = "button";
            removeButton.textContent = "Remove";
            removeButton.onclick = function() { removeRow(this); };
            cell5.appendChild(removeButton);
        } else {
            const cell4 = row.insertCell(3);
            const removeButton = document.createElement("button");
            removeButton.type = "button";
            removeButton.textContent = "Remove";
            removeButton.onclick = function() { removeRow(this); };
            cell4.appendChild(removeButton);
        }
    }
}

function addRow() {
    addDefaultRows(1, 'fundsTable', 'date', 'checkNumber', 'particulars', 'amount');
}

function addDisbursement() {
    addDefaultRows(1, 'disbursementsTable', 'disbursementDate', 'disbursementNumber', 'disbursementParticulars');
}

function removeRow(button) {
    const row = button.parentNode.parentNode;
    row.parentNode.removeChild(row);
}
