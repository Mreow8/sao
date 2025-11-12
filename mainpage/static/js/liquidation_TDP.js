document.getElementById("printButton").addEventListener("click", function(event) {
    if (!validateForm() && !error-message) {
        event.preventDefault();
        alert('Please fill out all required fields before printing.');
    }
    else {
        window.print();
    }
});

function validateForm() {
    const requiredFields = document.querySelectorAll('.required-field');
    let allFieldsFilled = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('input-error');
            allFieldsFilled = false;
        } else {
            field.classList.remove('input-error');
        }
    });

    return allFieldsFilled;
}


function updateReportHeader() {
    const semesterElement = document.getElementById('semester');
    const academicYearElement = document.getElementById('academic_year');
    const reportHeaderElement = document.getElementById('report-header');

    const semester = semesterElement.options[semesterElement.selectedIndex].text;
    const academicYear = academicYearElement.value;

    reportHeaderElement.textContent = `Fund Utilization Report of the TDP/Administrative Support Cost (ASC) as of ${semester} ${academicYear}`;
}

function calculate() {
    const amount1 = parseFloat(document.getElementById('amount1').value) || 0;

    const amount1_0_05 = (amount1 * 0.005).toFixed(2);
    const total1 = (amount1 + parseFloat(amount1_0_05)).toFixed(2);
    const total1_0_05 = (amount1 + parseFloat(amount1_0_05)).toFixed(2);

    document.getElementById('amount1_0_05').innerText = amount1_0_05;
    document.getElementById('total1').innerText = total1;
    document.getElementById('total1_0_05').innerText = total1_0_05;

    let totalDisbursement1 = 0;
    let totalDisbursement1_0_05 = 0;

    document.querySelectorAll('input[name^="disbursementAmount"]').forEach(input => {
        const disbursementAmount = parseFloat(input.value) || 0;
        totalDisbursement1 += disbursementAmount;
        totalDisbursement1_0_05 += disbursementAmount;
    });

    totalDisbursement1 = totalDisbursement1.toFixed(2);
    totalDisbursement1_0_05 = totalDisbursement1_0_05.toFixed(2);

    document.getElementById('totalDisbursement1').innerText = totalDisbursement1;
    document.getElementById('totalDisbursement1_0_05').innerText = totalDisbursement1_0_05;

    document.getElementById('total1_0_05_input').value = total1_0_05;
    document.getElementById('totalDisbursement1_0_05_input').value = totalDisbursement1_0_05;

    const balance = (parseFloat(amount1_0_05) - parseFloat(totalDisbursement1_0_05)).toFixed(2);
    document.getElementById('balance').value = balance;

    validateForm(); 
}

document.addEventListener('DOMContentLoaded', updateReportHeader);
document.getElementById('semester').addEventListener('change', updateReportHeader);
document.getElementById('academic_year').addEventListener('input', updateReportHeader);
let disbursementIndex = 2; 

function addRow() {
var table = document.getElementById("table").getElementsByTagName('tbody')[0];

var newRow = table.insertRow(table.rows.length - 3);  
var cell1 = newRow.insertCell(0);
var cell2 = newRow.insertCell(1);
var cell3 = newRow.insertCell(2);
var cell4 = newRow.insertCell(3);
var cell5 = newRow.insertCell(4);

cell1.innerHTML = `<input type="date" required class="required-field" name="disbursementDate${disbursementIndex}" id="disbursementDate${disbursementIndex}">`;
cell2.innerHTML = `<input type="text" required class="required-field" name="disbursementNumber${disbursementIndex}" id="disbursementNumber${disbursementIndex}" placeholder="Check Number">`;
cell3.innerHTML = `<input type="text" required class="required-field" name="disbursementParticulars${disbursementIndex}" id="disbursementParticulars${disbursementIndex}" placeholder="Particulars">`;
cell4.innerHTML = `<input type="number" required class="required-field" step="0.01" name="disbursementAmount${disbursementIndex}" id="disbursementAmount${disbursementIndex}" placeholder="Amount" oninput="calculate()">`;
cell5.innerHTML = '<button type="button" id="remove" onclick="removeRow(this)">Remove</button>';

disbursementIndex++; 
}

function removeRow(button) {
var row = button.parentNode.parentNode;
row.parentNode.removeChild(row);

calculate();
}