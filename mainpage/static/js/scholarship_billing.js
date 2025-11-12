
document.addEventListener('DOMContentLoaded', function() {
     const dropdowns = document.querySelectorAll('.dropdown');

     dropdowns.forEach(dropdown => {
         const button = dropdown.querySelector('.dropbtn');
         const content = dropdown.querySelector('.dropdown-content');

         button.addEventListener('click', function() {
             content.style.display = content.style.display === 'block' ? 'none' : 'block';
         });
     });

     const scholarshipTypeOptions = document.querySelectorAll('.scholarship-type-option');
     scholarshipTypeOptions.forEach(option => {
         option.addEventListener('click', function(e) {
             e.preventDefault();
             const scholarshipType = this.dataset.scholarshipType;
             console.log(`Selected Scholarship Type: ${scholarshipType}`);
             document.getElementById('scholarship-type-input').value = scholarshipType;
             document.getElementById('filter-form').submit();
         });
     });

     const semesterOptions = document.querySelectorAll('.semester-option');
     semesterOptions.forEach(option => {
         option.addEventListener('click', function(e) {
             e.preventDefault();
             const semester = this.dataset.semester;
             console.log(`Selected Semester: ${semester}`);
             document.getElementById('semester-input').value = semester;
             document.getElementById('filter-form').submit();
         });
     });

     $('#scholarship_year').change(function() {
         $('#scholarship-year-input').val($(this).val());
         $('#filter-form').submit();
     });
 });