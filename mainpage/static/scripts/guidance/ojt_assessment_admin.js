$(document).ready(function () {
  // Get CSRF token from cookies
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      var cookies = document.cookie.split(";");
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  var csrftoken = getCookie("csrftoken");

  /* !! REMOVED !!
  The entire $("#searchButton").on("click", ...) function was removed.
  Your HTML <form method="GET"> now handles searching, which
  allows it to work with pagination and sorting.
  */

  // --- ACCEPT BUTTON ---
  $(document).on("click", ".accept", function () {
    let OjtRequestID = $(this).closest("tr").find(".OjtRequestID").val();
    let statusSpan = $(this).closest("tr").find(".pending");
    let accept = $(this).closest("tr").find(".accept");
    let decline = $(this).closest("tr").find(".decline");
    let showformButton = $(this).closest("tr").find(".showformButton");

    $.post({
      url: "/main/update_ojt_assessment/", // CHECK YOUR URL
      data: { OjtRequestID: OjtRequestID, type: "accept" },
      headers: { "X-CSRFToken": csrftoken },
      success: function (response) {
        // location.reload(); // Use this for simplicity
        statusSpan.replaceWith(' <span class="accepted">Accepted</span>');
        showformButton.removeClass("hidden");
        accept.remove();
        decline.remove();
      },
      error: function (xhr, status, error) {
        alert("Error: Could not accept the request.");
      },
    });
  });

  // --- SHOW FORM MODAL ---
  // NOTE: Your HTML template is missing the modal HTML ('.showform_container')
  // This code expects a modal to exist on the page.
  $(document).on("click", ".showformButton", function (e) {
    // If it's a link, prevent it from navigating
    e.preventDefault();

    // Check if the button is hidden (i.e., not accepted)
    if ($(this).hasClass("hidden")) {
      return;
    }

    let OjtRequestID = $(this).closest("tr").find(".OjtRequestID").val();

    // This code will fail until you add the modal HTML
    $(".showform_container").addClass("active");

    $.post({
      url: "/main/get_ojt_assessment_data/", // CHECK YOUR URL
      data: { OjtRequestID: OjtRequestID },
      headers: { "X-CSRFToken": csrftoken },
      success: function (response) {
        $("#student-name").text(response.name);
        $("#school-year").text(response.schoolyear);
        $("#student-course").text(`${response.program}.`);
        $("#issue-date").text(response.date_accepted);
        $(".showform_container").addClass("active");
      },
      error: function (xhr, status, error) {
        alert("Error: Could not load form data.");
      },
    });
  });

  // --- CLOSE MODAL ---
  $(document).on("click", ".closeform", function () {
    $(".showform_container").removeClass("active");
  });

  // --- DECLINE BUTTON ---
  $(document).on("click", ".decline", function () {
    let OjtRequestID = $(this).closest("tr").find(".OjtRequestID").val();
    let statusSpan = $(this).closest("tr").find(".pending");
    let accept = $(this).closest("tr").find(".accept");
    let decline = $(this).closest("tr").find(".decline");

    $.post({
      url: "/main/update_ojt_assessment/", // CHECK YOUR URL
      data: { OjtRequestID: OjtRequestID, type: "decline" },
      headers: { "X-CSRFToken": csrftoken },
      success: function (response) {
        // location.reload(); // Use this for simplicity
        statusSpan.replaceWith(' <span class="declined">Declined</span>');
        accept.remove();
        decline.remove();
      },
      error: function (xhr, status, error) {
        alert("Error: Could not decline the request.");
      },
    });
  });

  // --- SAVE PDF BUTTON ---
  $(document).on("click", ".saveButton", function () {
    const elements = document.getElementById("paper");
    const student_name = $("#student-name").text();
    const options = {
      margin: [0, 0, 0, 0],
      filename: `${student_name}_certificate.pdf`,
      image: { type: "jpeg", quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: "mm", format: [216, 279], orientation: "portrait" },
    };

    html2pdf().from(elements).set(options).save();
  });

  // --- [FIXED] PRINT BUTTON ---
  // The code was floating, now it's inside a click handler
  $(document).on("click", ".printButton", function () {
    const elements = document.getElementById("paper");
    const student_name = $("#student-name").text();
    const options = {
      margin: [0, 0, 0, 0],
      filename: `${student_name}_certificate.pdf`,
      image: { type: "jpeg", quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: "mm", format: [216, 279], orientation: "portrait" },
    };

    // Use .toPdf().print() to open the print dialog
    html2pdf().from(elements).set(options).toPdf().print();
  });

  // --- DELETE BUTTON ---
  $(document).on("click", ".delete", function () {
    let OjtRequestID = $(this).closest("tr").find(".OjtRequestID").val();
    let parentRow = $(this).closest("tr");

    // [RECOMMENDATION] Use SweetAlert for confirmation
    Swal.fire({
      title: "Are you sure?",
      text: "This action cannot be undone.",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#d33",
      cancelButtonColor: "#3085d6",
      confirmButtonText: "Yes, delete it!",
    }).then((result) => {
      if (result.isConfirmed) {
        $.post({
          url: "/main/delete_ojt_assessment/", // CHECK YOUR URL
          data: { OjtRequestID: OjtRequestID },
          headers: { "X-CSRFToken": csrftoken },
          success: function (response) {
            parentRow.remove();
            Swal.fire("Deleted!", "The request has been deleted.", "success");
          },
          error: function (xhr, status, error) {
            Swal.fire("Error!", "Could not delete the request.", "error");
          },
        });
      }
    });
  });
});
