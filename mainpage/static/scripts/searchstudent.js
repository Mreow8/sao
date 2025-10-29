document.addEventListener("DOMContentLoaded", function () {
  const studentInput = document.getElementById("studentIDBox");
  const studentDetails = document.getElementById("student_details");
  // We can likely disable or change the functionality of the existing #searchButton
  // as the AJAX will handle the lookup on input/change.
  const searchButton = document.getElementById("searchButton");
  searchButton.style.display = "none"; // Optional: Hide the old search button

  function fetchStudentDetails(studentID) {
    if (!studentID) {
      studentDetails.classList.add("hidden");
      return;
    }
    // ASSUMPTION: You have a Django URL mapped to handle this AJAX request
    fetch(`/discipline/get-student/${studentID}/`)
      .then((response) => response.json())
      .then((data) => {
        if (data.found) {
          document.getElementById("student_name").textContent = data.name;
          document.getElementById("student_course").textContent = data.course;
          document.getElementById("student_year").textContent = data.year;
          studentDetails.classList.remove("hidden");

          // Additionally, show the main intake form after successful lookup
          document.getElementById("info_table").classList.remove("hidden");
          document.getElementById("intakeForm").classList.remove("hidden");

          // Set the hidden input for the POST request
          document.getElementById("individualId").value = data.profile_id;
        } else {
          document.getElementById("student_name").textContent = "";
          document.getElementById("student_course").textContent = "";
          document.getElementById("student_year").textContent = "";
          studentDetails.classList.add("hidden");

          // Hide the form if student not found
          document.getElementById("info_table").classList.add("hidden");
          document.getElementById("intakeForm").classList.add("hidden");
          alert("Student not found.");
        }
      })
      .catch((err) => {
        console.error("Error fetching student details:", err);
        studentDetails.classList.add("hidden");
        document.getElementById("info_table").classList.add("hidden");
        document.getElementById("intakeForm").classList.add("hidden");
      });
  }

  studentInput.addEventListener("input", function () {
    fetchStudentDetails(this.value.trim());
  });
  studentInput.addEventListener("change", function () {
    fetchStudentDetails(this.value.trim());
  });
});
