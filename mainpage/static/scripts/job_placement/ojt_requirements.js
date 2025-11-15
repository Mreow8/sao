/* ojt_requirements.js */

// Helper function to get the CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
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
  // Get references to modal elements
  const form = document.querySelector(".showcontainer");
  const close = document.querySelector(".close-button");
  const xbtn = document.querySelector(".closeform");

  // This is the main handler for opening the modal
  $(".view-pdf").click(function () {
    let ojtRequirementId = $(this).val();
    let attrName = $(this).attr("name");

    let req_holder = $('input[name="req_id"]');
    let attr_holder = $('input[name="attr_name"]');

    $.ajax({
      type: "POST",
      // [FIX] Use the absolute URL path from your urls.py
      url: `/jobplacement/ojt/requirements/tracker/view/iframe/${ojtRequirementId}`,
      // [FIX] Send the token in the headers
      headers: { "X-CSRFToken": csrftoken },
      data: {
        // [FIX] Removed the broken csrfmiddlewaretoken line
        id: ojtRequirementId,
        attr_name: attrName,
      },
      success: function (response) {
        if (response.url) {
          $("#pdf-iframe").attr("src", response.url);
          req_holder.val(ojtRequirementId);
          attr_holder.val(attrName);
          form.classList.add("active");
        } else {
          alert("PDF not found!");
        }
      },
      error: function (xhr, textStatus, errorThrown) {
        console.error("Error:", errorThrown);
      },
    });
  });

  // Search bar logic
  $("#search_bar").on("input", function () {
    let query = $(this).val();
    if (query.length > 0) {
      // [FIX] Changed to absolute URL
      $.ajax({
        url: "/jobplacement/suggestions/", // Use absolute path
        data: { query: query },
        success: function (data) {
          console.log(data);
          $("#search_suggestions").html("");
          for (let i = 0; i < data.length; i++) {
            let text = `${data[i][0]} - ${data[i][1]}, ${data[i][2]}`;
            // [FIX] Stored ID in data-stud for reliable retrieval
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

  // --- Modal Close Handlers ---
  if (close && form) {
    close.addEventListener("click", () => {
      form.classList.remove("active");
      $("#pdf-iframe").attr("src", ""); // Clear iframe src
    });
  }

  if (xbtn && form) {
    xbtn.addEventListener("click", () => {
      form.classList.remove("active");
      $("#pdf-iframe").attr("src", ""); // Clear iframe src
    });
  }

  window.onclick = function (event) {
    if (form && event.target == form) {
      form.classList.remove("active");
      $("#pdf-iframe").attr("src", ""); // Clear iframe src
    }
  };
});

// [FIX] Updated function to read from data-stud
function assign_stud_id(e) {
  let element = $(e);
  const stud = element.data("stud") || element.text().split("-")[0].trim();
  $("#search_bar").val(stud);
  $("#search_suggestions").html("");
}
