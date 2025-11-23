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

  /* Search is handled by your HTML <form>, so no JS is needed.
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
        // --- SIMPLEST FIX: Reload the page to show changes ---
        location.reload();

        /* // Optional: Manual update without reload
        statusSpan.replaceWith(' <span class="accepted">Accepted</span>');
        
        // Update the link to be clickable
        showformButton.removeClass("hidden");
        showformButton.attr("href", response.print_url); // Assumes your view returns the URL
        showformButton.attr("target", "_blank");

        accept.remove();
        decline.remove();
        */
      },
      error: function (xhr, status, error) {
        alert("Error: Could not accept the request.");
      },
    });
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
        // --- SIMPLEST FIX: Reload the page to show changes ---
        location.reload();

        /*
        // Optional: Manual update without reload
        statusSpan.replaceWith(' <span class="declined">Declined</span>');
        accept.remove();
        decline.remove();
        */
      },
      error: function (xhr, status, error) {
        alert("Error: Could not decline the request.");
      },
    });
  });

  // --- DELETE BUTTON ---
  $(document).on("click", ".delete", function () {
    let OjtRequestID = $(this).closest("tr").find(".OjtRequestID").val();
    let parentRow = $(this).closest("tr");

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
          url: "{% url 'delete_ojt_assessment' %}", // CHECK YOURS URL
          data: { OjRequestID: OjtRequestID },
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
