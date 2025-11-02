$("document").ready(function () {
  // This part is correct and handles the dynamic award dropdowns.
  $("#program_select").change(function () {
    var awards = {
      AGRICULTURE: [
        "Leadership Award",
        "Social Responsibility and Civic Engangement Award",
        "Others",
      ],
      BIT: ["Best OJT Award", "Researcher of the Year", "Others"],
      BES: ["Leadership Award", "Others"],
      BSHM: ["Leadership Award", "Others"],
      BSIE: [
        "Leadership Award",
        "Outstanding Athlete Award",
        "Researcher of the Year",
        "Others",
      ],
      BSIT: [
        "Best Capstone",
        "Excellence Award",
        "Leadership Award",
        "Programmer of the Year",
        "Others",
      ],
      CAS: [
        "Academic Leadership Award",
        "BAEL Pride Award",
        "Leadership Award",
        "Loyalty Award",
        "Outstanding Athlete Award",
        "Others",
      ],
      FORESTRY: ["Leadership Award", "Outstanding Athlete", "Others"],
      COED: [
        "Best in Elocution Award",
        "Leadership Award",
        "Relentless Mentor of the Year Award",
        "Researcher of the Year",
        "Student Extensionista of the Year Award",
        "Others",
      ],
    };

    $("#program_select").on("change", function () {
      $("#award_select").val("None").trigger("change");
      var selectedProgram = $(this).val();
      var awardSelect = $("#award_select");
      awardSelect.empty(); // Clear existing options

      if (selectedProgram !== "None" && awards[selectedProgram]) {
        // Add the default 'None' option first
        awardSelect.append(new Option("----------", "None"));

        awards[selectedProgram].forEach(function (award) {
          awardSelect.append(new Option(award, award));
        });
        $("#award_select").trigger("change");
      } else {
        // Add the default 'None' option
        awardSelect.append(new Option("----------", "None"));
      }
    });

    $("#award_select").on("change", function () {
      $("#leadership_fields").addClass("hidden_fields");
      $("#capstone_fields").addClass("hidden_fields");
      $("#ojt_fields").addClass("hidden_fields");
      $("#research_fields").addClass("hidden_fields");
      $("#Others").addClass("hidden_fields");
      switch ($(this).val()) {
        case "Leadership Award":
          console.log("Leadership");
          $("#leadership_fields").removeClass("hidden_fields");
          break;
        case "Best Capstone":
          console.log("Capstone");
          $("#capstone_fields").removeClass("hidden_fields");
          break;
        case "Best OJT Award":
          console.log("OJT");
          $("#ojt_fields").removeClass("hidden_fields");
          break;
        case "Researcher of the Year":
          console.log("Research");
          $("#research_fields").removeClass("hidden_fields");
          break;
        case "Others":
          console.log("Others");
          $("#Others").removeClass("hidden_fields");
          break;
      }
    });
  });

  // This ensures the dropdowns are set up correctly on page load.
  $("#program_select").val("None").trigger("change");
});

// The old 'assign_student' function and the
// 'assign_student_id' input listener have been completely removed.
