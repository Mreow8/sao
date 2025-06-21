$('.btn').click(function(){
    $(this).toggleClass("click");
    $('.side-nav').toggleClass("show");
    $('.orange-bar').toggleClass("show");
});

$('.closebtn').click(function(){
    $(this).toggleClass("click");
    $('.side-nav').toggleClass("show");
    $('.orange-bar').toggleClass("show");
});

$('.studentlife-btn').click(function() {
    $('.side-nav ul .studentlife').toggleClass("show"); 
    $('.side-nav ul .first').toggleClass("rotate");
});
$('.scholar-btn').click(function() {
    $('.side-nav ul .scholar-show').toggleClass("show2"); 
    $('.side-nav ul .second').toggleClass("rotate");
});
$('.jobplace-btn').click(function() {
    $('.side-nav ul .jobplace-show').toggleClass("show3"); 
    $('.side-nav ul .third').toggleClass("rotate");
});
$('.student_disc-btn').click(function() {
    $('.side-nav ul .student_disc-show').toggleClass("show4"); 
    $('.side-nav ul .fourth').toggleClass("rotate");
});
$('.guide-btn').click(function() {
    $('.side-nav ul .guide-show').toggleClass("show5"); 
    $('.side-nav ul .fifth').toggleClass("rotate");
});
$('.alumni-btn').click(function() {
    $('.side-nav ul .alumni-show').toggleClass("show6"); 
    $('.side-nav ul .sixth').toggleClass("rotate");
});
$('.community-btn').click(function() {
    $('.side-nav ul .community-show').toggleClass("show7"); 
    $('.side-nav ul .seventh').toggleClass("rotate");
});
$('.student_org-btn').click(function() {
    $('.side-nav ul .student_org-show').toggleClass("show8"); 
    $('.side-nav ul .eight').toggleClass("rotate");
});
$('.medical-btn').click(function() {
    $('.side-nav ul .medical-show').toggleClass("show9"); 
    $('.side-nav ul .ninth').toggleClass("rotate");
});

document.addEventListener('DOMContentLoaded', function() {
    // Convert username to sentence case
    function toSentenceCase(str) {
        return str.toLowerCase().replace(/(^\w{1})|(\s+\w{1})/g, letter => letter.toUpperCase());
    }

    var usernameElement = document.getElementById('username');
    if (usernameElement) {
        usernameElement.textContent = toSentenceCase(usernameElement.textContent);
    }

    // Toggle dropdown on click
    var dropdownLink = document.querySelector('.dropdown-link');
    var dropdown = dropdownLink.closest('.dropdown');
    dropdownLink.addEventListener('click', function(event) {
        event.preventDefault();
        dropdown.classList.toggle('show');
    });

    // Close the dropdown if the user clicks outside of it
    window.onclick = function(event) {
        if (!event.target.matches('.dropdown-link')) {
            var dropdowns = document.getElementsByClassName("dropdown");
            for (var i = 0; i < dropdowns.length; i++) {
                var openDropdown = dropdowns[i];
                if (openDropdown.classList.contains('show')) {
                    openDropdown.classList.remove('show');
                }
            }
        }
    }
});



