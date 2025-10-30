/* Image preview for Bank QR admin upload */
function loadImageBanks(event) {
  let img = document.getElementById("outputBanks");
  if (img) {
    img.src = URL.createObjectURL(event.target.files[0]);
  }
}

/* Generic image preview (used by GCash receipt) */
function loadImage(event) {
  let img = document.getElementById("output"); // Note: This ID might need to be more specific
  if (img) {
    img.src = URL.createObjectURL(event.target.files[0]);
  }
}

$(document).ready(function () {
  // --- Initialize Modal State ---
  // Start with mode1 (GCash) visible and others hidden
  $(".mode1, .mode2, .mode3").hide();
  $(".mode1").show();

  // --- Main Tab/Mode Switching ---
  $('input[name="mode"]').on("change", function () {
    $(".mode1, .mode2, .mode3").hide();
    $("." + $(this).val()).show();
  });

  // --- Popup Open/Close ---
  // Open popup
  $(".show-donate").on("click", function () {
    $(".donate-popup").css("display", "flex");
  });

  // Close popup via "X" or "Cancel" buttons
  $(".close, .closeBtn").on("click", function () {
    $(".donate-popup").hide();
  });

  // Close popup by clicking on the background overlay
  $(window).on("click", function (e) {
    if ($(e.target).hasClass("donate-popup")) {
      $(".donate-popup").hide();
    }
  });

  // --- Volunteer Form Logic ---
  $(".what_kind").on("change", function () {
    let val = $(this).val();
    // Hide all optional fields first
    $(
      ".recepient, .confirmation_label, .confirmation_photo, .date_sched, .volunteer_amount, .recepient_things"
    ).hide();

    // Show fields based on selection
    if (
      val === "RELIEF GOODS" ||
      val === "BELONGINGS" ||
      val === "EQUIPMENTS"
    ) {
      $(".confirmation_label, .confirmation_photo, .recepient_things").show();
    } else if (val === "MONEY") {
      $(
        ".recepient, .confirmation_label, .confirmation_photo, .volunteer_amount"
      ).show();
    } else if (val === "SERVICE") {
      $(".date_sched").show();
    }
  });
  // --- 11-Digit Tab-Key Validation ---

  function checkPhoneNumberOnTab(event) {
    // Check if the pressed key is 'Tab'
    if (event.key === "Tab" || event.keyCode === 9) {
      // Get the value from the input field that triggered the event
      const phoneNumber = $(this).val();

      // If the length is not 11 digits
      if (phoneNumber.length !== 11) {
        // Prevent the default "Tab" behavior (moving to the next input)
        event.preventDefault();

        // Alert the user
        alert("Please enter exactly 11 digits before proceeding.");
      }
    }
  }

  // Apply this validation logic to both phone number inputs
  $("#gcash_number").on("keydown", checkPhoneNumberOnTab);
  $("#contact_number").on("keydown", checkPhoneNumberOnTab);
  // --- GCash Form "Next" Button & Validation ---
  $(".nextGcash").on("click", function () {
    const gcashNumber = $("#gcash_number").val();

    // Validation Check
    if (gcashNumber.length !== 11) {
      alert("Please enter a valid 11-digit GCash number.");
      return; // Stop if invalid
    }

    // If valid, show next step
    $(".gcash-form").hide();
    $(".gcash-img").show();
  });

  // --- Bank Form "Next" Button ---
  // (Add validation here if needed)
  $(".nextBank").on("click", function () {
    // Add validation for bank_number here if you want

    // Show next step
    $(".bank-form").hide();
    $(".bank-img").show();
  });

  // --- Volunteer Form Submission Validation ---
  $(".mode3 form").on("submit", function (e) {
    const contactNumber = $("#contact_number").val();

    // Validation Check
    if (contactNumber.length !== 11) {
      alert("Please enter a valid 11-digit contact number.");
      e.preventDefault(); // This stops the form from submitting
    }
  });

  // --- Dynamic Bank QR Code (from your loop) ---
  // Note: This needs to be outside the document.ready if `qrCodeID` is rendered in the main template
  // If `donate.html` is included *inside* the loop, this is fine.
  // If not, you may need to move the `{% for qrcode ... %}` loop from the HTML
  // to be *inside* this script block.

  // Assuming the loop is in the HTML as you provided:
  // This will re-bind the change event for every QR code, which is inefficient
  // but matches your provided template structure.

  // A better way (if you have only one qrCodeID object):
  /*
  const qrCodeData = {
      BPI: "{{ qrCodeID.first.bpi.url }}",
      BDO: "{{ qrCodeID.first.bdo.url }}",
      LANDBANK: "{{ qrCodeID.first.landbank.url }}",
      // ... etc ...
  };
  
  $(".bank_card").on("change", function () {
    let bank_card = $(this).val();
    if (qrCodeData[bank_card]) {
      $("#qr_bank img").attr("src", qrCodeData[bank_card]);
    }
  });
  */
});
