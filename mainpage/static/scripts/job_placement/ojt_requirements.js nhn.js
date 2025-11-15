// ...existing code...
$(document).ready(function () {
  // helper to read csrftoken from cookie (Django)
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      document.cookie.split(";").forEach(function (cookie) {
        const c = cookie.trim();
        if (c.startsWith(name + "="))
          cookieValue = decodeURIComponent(c.substring(name.length + 1));
      });
    }
    return cookieValue;
  }
  const csrftoken = getCookie("csrftoken");

  // testing purposes
  const open = document.querySelector(".view-pdf");
  const close = document.querySelector(".close-button");
  const form = document.querySelector(".showcontainer");
  const xbtn = document.querySelector(".closeform");

  $(".view-pdf").click(function () {
    let ojtRequirementId = $(this).val();
    let attrName = $(this).attr("name");

    let req_holder = $('input[name="req_id"]');
    let attr_holder = $('input[name="attr_name"]');

    $.ajax({
      type: "POST",
      // use absolute path (adjust if your route differs)
      url: `/jobplacement/ojt/requirements/tracker/view/iframe/${ojtRequirementId}`,
      headers: { "X-CSRFToken": csrftoken },
      data: {
        id: ojtRequirementId,
        attr_name: attrName,
      },
      success: function (response) {
        if (response.url) {
          // Assuming you have an iframe with id="pdfViewer"
          $("#pdf-iframe").attr("src", response.url);
          req_holder.val(ojtRequirementId);
          attr_holder.val(attrName);
          if (form) form.classList.add("active");
        } else {
          alert("PDF not found!");
        }
      },
      error: function (xhr, textStatus, errorThrown) {
        console.error("Error:", errorThrown);
      },
    });
  });

  $("#search_bar").on("input", function () {
    let query = $(this).val();
    if (query.length > 0) {
      $.ajax({
        // absolute suggestions endpoint
        url: "/jobplacement/suggestions/",
        data: { query: query },
        success: function (data) {
          console.log(data);
          $("#search_suggestions").html("");
          for (let i = 0; i < data.length; i++) {
            text = `${data[i][0]} - ${data[i][1]}, ${data[i][2]}`;
            // store id in data attribute for reliable retrieval
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

  // attach handlers only if elements exist
  if (open && form) {
    open.addEventListener("click", () => {
      form.classList.add("active");
    });
  }
  if (close && form) {
    close.addEventListener("click", () => {
      form.classList.remove("active");
    });
  }
  if (xbtn && form) {
    xbtn.addEventListener("click", () => {
      form.classList.remove("active");
    });
  }
  window.onclick = function (event) {
    if (form && event.target == form) {
      form.classList.remove("active");
    }
  };
});

function assign_stud_id(e) {
  let element = $(e);
  // read stored data-stud attribute
  const stud =
    element.data("stud") ||
    element.attr("value") ||
    element.text().split("-")[0].trim();
  $("#search_bar").val(stud);
  $("#search_suggestions").html("");
}
// ...existing code...
