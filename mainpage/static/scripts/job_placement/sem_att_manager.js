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

  // test selector fix
  $("#dummy").on("click", function () {
    console.log("Clicked");
  });

  $("#saveAll").on("click", function () {
    console.log("save all clicked");
    const tableData = [];

    $("#attendeeTable tbody tr").each(function () {
      const rows = {
        sem_att_id: $(this).data("item-id"),
        stud_id: $(this).find("td:eq(0)").text().trim(),
      };
      tableData.push(rows);
    });

    console.log(tableData);
    let sem_id = $("#sem_id").val();
    // use absolute path matching Django urlconf
    let _url = `/jobplacement/attendance/attend_all/${sem_id}/`;

    // send recorded data to the server using ajax
    $.ajax({
      url: _url,
      method: "POST",
      contentType: "application/json",
      headers: {
        "X-CSRFToken": csrftoken,
      },
      data: JSON.stringify(tableData),
      success: function () {
        console.log("Successfully POST items!");
        window.location.reload();
      },
      error: function (xhr, status, err) {
        console.error("Failed to POST items:", status, err, xhr.responseText);
      },
    });
  });

  $("#search_bar").on("input", function () {
    let query = $(this).val().trim();
    if (query.length > 0) {
      $.ajax({
        url: "/jobplacement/suggestions/",
        data: { query: query },
        method: "GET",
        dataType: "json",
        success: function (data) {
          console.log(data);
          $("#search_suggestions").empty();
          for (let i = 0; i < data.length; i++) {
            const stud = String(data[i][0]);
            const text = `${stud} - ${data[i][1]}, ${data[i][2]}`;
            // store id in data-stud for reliable retrieval
            $("#search_suggestions").append(
              `<li data-stud="${stud}" onclick="getstudent(this)">${text}</li>`
            );
          }
        },
        error: function (xhr) {
          console.error("suggestions error", xhr.status, xhr.responseText);
        },
      });
    } else {
      $("#search_suggestions").empty();
    }
  });
});

function getstudent(e) {
  let element = $(e);
  const stud = element.data("stud") || element.text().split("-")[0].trim();
  $("#search_bar").val(stud);
  $("#search_suggestions").empty();
}
// ...existing code...
