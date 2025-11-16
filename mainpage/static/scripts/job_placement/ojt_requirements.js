/* ojt_requirements.js - IFRAME VERSION (Corrected) */

// Helper function to get the CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie("csrftoken");

$(document).ready(function () {
  // --- MODAL LOGIC ---
  const popup = document.querySelector(".showcontainer");
  const iframe = document.getElementById("pdf-iframe");
  const closeButtons = document.querySelectorAll(".closeform, .close-button");

  // The hidden inputs in the Accept/Decline forms
  const hiddenReqIdInputs = document.querySelectorAll('input[name="req_id"]');
  const hiddenAttrNameInputs = document.querySelectorAll(
    'input[name="attr_name"]'
  );

  // This is the main handler for opening the modal
  $(".view-pdf").click(function () {
    // 1. Get all data from the button
    const button = $(this);
    const reqId = button.val();
    const attrName = button.attr("name");
    const viewUrl = button.data("url"); // This is the 'view_pdf' URL

    if (!viewUrl) {
      alert(
        "Error: Missing data-url attribute on the button. Cannot load file."
      );
      return;
    }

    // Set iframe to empty while loading
    if (iframe) {
      iframe.src = "";
    }

    // 2. Call the 'view_pdf' function via AJAX
    $.ajax({
      type: "POST",
      url: viewUrl, // The URL from data-url
      headers: { "X-CSRFToken": csrftoken },
      data: {
        attr_name: attrName,
      },
      success: function (response) {
        // 3. On success, 'response.url' is the 'stream_ojt_file' URL
        if (response.url && iframe) {
          // 4. Set the iframe source to the streaming URL
          iframe.src = response.url;

          // 5. Populate the hidden fields in BOTH forms
          hiddenReqIdInputs.forEach((input) => (input.value = reqId));
          hiddenAttrNameInputs.forEach((input) => (input.value = attrName));

          // 6. Show the modal
          if (popup) {
            // ✅ THIS IS THE FIX
            popup.classList.add("active");
          }
        } else {
          alert(response.error || "Could not get file URL.");
        }
      },
      error: function (xhr, textStatus, errorThrown) {
        console.error("AJAX Error:", errorThrown, xhr.responseText);
        alert("AJAX Error: Could not contact server. Check console.");
      },
    });
  });

  // --- Modal Close Handlers ---
  closeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      if (popup) {
        // ✅ THIS IS THE FIX
        popup.classList.remove("active");
        if (iframe) {
          iframe.src = ""; // Clear iframe src when closing
        }
      }
    });
  });

  // --- SEARCH BAR LOGIC ---
  $("#search_bar").on("input", function () {
    let query = $(this).val();
    if (query.length > 0) {
      $.ajax({
        url: "/jobplacement/suggestions/", // Use absolute path
        data: { query: query },
        success: function (data) {
          $("#search_suggestions").html("");
          for (let i = 0; i < data.length; i++) {
            let text = `${data[i][0]} - ${data[i][1]}, ${data[i][2]}`;
            $("#search_suggestions").append(
              '<li data-stud="' +
                data[i][0] +
                '" onclick="assign_stud_id(this)">' +
                text +
                "</li>"
            );
          }
        },
      });
    } else {
      $("#search_suggestions").html("");
    }
  });
}); // End of document.ready

function assign_stud_id(e) {
  let element = $(e);
  const stud = element.data("stud") || element.text().split("-")[0].trim();
  $("#search_bar").val(stud);
  $("#search_suggestions").html("");
}
