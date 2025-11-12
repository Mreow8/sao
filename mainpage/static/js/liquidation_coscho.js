function updateResults() {
    const totalAdminCost = parseFloat(document.getElementById('total_admin_cost').value) || 0;
    const totalStipend = parseFloat(document.getElementById('total_stipend').value) || 0;
    const officeSupplies = parseFloat(document.getElementById('office_supplies').value) || 0;
    const communication = parseFloat(document.getElementById('communication').value) || 0;
    const traveling = parseFloat(document.getElementById('traveling').value) || 0;
    const representation = parseFloat(document.getElementById('representation').value) || 0;
    const professionalServices = parseFloat(document.getElementById('professional_services').value) || 0;
    const legalServices = parseFloat(document.getElementById('legal_services').value) || 0;
    const otherExpenses = parseFloat(document.getElementById('other_expenses').value) || 0;

    document.querySelector('.total_admin_cost_result').innerText = totalAdminCost.toFixed(2);
    document.querySelector('.total_stipend').innerText = totalStipend.toFixed(2);

    const totalDisbursement = officeSupplies + communication + traveling + representation + professionalServices + legalServices + otherExpenses;
    document.querySelector('.total_disbursement_result').innerText = totalDisbursement.toFixed(2);

    const balance = totalStipend - totalDisbursement;
    document.getElementById('balance').value = balance.toFixed(2);
}

function validateForm() {
    const requiredInputs = document.querySelectorAll('input[required]');
    let allFilled = true;

    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            allFilled = false;
        } else {
            input.style.border = ''; // Remove the highlight if filled
        }
    });

    return allFilled;
}

function printFormDiv() {
    if (!validateForm()) {
        return;
    }

    // Hide the buttons
    document.querySelector('.print-button').style.display = 'none';
    document.querySelector('.submit-btn').style.display = 'none';

    // Print the form content
    window.print();

    document.querySelector('.print-button').style.display = 'inline-block';
    document.querySelector('.submit-btn').style.display = 'inline-block';
}

document.addEventListener('DOMContentLoaded', updateResults);
document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('.print-button').addEventListener('click', printFormDiv);
});
