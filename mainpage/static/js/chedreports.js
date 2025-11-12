document.addEventListener('DOMContentLoaded', function() {
    const dropdown = document.querySelector('.dropbtn');
    const dropdownContent = document.querySelector('.dropdown-content');

    dropdown.addEventListener('click', function() {
        dropdownContent.classList.toggle('show');
    });

    window.addEventListener('click', function(event) {
        if (!event.target.matches('.dropbtn')) {
            if (dropdownContent.classList.contains('show')) {
                dropdownContent.classList.remove('show');
            }
        }
    });
});
