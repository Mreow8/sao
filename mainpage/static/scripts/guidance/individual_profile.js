$(document).ready(function () {
  // --- (Remove error highlight, no changes) ---
  $(document).on("input change focus", "input, select, textarea", function () {
    $(this).removeClass("invalid-field");
    $(this)
      .closest(".field_container, .side-way, .yes_no_question_cotainer")
      .removeClass("invalid-field");
  });

  // --- (Consent modal, no changes) ---
  $("#consent_container").addClass("active");
  $("#agreeCheck").change((event) => {
    if ($("#agreeCheck").is(":checked")) {
      $("#proceedBtn").prop("disabled", false);
      $("#proceedBtn").removeClass("disabled");
    } else {
      $("#proceedBtn").prop("disabled", true);
      $("#proceedBtn").addClass("disabled");
    }
  });
  $(document).on("click", "#proceedBtn", function (event) {
    event.preventDefault();
    $("#consent_container").removeClass("active");
  });

  // --- (getCookie, no changes) ---
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      var cookies = document.cookie.split(";");
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  var csrftoken = getCookie("csrftoken");

  // --- (Search button AJAX, no changes) ---
  $("#searchButton").on("click", function (event) {
    event.preventDefault();
    var idNumber = $("#studentIDBox").val();
    $.ajax({
      url: "/search_student_info_for_individual_profile/",
      method: "POST",
      data: { id_number: idNumber },
      beforeSend: function (xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      },
      success: function (response) {
        $("#info_table").removeClass("hidden");
        $("#individualProfileForm").removeClass("hidden");
        $("#student_id_val").val(response.student_id);
        $("#info_table tr").empty();
        $("#info_table").append(
          '<tr id="info_table_head">' +
            "<th>NAME</th>" +
            "<th>COURSE</th>" +
            "<th>SEX</th>" +
            "</tr>"
        );
        let sex = "";
        if (response.sex === "M") {
          sex = "Male";
        } else {
          sex = "Female";
        }
        $("#info_table").append(
          "<tr>" +
            "<td>" +
            response.name +
            "</td>" +
            "<td>" +
            `${response.program}` +
            "</td>" +
            "<td>" +
            sex +
            "</td>" +
            "</tr>"
        );
      },
      error: function (error) {
        $("#requestForm").addClass("hidden");
        $("#info_table").removeClass("hidden");
        $("#info_table").empty();
        $("#info_table").append(
          "<tr>" + '<td colspan="4">Student ID not found.</td>' + "</tr>"
        );
      },
    });
  });

  // --- (Dynamic row and field visibility logic, no changes) ---
  $("#addanother").on("click", function (event) {
    event.preventDefault();
    let newRow = `<tr class="sibllingsrowTemplate">
                        <td><div class="field_container"><input type="text" name="name[]"></div></td>
                        <td><div class="field_container"><input type="number" name="age[]"></div></td>
                        <td><div class="field_container"><input type="text" name="placework[]"></div></td>
                        <td><button class="deleteRow OrangeButton">Delete</button></td>
                    </tr>`;
    $("#siblings").append(newRow);
  });
  $("#siblings").on("click", ".deleteRow", function (event) {
    event.preventDefault();
    var rowCount = $("#siblings tr.sibllingsrowTemplate").length;
    if (rowCount > 1) {
      $(this).closest("tr").remove();
    } else {
      $(this).closest("tr").find("input").val("");
    }
  });
  $("#organizationTable").on("click", ".deleteRow", function (event) {
    event.preventDefault();
    var rowCount = $("#organizationTable tr.orgRowTemplate").length;
    if (rowCount > 1) {
      $(this).closest("tr").remove();
    } else {
      $(this).closest("tr").find("input").val("");
      $('.inoutschool input[type="radio"]').prop("checked", false);
    }
  });

  $("#addOrganization").on("click", function (event) {
    event.preventDefault();
    let newRow = `<tr class="orgRowTemplate">
                        <td><div class="field_container"><input type="text" name="name_of_organization[]" required></div></td>
                        <td>
                            <div class="inoutschool field_container">    
                                <div id="inoutSchool" class="side-way"><div>
                                    <label for="id_elementaryType_0"><input type="radio" name="inoutSchool[]" value="True" class="side-way" required="" id="inoutSchool_0">Yes</label>
                                </div>
                                <div id="inoutSchool" class="side-way">
                                    <label for="id_elementaryType_1"><input type="radio" name="inoutSchool[]" value="False" class="side-way" required="" id="inoutSchool_1">No</label>
                                </div>
                            </div>
                        </td>
                        <td><div class="field_container"><input type="text" name="position[]"></div></td>
                        <td><div class="field_container"><input type="text" name="inclusiveyears[]"></div></td>
                        <td><div class="field_container"><button class="deleteRow OrangeButton">Delete</button></div></td>
                    </tr>`;
    $("#organizationTable").append(newRow);
  });

  // --- (All other field visibility toggles, no changes) ---
  $("#id_sourceOfIncome").change(function (event) {
    let selectedValue = $(this).val();
    if (
      selectedValue == "familyownedbusiness" ||
      selectedValue == "relatives"
    ) {
      $("#source_income_container").removeClass("hidden");
      $("#id_sourceOfIncomeSpecify").attr("required", "required");
    } else {
      $("#source_income_container").addClass("hidden");
      $("#id_sourceOfIncomeSpecify").removeAttr("required", "required");
    }
  });
  $("#id_studentType").change(function (event) {
    let selectedValue = $(this).val();
    if (selectedValue == "newStudent") {
      $("#hs_curriculum").removeClass("hidden");
      $("#id_curriculumtype").attr("required", "required");
    } else {
      $("#hs_curriculum").addClass("hidden");
      $("#id_curriculumtype").removeAttr("required", "required");
    }
  });
  $("#id_curriculumtype").change(function (event) {
    let selectedValue = $(this).val();
    if (selectedValue == "seniorhigh") {
      $("#hs_track").removeClass("hidden");
      $("#id_track").attr("required", "required");
    } else {
      $("#hs_track").addClass("hidden");
      $("#id_track").removeAttr("required", "required");
    }
  });
  $("#id_livingWith").change(function (event) {
    let selectedValue = $(this).val();
    if (selectedValue == "relative" || selectedValue == "others") {
      $("#living_specify").removeClass("hidden");
      $("#id_livingSpecify").attr("required", "required");
    } else {
      $("#living_specify").addClass("hidden");
      $("#id_livingSpecify").removeAttr("required", "required");
    }
  });
  $("#id_placeOfLiving").change(function (event) {
    let selectedValue = $(this).val();
    if (selectedValue == "others") {
      $("#place_of_living_other").removeClass("hidden");
      $("#id_placeOfLivingOthers").attr("required", "required");
    } else {
      $("#place_of_living_other").addClass("hidden");
      $("#id_placeOfLivingOthers").removeAttr("required", "required");
    }
  });
  $("#id_fatherOccupation").change(function (event) {
    let selectedValue = $(this).val();
    if (selectedValue == "others") {
      $("#father_occupation_other").removeClass("hidden");
      $("#id_fatherOtherOccupation").attr("required", "required");
    } else {
      $("#father_occupation_other").addClass("hidden");
      $("#id_fatherOtherOccupation").removeAttr("required", "required");
    }
  });
  $("#id_motherOccupation").change(function (event) {
    let selectedValue = $(this).val();
    if (selectedValue == "others") {
      $("#mother_occupation_other").removeClass("hidden");
      $("#id_motherOtherOccupation").attr("required", "required");
    } else {
      $("#mother_occupation_other").addClass("hidden");
      $("#id_motherOtherOccupation").removeAttr("required", "required");
    }
  });
  $('input[name="schoolLeaver"]').on("change", function (event) {
    if ($(this).val() === "True") {
      $("#reasonOfLeaving").removeClass("hidden");
      $("#id_schoolLeaverWhy").attr("required", "required");
    } else {
      $("#reasonOfLeaving").addClass("hidden");
      $("#id_schoolLeaverWhy").removeAttr("required", "required");
    }
  });
  $("#id_finaciallySupporting").change(function (event) {
    let selectedValue = $(this).val();
    if (selectedValue == "scholarship") {
      $("#scholarship").removeClass("hidden");
      $("#id_typeOfScholarship").attr("required", "required");
    } else {
      $("#scholarship").addClass("hidden");
      $("#id_typeOfScholarship").removeAttr("required", "required");
      $("#id_specifyScholarship").removeAttr("required", "required");
    }
  });
  $("#id_typeOfScholarship").change(function (event) {
    let selectedValue = $(this).val();
    if (selectedValue == "organizations") {
      $("#specifyScholarShip").removeClass("hidden");
      $("#id_specifyScholarship").attr("required", "required");
    } else {
      $("#specifyScholarShip").addClass("hidden");
      $("#id_specifyScholarship").removeAttr("required", "required");
    }
  });
  $('input[name="doYouPlanToWork"]').on("change", function (event) {
    if ($(this).val() === "False") {
      $("#specifyDontWork").removeClass("hidden");
      $("#id_specifyIfNo").attr("required", "required");
    } else {
      $("#specifyDontWork").addClass("hidden");
      $("#id_specifyIfNo").removeAttr("required", "required");
    }
  });
  $("#id_decisionForTheCourse").change(function (event) {
    let selectedValue = $(this).val();
    if (selectedValue != "self") {
      $("#preferedCourse").removeClass("hidden");
    } else {
      $("#preferedCourse").addClass("hidden");
    }
  });

  // --- (enforceNumericOnly, no changes) ---
  function enforceNumericOnly(event) {
    var $this = $(this);
    var value = $this.val();
    var numericValue = value.replace(/[^0-9]/g, "");
    if (value !== numericValue) {
      $this.val(numericValue);
    }
  }
  $(
    "#id_mobileNo, #id_fatherMobilePhone, #id_motherMobilePhone, #id_personInCaseofEmergencyMobileNo"
  ).on("input", enforceNumericOnly);

  // --- MODIFIED VALIDATION FUNCTION ---
  // This function now returns an object: { isValid: bool, firstInvalidField: $element }
  function validateFields(container) {
    var isValid = true;
    var radioGroups = {};
    var firstInvalidField = null; // Track the first field that fails

    container.find(".validation-summary").remove();
    container.find("input, select, textarea").each(function () {
      $(this).removeClass("invalid-field");
      $(this)
        .closest(".field_container, .side-way, .yes_no_question_cotainer")
        .removeClass("invalid-field");
    });

    container.find("input, select, textarea").each(function () {
      var $this = $(this);
      var isRequired = $this.prop("required");
      var isVisible = $this.closest(".hidden").length === 0;

      if (!isVisible) {
        return;
      }

      // 1. Handle Radio Buttons
      if ($this.attr("type") === "radio" && isRequired) {
        var name = $this.attr("name");
        if (!(name in radioGroups)) {
          radioGroups[name] =
            container.find(
              'input[type="radio"][name="' + name + '"]:visible:checked'
            ).length > 0;
          if (!radioGroups[name]) {
            isValid = false; // Set main validity to false
            if (!firstInvalidField) {
              // Store this as the first error
              firstInvalidField = $this;
            }
          }
        }
      }
      // 2. Handle Required & Empty (for non-radios)
      else if (isRequired && !$this.val() && $this.attr("type") !== "radio") {
        isValid = false;
        $this.addClass("invalid-field");
        if (!firstInvalidField) {
          firstInvalidField = $this;
        }
      }
      // 3. Handle Pattern (for phone numbers, etc.)
      else if ($this.attr("pattern") && $this.val()) {
        // --- THIS IS THE FIX ---
        // We create the regex directly from the pattern, *without* adding extra "^" and "$"
        var regex = new RegExp($this.attr("pattern"));
        // --- END OF FIX ---

        if (!regex.test($this.val())) {
          isValid = false;
          $this.addClass("invalid-field");
          if (!firstInvalidField) {
            firstInvalidField = $this;
          }
        }
      }
      // 4. Handle Email
      else if ($this.attr("type") === "email" && $this.val()) {
        var emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
        if (!emailPattern.test($this.val())) {
          isValid = false;
          $this.addClass("invalid-field");
          if (!firstInvalidField) {
            firstInvalidField = $this;
          }
        }
      }
    });

    // Process radio groups for highlighting (only highlight, validity is already set)
    Object.keys(radioGroups).forEach(function (name) {
      if (!radioGroups[name]) {
        var $radioGroupContainer = container
          .find('input[type="radio"][name="' + name + '"]')
          .closest(".field_container, .side-way, .yes_no_question_cotainer");
        $radioGroupContainer.addClass("invalid-field");
      }
    });

    return {
      isValid: isValid,
      firstInvalidField: firstInvalidField,
    };
  }
  // --- END MODIFIED VALIDATION FUNCTION ---

  // --- (MODIFIED NEXT PAGE HANDLER, no changes from last time) ---
  $(".nextpage").on("click", function () {
    let current = $(".current-page-activated");
    let next = current.next(".fill_out_container");
    let curret_page_counter = $(".current-fill-out");
    let next_page_counter = curret_page_counter.next(".page_viewer");

    current.find(".validation-summary").remove();

    var validationResult = validateFields(current);

    if (validationResult.isValid) {
      current
        .removeClass("current-page-activated")
        .addClass("current-page-deactivated");
      curret_page_counter.removeClass("current-fill-out");
      next_page_counter.addClass("current-fill-out");
      setTimeout(function () {
        current.addClass("hidden");
        next.removeClass("hidden").addClass("current-page-activated");
        current.removeClass("current-page-deactivated");
      }, 200);
    } else {
      var errorMessage = "Please correct all highlighted fields.";

      if (validationResult.firstInvalidField) {
        var $field = validationResult.firstInvalidField;
        var title = $field.attr("title");
        var label = $("label[for='" + $field.attr("id") + "']").text();

        if (title) {
          errorMessage = title;
        } else if (label) {
          errorMessage = "Please check the '" + label.trim() + "' field.";
        }
      }

      var $errorMessage = $(
        '<div class="validation-summary">' + errorMessage + "</div>"
      );
      current.prepend($errorMessage);
      $errorMessage[0].scrollIntoView({ behavior: "smooth", block: "center" });
    }
  });

  // --- (Previous Page handler, no changes) ---
  $(".prevPage").on("click", () => {
    let current = $(".current-page-activated");
    let prev = current.prev(".fill_out_container");
    let curret_page_counter = $(".current-fill-out");
    let prev_page_counter = curret_page_counter.prev(".page_viewer");
    current.removeClass("current-page-activated");
    curret_page_counter.removeClass("current-fill-out");
    prev_page_counter.addClass("current-fill-out");
    setTimeout(function () {
      current.addClass("hidden");
      prev.removeClass("hidden").addClass("current-page-activated");
      current.removeClass("current-page-deactivated");
    }, 200);
  });
});
